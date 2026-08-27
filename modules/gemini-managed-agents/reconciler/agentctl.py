#!/usr/bin/env python3
"""Mechanical CRUD and drift reconciler for Gemini Developer API managed agents."""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import math
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NoReturn


API_BASE = "https://generativelanguage.googleapis.com/v1beta"
API_VERSION = "agents.selamy.dev/v1alpha1"
CLIENT_HEADER = "selamy-labs-opentofu/0.9.0"
KIND = "ManagedAgent"
BASE_AGENT = "antigravity-preview-05-2026"
SUPPORTED_MODELS = {
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
}
BUILTIN_TOOLS = {"code_execution", "google_search", "url_context"}
SECRET_VERSION_RE = re.compile(r"^projects/[^/]+/secrets/[^/]+/versions/[0-9]+$")
NAME_RE = re.compile(r"^[a-z][a-z0-9-]{0,39}[a-z0-9]$")
REVISION_RE = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
MCP_NAME_RE = re.compile(r"^[a-z0-9_-]+$")
RESERVED_PREFIXES = (
    "antigravity-",
    "veo-",
    "omni-",
    "lyria-",
    "imagen-",
    "gemma-",
    "gemini-",
    "google-",
    "youtube-",
    "android-",
    "chrome-",
    "pixel-",
    "waze-",
    "fitbit-",
    "nest-",
    "kaggle-",
)
MAX_INLINE_FILE_BYTES = 1_000_000
MAX_INLINE_TOTAL_BYTES = 2_000_000
OAUTH_SCOPES = (
    "https://www.googleapis.com/auth/cloud-platform,"
    "https://www.googleapis.com/auth/generative-language.retriever"
)


class ReconcilerError(RuntimeError):
    pass


@dataclass(frozen=True)
class RenderedRevision:
    key: str
    agent_id: str
    revision_digest: str
    remote_digest: str
    payload: dict[str, Any]
    summary: dict[str, Any]
    secret_references: tuple[str, ...]


@dataclass(frozen=True)
class RenderedManifest:
    active_revision: str
    labels: dict[str, str]
    annotations: dict[str, str]
    revisions: dict[str, RenderedRevision]


def fail(message: str) -> NoReturn:
    raise ReconcilerError(message)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def require_object(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{context} must be an object")
    return value


def require_string(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{context} must be a non-empty string")
    return value


def reject_unknown(value: dict[str, Any], allowed: set[str], context: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        fail(f"{context} has unknown fields: {', '.join(unknown)}")


def string_map(value: Any, context: str) -> dict[str, str]:
    if value is None:
        return {}
    obj = require_object(value, context)
    result: dict[str, str] = {}
    for key, item in obj.items():
        if not isinstance(key, str) or not isinstance(item, str):
            fail(f"{context} must contain string keys and values")
        result[key] = item
    return dict(sorted(result.items()))


def non_negative_integer(value: Any, context: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or value < 0
        or (isinstance(value, float) and (not math.isfinite(value) or not value.is_integer()))
    ):
        fail(f"{context} must be a non-negative integer")
    return int(value)


def resolve_inside(base: Path, relative: str, context: str) -> Path:
    candidate = (base / require_string(relative, context)).resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError:
        fail(f"{context} must stay within {base}")
    return candidate


def read_json(path: Path, context: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"{context} does not exist: {path}")
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        fail(f"{context} is not valid UTF-8 JSON: {error}")


def read_text_source(path: Path, context: str) -> tuple[str, str]:
    if path.is_symlink():
        fail(f"{context} must not be a symbolic link: {path}")
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        fail(f"{context} does not exist: {path}")
    if not path.is_file():
        fail(f"{context} must be a file: {path}")
    if len(data) > MAX_INLINE_FILE_BYTES:
        fail(f"{context} exceeds {MAX_INLINE_FILE_BYTES} bytes: {path}")
    try:
        content = data.decode("utf-8")
    except UnicodeDecodeError:
        fail(f"{context} must be UTF-8 text: {path}")
    if not content.strip():
        fail(f"{context} must not be empty: {path}")
    return content, hashlib.sha256(data).hexdigest()


def file_record(path: Path, target: str) -> tuple[dict[str, Any], dict[str, str], int]:
    data = path.read_bytes()
    if len(data) > MAX_INLINE_FILE_BYTES:
        fail(f"inline source exceeds {MAX_INLINE_FILE_BYTES} bytes: {path}")
    digest = hashlib.sha256(data).hexdigest()
    try:
        content = data.decode("utf-8")
        source = {"type": "inline", "target": target, "content": content}
    except UnicodeDecodeError:
        if path.suffix.lower() not in {".gif", ".jpeg", ".jpg", ".png", ".webp"}:
            fail(f"runtime sources must be UTF-8 text or a supported image: {path}")
        source = {
            "type": "inline",
            "target": target,
            "content": base64.b64encode(data).decode("ascii"),
            "encoding": "base64",
        }
    return source, {"target": target, "sha256": digest}, len(data)


def runtime_sources(revision_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    runtime_dir = revision_dir / "runtime"
    agents_file = runtime_dir / ".agents" / "AGENTS.md"
    if not agents_file.is_file():
        fail(f"revision runtime must contain .agents/AGENTS.md: {revision_dir}")

    sources: list[dict[str, Any]] = []
    digests: list[dict[str, str]] = []
    total_bytes = 0
    for item in runtime_dir.rglob("*"):
        if item.is_symlink():
            fail(f"runtime sources must not contain symbolic links: {item}")
    for path in sorted(item for item in runtime_dir.rglob("*") if item.is_file()):
        target = path.relative_to(runtime_dir).as_posix()
        source, digest, size = file_record(path, target)
        sources.append(source)
        digests.append(digest)
        total_bytes += size
    if total_bytes > MAX_INLINE_TOTAL_BYTES:
        fail(f"inline sources exceed {MAX_INLINE_TOTAL_BYTES} total bytes: {revision_dir}")
    return sources, digests


def secret_header_map(value: Any, context: str) -> tuple[dict[str, dict[str, str]], tuple[str, ...]]:
    if value is None:
        return {}, ()
    obj = require_object(value, context)
    result: dict[str, dict[str, str]] = {}
    references: list[str] = []
    for header, config_value in sorted(obj.items()):
        header_context = f"{context}.{header}"
        if not isinstance(header, str) or not re.fullmatch(r"[A-Za-z0-9-]+", header):
            fail(f"{header_context} has an invalid HTTP header name")
        config = require_object(config_value, header_context)
        reject_unknown(config, {"secret_manager_version", "prefix"}, header_context)
        reference = require_string(config.get("secret_manager_version"), f"{header_context}.secret_manager_version")
        if not SECRET_VERSION_RE.fullmatch(reference):
            fail(f"{header_context}.secret_manager_version must be immutable and fully qualified")
        prefix = config.get("prefix", "")
        if not isinstance(prefix, str) or "\r" in prefix or "\n" in prefix:
            fail(f"{header_context}.prefix must be a single-line string")
        result[header] = {"secret_manager_version": reference, "prefix": prefix}
        references.append(reference)
    return result, tuple(references)


def normalize_network(value: Any, context: str) -> tuple[Any, Any, tuple[str, ...], set[str]]:
    if value is None:
        return "disabled", {"mode": "disabled"}, (), set()
    obj = require_object(value, context)
    reject_unknown(obj, {"mode", "allowlist"}, context)
    mode = obj.get("mode", "disabled")
    if mode == "disabled":
        if obj.get("allowlist") not in (None, []):
            fail(f"{context}.allowlist must be empty when mode is disabled")
        return "disabled", {"mode": "disabled"}, (), set()
    if mode != "allowlist":
        fail(f"{context}.mode must be disabled or allowlist")
    raw_allowlist = obj.get("allowlist")
    if not isinstance(raw_allowlist, list) or not raw_allowlist:
        fail(f"{context}.allowlist must be a non-empty list")

    payload_entries: list[dict[str, Any]] = []
    portable_entries: list[dict[str, Any]] = []
    references: list[str] = []
    domains: set[str] = set()
    for index, item in enumerate(raw_allowlist):
        item_context = f"{context}.allowlist[{index}]"
        entry = require_object(item, item_context)
        reject_unknown(entry, {"domain", "headers"}, item_context)
        domain = require_string(entry.get("domain"), f"{item_context}.domain").lower()
        if domain == "*":
            fail(f"{item_context}.domain cannot be a catch-all wildcard")
        if not re.fullmatch(r"(?:\*\.)?[a-z0-9.-]+", domain):
            fail(f"{item_context}.domain is invalid")
        headers, header_references = secret_header_map(entry.get("headers"), f"{item_context}.headers")
        payload_entry: dict[str, Any] = {"domain": domain}
        portable_entry: dict[str, Any] = {"domain": domain}
        if headers:
            payload_entry["transform"] = headers
            portable_entry["headers"] = headers
        payload_entries.append(payload_entry)
        portable_entries.append(portable_entry)
        references.extend(header_references)
        domains.add(domain)
    return (
        {"allowlist": payload_entries},
        {"mode": "allowlist", "allowlist": portable_entries},
        tuple(references),
        domains,
    )


def normalize_tools(
    builtins_value: Any,
    mcp_value: Any,
    context: str,
    allowed_domains: set[str],
) -> tuple[list[dict[str, Any]], Any, tuple[str, ...]]:
    builtins = [] if builtins_value is None else builtins_value
    if not isinstance(builtins, list) or any(item not in BUILTIN_TOOLS for item in builtins):
        fail(f"{context}.builtin_tools must contain only {sorted(BUILTIN_TOOLS)}")
    if len(set(builtins)) != len(builtins):
        fail(f"{context}.builtin_tools must not contain duplicates")
    tools: list[dict[str, Any]] = [{"type": item} for item in sorted(builtins)]
    portable_mcp: list[dict[str, Any]] = []
    references: list[str] = []
    mcp_servers = [] if mcp_value is None else mcp_value
    if not isinstance(mcp_servers, list):
        fail(f"{context}.mcp_servers must be a list")
    names: set[str] = set()
    for index, item in enumerate(mcp_servers):
        item_context = f"{context}.mcp_servers[{index}]"
        server = require_object(item, item_context)
        reject_unknown(server, {"name", "url", "allowed_tools", "headers"}, item_context)
        name = require_string(server.get("name"), f"{item_context}.name")
        if not MCP_NAME_RE.fullmatch(name):
            fail(f"{item_context}.name must match ^[a-z0-9_-]+$")
        if name in names:
            fail(f"duplicate MCP server name: {name}")
        names.add(name)
        url = require_string(server.get("url"), f"{item_context}.url")
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.fragment or parsed.query:
            fail(f"{item_context}.url must be an HTTPS endpoint without credentials, query parameters, or fragments")
        host = parsed.hostname.lower()
        if host not in allowed_domains and not any(domain.startswith("*.") and host.endswith(domain[1:]) for domain in allowed_domains):
            fail(f"{item_context}.url host must be present in the network allowlist")
        allowed_tools = server.get("allowed_tools")
        if not isinstance(allowed_tools, list) or not allowed_tools or any(not isinstance(tool, str) or not tool for tool in allowed_tools):
            fail(f"{item_context}.allowed_tools must be a non-empty list")
        if len(set(allowed_tools)) != len(allowed_tools):
            fail(f"{item_context}.allowed_tools must not contain duplicates")
        headers, header_references = secret_header_map(server.get("headers"), f"{item_context}.headers")
        tool: dict[str, Any] = {
            "type": "mcp_server",
            "name": name,
            "url": url,
            # The current Agents REST OpenAPI wraps the tool-name subset in an
            # AllowedTools policy object. Some prose examples still show the
            # older flat list, so keep the portable manifest simple but emit
            # the API contract's typed wire shape here.
            "allowed_tools": [
                {
                    "mode": "auto",
                    "tools": sorted(allowed_tools),
                }
            ],
        }
        portable = {
            "type": "mcp_server",
            "name": name,
            "url": url,
            "allowed_tools": sorted(allowed_tools),
        }
        if headers:
            tool["headers"] = headers
            portable["headers"] = headers
        tools.append(tool)
        portable_mcp.append(portable)
        references.extend(header_references)
    portable = {"builtin_tools": sorted(builtins), "mcp_servers": portable_mcp}
    return tools, portable, tuple(references)


def render_manifest(manifest_path: Path) -> RenderedManifest:
    manifest_path = manifest_path.resolve()
    document = require_object(read_json(manifest_path, "manifest"), "manifest")
    reject_unknown(document, {"api_version", "kind", "metadata", "spec"}, "manifest")
    if document.get("api_version") != API_VERSION:
        fail(f"manifest.api_version must be {API_VERSION}")
    if document.get("kind") != KIND:
        fail(f"manifest.kind must be {KIND}")

    metadata = require_object(document.get("metadata"), "manifest.metadata")
    reject_unknown(metadata, {"name", "labels", "annotations"}, "manifest.metadata")
    name = require_string(metadata.get("name"), "manifest.metadata.name")
    if not NAME_RE.fullmatch(name) or name.lower().startswith(RESERVED_PREFIXES):
        fail("manifest.metadata.name must be a short lowercase slug without a Google-reserved prefix")
    labels = string_map(metadata.get("labels"), "manifest.metadata.labels")
    annotations = string_map(metadata.get("annotations"), "manifest.metadata.annotations")

    spec = require_object(document.get("spec"), "manifest.spec")
    reject_unknown(spec, {"backend", "active_revision", "revisions"}, "manifest.spec")
    if spec.get("backend") != "gemini_developer_api":
        fail("manifest.spec.backend must be gemini_developer_api")
    active_revision = require_string(spec.get("active_revision"), "manifest.spec.active_revision")
    revisions_value = require_object(spec.get("revisions"), "manifest.spec.revisions")
    if not revisions_value:
        fail("manifest.spec.revisions must not be empty")
    if active_revision not in revisions_value:
        fail("manifest.spec.active_revision must name a declared revision")

    rendered: dict[str, RenderedRevision] = {}
    for revision_key, revision_value in sorted(revisions_value.items()):
        if not REVISION_RE.fullmatch(revision_key):
            fail(f"invalid revision key: {revision_key}")
        context = f"manifest.spec.revisions.{revision_key}"
        revision = require_object(revision_value, context)
        reject_unknown(
            revision,
            {
                "directory",
                "description",
                "system_instruction",
                "base_agent",
                "model",
                "max_total_tokens",
                "builtin_tools",
                "mcp_servers",
                "network",
                "output_schema",
                "evaluation_cases",
                "lifecycle",
            },
            context,
        )
        revision_dir = resolve_inside(manifest_path.parent, revision.get("directory"), f"{context}.directory")
        if not revision_dir.is_dir():
            fail(f"{context}.directory does not exist: {revision_dir}")
        description = require_string(revision.get("description"), f"{context}.description")
        system_instruction_relative = require_string(
            revision.get("system_instruction"),
            f"{context}.system_instruction",
        )
        system_instruction_path = resolve_inside(
            revision_dir,
            system_instruction_relative,
            f"{context}.system_instruction",
        )
        system_instruction, system_instruction_digest = read_text_source(
            system_instruction_path,
            f"{context}.system_instruction",
        )
        base_agent = revision.get("base_agent", BASE_AGENT)
        if base_agent != BASE_AGENT:
            fail(f"{context}.base_agent must be {BASE_AGENT}")
        model = revision.get("model", "gemini-3.7-flash")
        if model not in SUPPORTED_MODELS:
            fail(f"{context}.model must be one of {sorted(SUPPORTED_MODELS)}")
        max_total_tokens = revision.get("max_total_tokens")
        if type(max_total_tokens) is not int or max_total_tokens < 1:
            fail(f"{context}.max_total_tokens must be a positive integer")

        network_payload, network_portable, network_refs, allowed_domains = normalize_network(revision.get("network"), f"{context}.network")
        tools_payload, tools_portable, tool_refs = normalize_tools(
            revision.get("builtin_tools"),
            revision.get("mcp_servers"),
            context,
            allowed_domains,
        )
        inline_payload, inline_digests = runtime_sources(revision_dir)

        output_schema_relative = require_string(revision.get("output_schema"), f"{context}.output_schema")
        output_schema_path = resolve_inside(revision_dir, output_schema_relative, f"{context}.output_schema")
        schema = require_object(read_json(output_schema_path, f"{context}.output_schema"), f"{context}.output_schema")
        output_schema_digest = digest_json(schema)
        evaluation_cases_value = revision.get("evaluation_cases", [])
        if not isinstance(evaluation_cases_value, list) or any(not isinstance(item, str) or not item for item in evaluation_cases_value):
            fail(f"{context}.evaluation_cases must be a list of paths")
        evaluation_paths: list[str] = []
        evaluation_digests: list[dict[str, str]] = []
        for index, relative in enumerate(evaluation_cases_value):
            path = resolve_inside(revision_dir, relative, f"{context}.evaluation_cases[{index}]")
            if not path.is_file():
                fail(f"evaluation case file does not exist: {path}")
            evaluation_paths.append(str(path))
            evaluation_digests.append({"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})

        lifecycle = revision.get("lifecycle", {})
        lifecycle = require_object(lifecycle, f"{context}.lifecycle")
        reject_unknown(lifecycle, {"deletion_policy", "reconcile_generation"}, f"{context}.lifecycle")
        deletion_policy = lifecycle.get("deletion_policy", "delete")
        if deletion_policy not in {"delete", "retain"}:
            fail(f"{context}.lifecycle.deletion_policy must be delete or retain")
        reconcile_generation = non_negative_integer(
            lifecycle.get("reconcile_generation", 0),
            f"{context}.lifecycle.reconcile_generation",
        )

        portable = {
            "api_version": API_VERSION,
            "backend": "gemini_developer_api",
            "name": name,
            "labels": labels,
            "annotations": annotations,
            "description": description,
            "system_instruction": {
                "path": system_instruction_relative,
                "sha256": system_instruction_digest,
            },
            "base_agent": base_agent,
            "model": model,
            "max_total_tokens": max_total_tokens,
            "tools": tools_portable,
            "network": network_portable,
            "inline_sources": inline_digests,
            "output_schema": {"path": output_schema_relative, "sha256": output_schema_digest},
            "evaluation_cases": evaluation_digests,
        }
        revision_digest = digest_json(portable)
        agent_id = f"{name}-{revision_digest[:16]}"
        description_with_digest = f"{description} [revision sha256:{revision_digest}]"
        payload = {
            "id": agent_id,
            "description": description_with_digest,
            "system_instruction": system_instruction,
            "base_agent": base_agent,
            "agent_config": {
                "type": "antigravity",
                "model": model,
                "max_total_tokens": str(max_total_tokens),
            },
            "tools": tools_payload,
            "base_environment": {
                "type": "remote",
                "sources": inline_payload,
                "network": network_payload,
            },
        }
        secret_references = tuple(sorted(set(network_refs + tool_refs)))
        remote_digest = digest_json(scrub_secrets(payload))
        summary = {
            "agent_id": agent_id,
            "revision_digest": revision_digest,
            "remote_digest": remote_digest,
            "model": model,
            "output_schema_path": output_schema_path.relative_to(manifest_path.parent).as_posix(),
            "output_schema_digest": output_schema_digest,
            "evaluation_case_paths": [
                Path(path).relative_to(manifest_path.parent).as_posix() for path in evaluation_paths
            ],
            "deletion_policy": deletion_policy,
            "reconcile_generation": reconcile_generation,
        }
        rendered[revision_key] = RenderedRevision(
            key=revision_key,
            agent_id=agent_id,
            revision_digest=revision_digest,
            remote_digest=remote_digest,
            payload=payload,
            summary=summary,
            secret_references=secret_references,
        )
    return RenderedManifest(active_revision, labels, annotations, rendered)


def scrub_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        if "secret_manager_version" in value and set(value) <= {"secret_manager_version", "prefix"}:
            return {
                "secret_manager_version": value["secret_manager_version"],
                "prefix": value.get("prefix", ""),
            }
        return {key: scrub_secrets(item) for key, item in sorted(value.items())}
    if isinstance(value, list):
        return [scrub_secrets(item) for item in value]
    return value


def redacted_actual(actual: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    fields = {
        key: ([] if key == "tools" and key not in actual else actual.get(key))
        for key in expected
    }
    expected_tools = expected.get("tools", [])
    actual_tools = fields.get("tools") or []
    for index, expected_tool in enumerate(expected_tools):
        if index >= len(actual_tools):
            continue
        actual_headers = actual_tools[index].get("headers", {})
        expected_headers = expected_tool.get("headers", {})
        if actual_headers or expected_headers:
            actual_tools[index]["headers"] = {
                header: (
                    secret_comparison_marker(value, expected_headers[header])
                    if header in expected_headers
                    else {"unexpected_header": True}
                )
                for header, value in actual_headers.items()
            }
    expected_network = expected.get("base_environment", {}).get("network")
    actual_environment = fields.get("base_environment") or {}
    actual_network = actual_environment.get("network")
    if isinstance(expected_network, dict) and isinstance(actual_network, dict):
        expected_allowlist = expected_network.get("allowlist", [])
        actual_allowlist = actual_network.get("allowlist", [])
        for index, expected_entry in enumerate(expected_allowlist):
            if index >= len(actual_allowlist):
                continue
            actual_transform = actual_allowlist[index].get("transform", {})
            expected_transform = expected_entry.get("transform", {})
            if actual_transform or expected_transform:
                actual_allowlist[index]["transform"] = redacted_transform(
                    actual_transform,
                    expected_transform,
                )
    return fields


def redacted_transform(actual: Any, expected: Any) -> dict[str, Any]:
    if not isinstance(expected, dict):
        return {"unexpected_transform": True}
    if isinstance(actual, list):
        if len(actual) != 1 or not isinstance(actual[0], dict):
            return {"unexpected_transform": True}
        actual = actual[0]
    if not isinstance(actual, dict):
        return {"unexpected_transform": True}
    return {
        header: (
            secret_comparison_marker(value, expected[header])
            if header in expected
            else {"unexpected_header": True}
        )
        for header, value in actual.items()
    }


def secret_comparison_marker(actual_value: Any, expected_config: dict[str, str]) -> dict[str, Any]:
    expected_value = materialize_secrets(expected_config)
    if isinstance(actual_value, str) and isinstance(expected_value, str) and hmac.compare_digest(actual_value, expected_value):
        return expected_config
    return {"secret_mismatch": True}


def production_api_base() -> str:
    override = os.environ.get("GEMINI_AGENTCTL_API_BASE")
    if not override:
        return API_BASE
    if os.environ.get("GEMINI_AGENTCTL_TEST_MODE") != "1":
        fail("GEMINI_AGENTCTL_API_BASE is allowed only in explicit test mode")
    return override.rstrip("/")


def command_output(command: list[str]) -> str | None:
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True, timeout=30)
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    value = result.stdout.strip()
    return value or None


def oauth_token() -> str:
    if os.environ.get("GEMINI_AGENTCTL_TEST_MODE") == "1":
        return os.environ.get("GEMINI_AGENTCTL_TEST_TOKEN", "test-token")
    explicit = os.environ.get("GOOGLE_OAUTH_ACCESS_TOKEN")
    if explicit:
        return explicit
    metadata_request = urllib.request.Request(
        "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
        headers={"Metadata-Flavor": "Google"},
    )
    try:
        with urllib.request.urlopen(metadata_request, timeout=2) as response:
            token = json.loads(response.read().decode("utf-8")).get("access_token")
            if token:
                return token
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        pass
    for command in (
        ["gcloud", "auth", "application-default", "print-access-token", f"--scopes={OAUTH_SCOPES}"],
        ["gcloud", "auth", "print-access-token", f"--scopes={OAUTH_SCOPES}"],
    ):
        token = command_output(command)
        if token:
            return token
    fail("unable to obtain OAuth access token from the environment, metadata server, or gcloud ADC")


def parse_secret_reference(reference: str) -> tuple[str, str, str]:
    if not SECRET_VERSION_RE.fullmatch(reference):
        fail(f"invalid immutable Secret Manager version: {reference}")
    parts = reference.split("/")
    return parts[1], parts[3], parts[5]


def access_secret(reference: str) -> str:
    project, secret, version = parse_secret_reference(reference)
    if os.environ.get("GEMINI_AGENTCTL_TEST_MODE") == "1":
        test_value = os.environ.get(f"GEMINI_AGENTCTL_TEST_SECRET_{secret.upper().replace('-', '_')}")
        if test_value is None:
            fail(f"test secret value is not configured for {secret}")
        return test_value
    token = oauth_token()
    url = (
        "https://secretmanager.googleapis.com/v1/"
        f"projects/{urllib.parse.quote(project, safe='')}/secrets/{urllib.parse.quote(secret, safe='')}/"
        f"versions/{urllib.parse.quote(version, safe='')}:access"
    )
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
        encoded = body["payload"]["data"]
        return base64.b64decode(encoded).decode("utf-8")
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError, urllib.error.URLError) as error:
        fallback = command_output(
            [
                "gcloud",
                "secrets",
                "versions",
                "access",
                version,
                f"--secret={secret}",
                f"--project={project}",
            ]
        )
        if fallback is not None:
            return fallback
        fail(f"unable to access Secret Manager version {reference}: {error}")


def materialize_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        if "secret_manager_version" in value and set(value) <= {"secret_manager_version", "prefix"}:
            return f"{value.get('prefix', '')}{access_secret(value['secret_manager_version'])}"
        return {key: materialize_secrets(item) for key, item in value.items()}
    if isinstance(value, list):
        return [materialize_secrets(item) for item in value]
    return value


def error_code(body: bytes) -> str:
    try:
        decoded = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "UNPARSEABLE_RESPONSE"
    objects: list[dict[str, Any]] = []
    if isinstance(decoded, dict):
        objects.append(decoded.get("error", decoded))
    elif isinstance(decoded, list):
        objects.extend(item for item in decoded if isinstance(item, dict))
    statuses = [item.get("status") for item in objects]
    safe_statuses = [status for status in statuses if isinstance(status, str) and re.fullmatch(r"[A-Z][A-Z0-9_]*", status)]
    return safe_statuses[0] if safe_statuses else "REQUEST_REJECTED"


class ApiClient:
    def __init__(self, project_id: str, authentication_mode: str, api_key_reference: str):
        self.project_id = project_id
        self.authentication_mode = authentication_mode
        self.api_key_reference = api_key_reference
        if authentication_mode not in {"oauth", "api_key_secret_manager"}:
            fail("authentication mode must be oauth or api_key_secret_manager")
        if authentication_mode == "api_key_secret_manager" and not SECRET_VERSION_RE.fullmatch(api_key_reference):
            fail("API key mode requires an immutable Secret Manager version")

    def headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-client": CLIENT_HEADER,
        }
        if self.authentication_mode == "oauth":
            headers["Authorization"] = f"Bearer {oauth_token()}"
            headers["x-goog-user-project"] = self.project_id
        else:
            headers["x-goog-api-key"] = access_secret(self.api_key_reference)
        return headers

    def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> tuple[int, Any | None]:
        data = None if body is None else canonical_json(body).encode("utf-8")
        request = urllib.request.Request(
            f"{production_api_base()}/{path.lstrip('/')}",
            data=data,
            method=method,
            headers=self.headers(),
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = response.read()
                return response.status, json.loads(payload.decode("utf-8")) if payload else None
        except urllib.error.HTTPError as error:
            payload = error.read()
            if error.code in {404, 409}:
                return error.code, None
            # Service messages are intentionally not surfaced: validation
            # responses may echo request fields after runtime-only secrets have
            # been materialized. A stable status code is actionable without
            # risking credentials in stderr or CI logs.
            fail(f"Gemini Agents API HTTP {error.code}: {error_code(payload)}")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            fail(f"Gemini Agents API request failed: {error}")

    def get(self, agent_id: str) -> dict[str, Any] | None:
        status, body = self.request("GET", f"agents/{urllib.parse.quote(agent_id, safe='')}")
        if status == 404:
            return None
        return require_object(body, "GetAgent response")

    def create(self, payload: dict[str, Any]) -> None:
        status, _ = self.request("POST", "agents", materialize_secrets(payload))
        if status not in {200, 201, 409}:
            fail(f"unexpected CreateAgent status: {status}")

    def delete(self, agent_id: str) -> None:
        self.request("DELETE", f"agents/{urllib.parse.quote(agent_id, safe='')}")


def status_for(client: ApiClient, revision: RenderedRevision) -> dict[str, str]:
    actual = client.get(revision.agent_id)
    if actual is None:
        return {
            "status": "missing",
            "agent_id": revision.agent_id,
            "expected_digest": revision.remote_digest,
            "observed_digest": "",
        }
    observed_digest = digest_json(scrub_secrets(redacted_actual(actual, revision.payload)))
    return {
        "status": "current" if observed_digest == revision.remote_digest else "drifted",
        "agent_id": revision.agent_id,
        "expected_digest": revision.remote_digest,
        "observed_digest": observed_digest,
    }


def selected_revision(manifest_path: str, revision_key: str) -> RenderedRevision:
    manifest = render_manifest(Path(manifest_path))
    if revision_key not in manifest.revisions:
        fail(f"revision is not declared: {revision_key}")
    return manifest.revisions[revision_key]


def external_render(query: dict[str, Any]) -> dict[str, str]:
    manifest_path = require_string(query.get("manifest_path"), "query.manifest_path")
    manifest = render_manifest(Path(manifest_path))
    summary = {
        "active_revision": manifest.active_revision,
        "labels": manifest.labels,
        "annotations": manifest.annotations,
        "revisions": {key: revision.summary for key, revision in manifest.revisions.items()},
    }
    return {"manifest_json": canonical_json(summary)}


def external_read(query: dict[str, Any]) -> dict[str, str]:
    project_id = require_string(query.get("project_id"), "query.project_id")
    manifest_path = require_string(query.get("manifest_path"), "query.manifest_path")
    revision_key = require_string(query.get("revision_key"), "query.revision_key")
    authentication_mode = require_string(query.get("authentication_mode"), "query.authentication_mode")
    api_key_reference = query.get("api_key_secret_manager_version", "")
    if not isinstance(api_key_reference, str):
        fail("query.api_key_secret_manager_version must be a string")
    revision = selected_revision(manifest_path, revision_key)
    return status_for(ApiClient(project_id, authentication_mode, api_key_reference), revision)


def reconcile(args: argparse.Namespace) -> None:
    revision = selected_revision(args.manifest_path, args.revision_key)
    client = ApiClient(args.project_id, args.authentication_mode, args.api_key_secret_manager_version)
    status = status_for(client, revision)
    if status["status"] == "current":
        action = "unchanged"
    else:
        if status["status"] == "drifted":
            client.delete(revision.agent_id)
        client.create(revision.payload)
        verified = status_for(client, revision)
        if verified["status"] != "current":
            fail(f"post-reconcile verification failed for {revision.agent_id}")
        action = "created" if status["status"] == "missing" else "replaced"
    print(canonical_json({"action": action, "agent_id": revision.agent_id, "revision_digest": revision.revision_digest}))


def delete(args: argparse.Namespace) -> None:
    if args.deletion_policy == "retain":
        print(canonical_json({"action": "retained", "agent_id": args.agent_id}))
        return
    client = ApiClient(args.project_id, args.authentication_mode, args.api_key_secret_manager_version)
    if client.get(args.agent_id) is None:
        action = "absent"
    else:
        client.delete(args.agent_id)
        if client.get(args.agent_id) is not None:
            fail(f"post-delete verification failed for {args.agent_id}")
        action = "deleted"
    print(canonical_json({"action": action, "agent_id": args.agent_id}))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    subparsers = result.add_subparsers(dest="command", required=True)
    subparsers.add_parser("render")
    subparsers.add_parser("read")

    reconcile_parser = subparsers.add_parser("reconcile")
    reconcile_parser.add_argument("--project-id", required=True)
    reconcile_parser.add_argument("--manifest-path", required=True)
    reconcile_parser.add_argument("--revision-key", required=True)
    reconcile_parser.add_argument("--authentication-mode", required=True)
    reconcile_parser.add_argument("--api-key-secret-manager-version", default="")

    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("--project-id", required=True)
    delete_parser.add_argument("--agent-id", required=True)
    delete_parser.add_argument("--deletion-policy", choices=("delete", "retain"), required=True)
    delete_parser.add_argument("--authentication-mode", required=True)
    delete_parser.add_argument("--api-key-secret-manager-version", default="")
    return result


def main() -> int:
    try:
        args = parser().parse_args()
        if args.command in {"render", "read"}:
            query = json.load(sys.stdin)
            output = external_render(query) if args.command == "render" else external_read(query)
            print(canonical_json(output))
        elif args.command == "reconcile":
            reconcile(args)
        else:
            delete(args)
        return 0
    except (ReconcilerError, json.JSONDecodeError) as error:
        print(f"agentctl: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
