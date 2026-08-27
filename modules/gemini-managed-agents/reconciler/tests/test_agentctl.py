from __future__ import annotations

import argparse
import contextlib
import copy
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "agentctl.py"
SPEC = importlib.util.spec_from_file_location("agentctl", SCRIPT)
assert SPEC and SPEC.loader
agentctl = importlib.util.module_from_spec(SPEC)
sys.modules["agentctl"] = agentctl
SPEC.loader.exec_module(agentctl)

FIXTURE = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "agents" / "test-worker"
COMPLETE = Path(__file__).resolve().parents[2] / "examples" / "complete" / "agents" / "research-assistant"


class FakeAgentsHandler(BaseHTTPRequestHandler):
    agents: dict[tuple[str, str], dict] = {}
    events: list[tuple[str, str, str]] = []
    reject_next_post: dict | None = None

    def log_message(self, *_args: object) -> None:
        return

    def response(self, status: int, body: dict | None = None) -> None:
        encoded = b"" if body is None else json.dumps(body).encode("utf-8")
        self.send_response(status)
        if encoded:
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        if encoded:
            self.wfile.write(encoded)

    def agent_id(self) -> str:
        return self.path.rsplit("/", 1)[-1]

    def project_id(self) -> str:
        return self.headers.get("x-goog-user-project", "api-key-project")

    def agent_key(self, agent_id: str | None = None) -> tuple[str, str]:
        return (self.project_id(), self.agent_id() if agent_id is None else agent_id)

    def client_is_identified(self) -> bool:
        return self.headers.get("x-goog-api-client") == agentctl.CLIENT_HEADER

    def do_GET(self) -> None:
        if not self.client_is_identified():
            self.response(400, {"error": {"status": "INVALID_ARGUMENT"}})
            return
        agent_id = self.agent_id()
        key = self.agent_key(agent_id)
        self.events.append(("GET", agent_id, key[0]))
        if key not in self.agents:
            self.response(404, {"message": "not found"})
            return
        payload = copy.deepcopy(self.agents[key])
        if payload.get("tools") == []:
            del payload["tools"]
        self.response(200, payload)

    def do_POST(self) -> None:
        if not self.client_is_identified():
            self.response(400, {"error": {"status": "INVALID_ARGUMENT"}})
            return
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        agent_id = payload["id"]
        key = self.agent_key(agent_id)
        self.events.append(("POST", agent_id, key[0]))
        if self.reject_next_post is not None:
            response = self.reject_next_post
            self.reject_next_post = None
            self.response(400, response)
            return
        for tool in payload.get("tools", []):
            if tool.get("type") != "mcp_server":
                continue
            allowed = tool.get("allowed_tools")
            valid = (
                isinstance(allowed, list)
                and len(allowed) == 1
                and isinstance(allowed[0], dict)
                and set(allowed[0]) == {"mode", "tools"}
                and allowed[0]["mode"] in {"auto", "any", "none", "validated"}
                and isinstance(allowed[0]["tools"], list)
                and all(isinstance(item, str) and item for item in allowed[0]["tools"])
            )
            if not valid:
                self.response(400, {"error": {"status": "INVALID_ARGUMENT", "message": "invalid allowed_tools"}})
                return
        if key in self.agents:
            self.response(409, {"message": "already exists"})
            return
        self.agents[key] = copy.deepcopy(payload)
        self.response(200, copy.deepcopy(payload))

    def do_DELETE(self) -> None:
        if not self.client_is_identified():
            self.response(400, {"error": {"status": "INVALID_ARGUMENT"}})
            return
        agent_id = self.agent_id()
        key = self.agent_key(agent_id)
        self.events.append(("DELETE", agent_id, key[0]))
        if key not in self.agents:
            self.response(404, {"message": "not found"})
            return
        del self.agents[key]
        self.response(204)


@contextlib.contextmanager
def fake_api():
    FakeAgentsHandler.agents = {}
    FakeAgentsHandler.events = []
    FakeAgentsHandler.reject_next_post = None
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeAgentsHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    environment = {
        "GEMINI_AGENTCTL_TEST_MODE": "1",
        "GEMINI_AGENTCTL_API_BASE": f"http://127.0.0.1:{server.server_port}/v1beta",
    }
    try:
        with patch.dict(os.environ, environment, clear=False):
            yield FakeAgentsHandler
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def reconcile_args(manifest: Path) -> argparse.Namespace:
    return argparse.Namespace(
        project_id="example-project-12345",
        manifest_path=str(manifest),
        revision_key="v1",
        authentication_mode="oauth",
        api_key_secret_manager_version="",
    )


class RenderTests(unittest.TestCase):
    def test_render_is_content_addressed_and_defaults_network_to_deny(self) -> None:
        rendered = agentctl.render_manifest(FIXTURE / "agent.json")
        revision = rendered.revisions["v1"]

        self.assertTrue(revision.agent_id.startswith("test-worker-"))
        self.assertEqual(revision.payload["base_environment"]["network"], "disabled")
        self.assertEqual(revision.payload["tools"], [])
        self.assertIn("typed worker", revision.payload["system_instruction"])
        self.assertEqual(len(revision.revision_digest), 64)

    def test_runtime_change_creates_a_new_immutable_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy_path = Path(directory) / "test-worker"
            shutil.copytree(FIXTURE, copy_path)
            before = agentctl.render_manifest(copy_path / "agent.json").revisions["v1"]
            agents_file = copy_path / "revisions" / "v1" / "runtime" / ".agents" / "AGENTS.md"
            agents_file.write_text(agents_file.read_text(encoding="utf-8") + "\nBe concise.\n", encoding="utf-8")
            after = agentctl.render_manifest(copy_path / "agent.json").revisions["v1"]

        self.assertNotEqual(before.revision_digest, after.revision_digest)
        self.assertNotEqual(before.agent_id, after.agent_id)

    def test_system_instruction_change_creates_a_new_immutable_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy_path = Path(directory) / "test-worker"
            shutil.copytree(FIXTURE, copy_path)
            before = agentctl.render_manifest(copy_path / "agent.json").revisions["v1"]
            instruction = copy_path / "revisions" / "v1" / "instructions" / "system.md"
            instruction.write_text("You are a changed typed worker.\n", encoding="utf-8")
            after = agentctl.render_manifest(copy_path / "agent.json").revisions["v1"]

        self.assertNotEqual(before.revision_digest, after.revision_digest)
        self.assertNotEqual(before.agent_id, after.agent_id)
        self.assertEqual(after.payload["system_instruction"], "You are a changed typed worker.\n")

    def test_mcp_subset_uses_current_agents_api_wire_shape(self) -> None:
        revision = agentctl.render_manifest(COMPLETE / "agent.json").revisions["v1"]
        mcp_tool = revision.payload["tools"][0]

        self.assertEqual(
            mcp_tool["allowed_tools"],
            [{"mode": "auto", "tools": ["read_publication", "search_publications"]}],
        )
        self.assertEqual(
            revision.summary["output_schema_path"],
            "revisions/v1/schemas/output.schema.json",
        )
        self.assertEqual(
            revision.summary["evaluation_case_paths"],
            ["revisions/v1/evaluations/cases.jsonl"],
        )

    def test_catch_all_network_rule_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy_path = Path(directory) / "test-worker"
            shutil.copytree(FIXTURE, copy_path)
            manifest_path = copy_path / "agent.json"
            document = json.loads(manifest_path.read_text(encoding="utf-8"))
            revision = document["spec"]["revisions"]["v1"]
            revision["network"] = {"mode": "allowlist", "allowlist": [{"domain": "*"}]}
            manifest_path.write_text(json.dumps(document), encoding="utf-8")

            with self.assertRaisesRegex(agentctl.ReconcilerError, "catch-all"):
                agentctl.render_manifest(manifest_path)

    def test_mcp_url_cannot_carry_a_query_secret(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy_path = Path(directory) / "test-worker"
            shutil.copytree(FIXTURE, copy_path)
            manifest_path = copy_path / "agent.json"
            document = json.loads(manifest_path.read_text(encoding="utf-8"))
            revision = document["spec"]["revisions"]["v1"]
            revision["network"] = {"mode": "allowlist", "allowlist": [{"domain": "api.example.com"}]}
            revision["mcp_servers"] = [
                {
                    "name": "catalog",
                    "url": "https://api.example.com/mcp?token=inline-value",
                    "allowed_tools": ["search"],
                }
            ]
            manifest_path.write_text(json.dumps(document), encoding="utf-8")

            with self.assertRaisesRegex(agentctl.ReconcilerError, "without credentials"):
                agentctl.render_manifest(manifest_path)

    def test_json_booleans_are_not_accepted_as_integers(self) -> None:
        for field, value in (("max_total_tokens", True), ("reconcile_generation", False)):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                copy_path = Path(directory) / "test-worker"
                shutil.copytree(FIXTURE, copy_path)
                manifest_path = copy_path / "agent.json"
                document = json.loads(manifest_path.read_text(encoding="utf-8"))
                revision = document["spec"]["revisions"]["v1"]
                if field == "reconcile_generation":
                    revision["lifecycle"][field] = value
                else:
                    revision[field] = value
                manifest_path.write_text(json.dumps(document), encoding="utf-8")

                with self.assertRaises(agentctl.ReconcilerError):
                    agentctl.render_manifest(manifest_path)


class LifecycleTests(unittest.TestCase):
    PROJECT = "example-project-12345"

    def key(self, agent_id: str, project_id: str | None = None) -> tuple[str, str]:
        return (project_id or self.PROJECT, agent_id)

    def test_required_google_client_header_is_sent(self) -> None:
        with patch.dict(os.environ, {"GEMINI_AGENTCTL_TEST_MODE": "1"}, clear=False):
            headers = agentctl.ApiClient(self.PROJECT, "oauth", "").headers()

        self.assertEqual(headers["x-goog-api-client"], agentctl.CLIENT_HEADER)

    def test_secret_header_drift_is_detected_without_exposing_the_value(self) -> None:
        manifest = COMPLETE / "agent.json"
        revision = agentctl.render_manifest(manifest).revisions["v1"]
        environment = {"GEMINI_AGENTCTL_TEST_SECRET_RESEARCH_CATALOG_TOKEN": "private-test-value"}
        with fake_api() as api, patch.dict(os.environ, environment, clear=False):
            args = reconcile_args(manifest)
            agentctl.reconcile(args)
            client = agentctl.ApiClient("example-project-12345", "oauth", "")
            self.assertEqual(agentctl.status_for(client, revision)["status"], "current")

            api.agents[self.key(revision.agent_id)]["tools"][0]["headers"]["Authorization"] = "Bearer altered"
            status = agentctl.status_for(client, revision)

        self.assertEqual(status["status"], "drifted")
        self.assertNotIn("private-test-value", json.dumps(status))
        self.assertNotIn("altered", json.dumps(status))

    def test_unexpected_tool_and_network_headers_are_redacted_drift(self) -> None:
        manifest = COMPLETE / "agent.json"
        revision = agentctl.render_manifest(manifest).revisions["v1"]
        environment = {"GEMINI_AGENTCTL_TEST_SECRET_RESEARCH_CATALOG_TOKEN": "private-test-value"}
        with fake_api() as api, patch.dict(os.environ, environment, clear=False):
            agentctl.reconcile(reconcile_args(manifest))
            client = agentctl.ApiClient(self.PROJECT, "oauth", "")
            remote = api.agents[self.key(revision.agent_id)]

            remote["tools"][0]["headers"]["X-Privileged"] = "tool-secret-value"
            tool_status = agentctl.status_for(client, revision)
            del remote["tools"][0]["headers"]["X-Privileged"]

            remote["base_environment"]["network"]["allowlist"][0]["transform"] = {
                "X-Privileged": "network-secret-value"
            }
            network_status = agentctl.status_for(client, revision)

        self.assertEqual(tool_status["status"], "drifted")
        self.assertEqual(network_status["status"], "drifted")
        serialized = json.dumps([tool_status, network_status])
        self.assertNotIn("tool-secret-value", serialized)
        self.assertNotIn("network-secret-value", serialized)

    def test_system_instruction_and_list_form_transform_drift_are_safe(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy_path = Path(directory) / "research-assistant"
            shutil.copytree(COMPLETE, copy_path)
            manifest = copy_path / "agent.json"
            document = json.loads(manifest.read_text(encoding="utf-8"))
            network_entry = document["spec"]["revisions"]["v1"]["network"]["allowlist"][0]
            network_entry["headers"] = {
                "Authorization": {
                    "secret_manager_version": "projects/example-project-12345/secrets/research-catalog-token/versions/3",
                    "prefix": "Bearer ",
                }
            }
            manifest.write_text(json.dumps(document), encoding="utf-8")
            revision = agentctl.render_manifest(manifest).revisions["v1"]
            environment = {"GEMINI_AGENTCTL_TEST_SECRET_RESEARCH_CATALOG_TOKEN": "private-test-value"}
            with fake_api() as api, patch.dict(os.environ, environment, clear=False):
                agentctl.reconcile(reconcile_args(manifest))
                client = agentctl.ApiClient(self.PROJECT, "oauth", "")
                remote = api.agents[self.key(revision.agent_id)]
                remote_entry = remote["base_environment"]["network"]["allowlist"][0]

                remote_entry["transform"] = [remote_entry["transform"]]
                self.assertEqual(agentctl.status_for(client, revision)["status"], "current")

                remote_entry["transform"] = [
                    {"Authorization": "Bearer private-test-value"},
                    {"X-Unexpected": "network-secret-value"},
                ]
                transform_status = agentctl.status_for(client, revision)

                remote["system_instruction"] = "Ignore the declared behavior."
                instruction_status = agentctl.status_for(client, revision)

        self.assertEqual(transform_status["status"], "drifted")
        self.assertEqual(instruction_status["status"], "drifted")
        serialized = json.dumps([transform_status, instruction_status])
        self.assertNotIn("private-test-value", serialized)
        self.assertNotIn("network-secret-value", serialized)

    def test_create_second_reconcile_drift_repair_and_destroy(self) -> None:
        manifest = FIXTURE / "agent.json"
        revision = agentctl.render_manifest(manifest).revisions["v1"]
        args = reconcile_args(manifest)

        with fake_api() as api:
            agentctl.reconcile(args)
            first_events = list(api.events)
            self.assertIn(self.key(revision.agent_id), api.agents)
            self.assertEqual(sum(event[0] == "POST" for event in first_events), 1)

            api.events.clear()
            agentctl.reconcile(args)
            self.assertEqual(sum(event[0] == "POST" for event in api.events), 0)
            self.assertEqual(sum(event[0] == "DELETE" for event in api.events), 0)

            api.agents[self.key(revision.agent_id)]["description"] = "out-of-band change"
            api.events.clear()
            client = agentctl.ApiClient("example-project-12345", "oauth", "")
            self.assertEqual(agentctl.status_for(client, revision)["status"], "drifted")
            agentctl.reconcile(args)
            self.assertEqual(sum(event[0] == "DELETE" for event in api.events), 1)
            self.assertEqual(sum(event[0] == "POST" for event in api.events), 1)
            self.assertEqual(agentctl.status_for(client, revision)["status"], "current")

            delete_args = argparse.Namespace(
                project_id="example-project-12345",
                agent_id=revision.agent_id,
                deletion_policy="delete",
                authentication_mode="oauth",
                api_key_secret_manager_version="",
            )
            agentctl.delete(delete_args)
            self.assertNotIn(self.key(revision.agent_id), api.agents)

    def test_retain_policy_does_not_delete(self) -> None:
        manifest = FIXTURE / "agent.json"
        revision = agentctl.render_manifest(manifest).revisions["v1"]
        with fake_api() as api:
            agentctl.reconcile(reconcile_args(manifest))
            delete_args = argparse.Namespace(
                project_id="example-project-12345",
                agent_id=revision.agent_id,
                deletion_policy="retain",
                authentication_mode="oauth",
                api_key_secret_manager_version="",
            )
            api.events.clear()
            agentctl.delete(delete_args)
            self.assertIn(self.key(revision.agent_id), api.agents)
            self.assertEqual(api.events, [])

    def test_api_error_diagnostic_never_echoes_runtime_secret(self) -> None:
        manifest = COMPLETE / "agent.json"
        environment = {"GEMINI_AGENTCTL_TEST_SECRET_RESEARCH_CATALOG_TOKEN": "private-test-value"}
        with fake_api() as api, patch.dict(os.environ, environment, clear=False):
            api.reject_next_post = {
                "error": {
                    "status": "INVALID_ARGUMENT",
                    "message": "bad header: Bearer private-test-value",
                }
            }
            with self.assertRaises(agentctl.ReconcilerError) as raised:
                agentctl.reconcile(reconcile_args(manifest))

        self.assertIn("INVALID_ARGUMENT", str(raised.exception))
        self.assertNotIn("private-test-value", str(raised.exception))

    @unittest.skipUnless(shutil.which("tofu"), "OpenTofu is required for the lifecycle contract test")
    def test_opentofu_apply_is_idempotent_and_destroy_cleans_up(self) -> None:
        module_dir = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            module_a = root / "module-a"
            shutil.copytree(
                module_dir,
                module_a,
                ignore=shutil.ignore_patterns(".terraform", ".terraform.lock.hcl", "__pycache__", "*.pyc"),
            )
            manifest_dir = root / "agent-`touch shell-owned`"
            shutil.copytree(FIXTURE, manifest_dir)
            manifest_path = manifest_dir / "agent.json"
            sentinel = root / "shell-owned"

            def write_configuration(source: Path, manifests: dict[str, Path]) -> None:
                entries = "\n".join(
                    f"    {key} = {json.dumps(str(path))}" for key, path in sorted(manifests.items())
                )
                configuration = f'''terraform {{
  required_version = ">= 1.8.0, < 2.0.0"
}}

variable "project_id" {{
  type    = string
  default = "example-project-12345"
}}

variable "authentication_mode" {{
  type    = string
  default = "oauth"
}}

variable "api_key_secret_manager_version" {{
  type    = string
  default = ""
}}

module "under_test" {{
  source = {json.dumps(str(source))}

  project_id = var.project_id
  authentication = {{
    mode                           = var.authentication_mode
    api_key_secret_manager_version = var.api_key_secret_manager_version == "" ? null : var.api_key_secret_manager_version
  }}
  manifest_paths = {{
{entries}
  }}
}}

output "drift_report" {{
  value = module.under_test.drift_report
}}
'''
                (root / "main.tf").write_text(configuration, encoding="utf-8")

            write_configuration(module_a, {"test_worker": manifest_path})

            with fake_api() as api:
                environment = dict(os.environ)
                environment["GEMINI_AGENTCTL_TEST_SECRET_AGENT_API_KEY_OLD"] = "old-test-key"
                environment["GEMINI_AGENTCTL_TEST_SECRET_AGENT_API_KEY_NEW"] = "new-test-key"

                def tofu(*arguments: str, expected: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess[str]:
                    result = subprocess.run(
                        ["tofu", *arguments],
                        cwd=root,
                        env=environment,
                        text=True,
                        capture_output=True,
                        timeout=180,
                    )
                    if result.returncode not in expected:
                        self.fail(f"tofu {' '.join(arguments)} failed\n{result.stdout}\n{result.stderr}")
                    return result

                tofu("init", "-backend=false", "-input=false")
                tofu("apply", "-auto-approve", "-input=false")
                self.assertEqual(len(api.agents), 1)
                self.assertFalse(sentinel.exists(), "caller-controlled manifest path executed in the shell")
                tofu("plan", "-detailed-exitcode", "-input=false")

                agent_id = next(iter(api.agents))[1]
                original_key = self.key(agent_id)

                api.events.clear()
                write_configuration(module_a, {"renamed_worker": manifest_path})
                tofu("apply", "-auto-approve", "-input=false")
                self.assertIn(original_key, api.agents)
                self.assertEqual(sum(event[0] in {"POST", "DELETE"} for event in api.events), 0)

                document = json.loads(manifest_path.read_text(encoding="utf-8"))
                document["spec"]["revisions"]["stable"] = document["spec"]["revisions"].pop("v1")
                document["spec"]["active_revision"] = "stable"
                manifest_path.write_text(json.dumps(document), encoding="utf-8")
                api.events.clear()
                tofu("apply", "-auto-approve", "-input=false")
                self.assertIn(original_key, api.agents)
                self.assertEqual(sum(event[0] in {"POST", "DELETE"} for event in api.events), 0)

                new_project = "example-project-67890"
                api.events.clear()
                tofu("apply", "-auto-approve", "-input=false", f"-var=project_id={new_project}")
                moved_key = self.key(agent_id, new_project)
                self.assertNotIn(original_key, api.agents)
                self.assertIn(moved_key, api.agents)
                self.assertIn(("DELETE", agent_id, self.PROJECT), api.events)
                self.assertIn(("POST", agent_id, new_project), api.events)

                api.agents[moved_key]["description"] = "out-of-band change"
                tofu(
                    "plan",
                    "-detailed-exitcode",
                    "-input=false",
                    f"-var=project_id={new_project}",
                    expected=(2,),
                )

                document = json.loads(manifest_path.read_text(encoding="utf-8"))
                document["spec"]["revisions"]["stable"]["lifecycle"]["reconcile_generation"] = 1
                manifest_path.write_text(json.dumps(document), encoding="utf-8")
                tofu("apply", "-auto-approve", "-input=false", f"-var=project_id={new_project}")
                tofu("plan", "-detailed-exitcode", "-input=false", f"-var=project_id={new_project}")

                old_key_reference = "projects/example-project-67890/secrets/agent-api-key-old/versions/1"
                api.events.clear()
                tofu(
                    "apply",
                    "-auto-approve",
                    "-input=false",
                    f"-var=project_id={new_project}",
                    "-var=authentication_mode=api_key_secret_manager",
                    f"-var=api_key_secret_manager_version={old_key_reference}",
                )
                api_key_identity = self.key(agent_id, "api-key-project")
                self.assertNotIn(moved_key, api.agents)
                self.assertIn(api_key_identity, api.agents)
                self.assertIn(("DELETE", agent_id, new_project), api.events)
                self.assertIn(("POST", agent_id, "api-key-project"), api.events)

                new_key_reference = "projects/example-project-67890/secrets/agent-api-key-new/versions/2"
                api.events.clear()
                tofu(
                    "apply",
                    "-auto-approve",
                    "-input=false",
                    f"-var=project_id={new_project}",
                    "-var=authentication_mode=api_key_secret_manager",
                    f"-var=api_key_secret_manager_version={new_key_reference}",
                )
                self.assertIn(api_key_identity, api.agents)
                self.assertEqual(sum(event[0] == "DELETE" for event in api.events), 1)
                self.assertEqual(sum(event[0] == "POST" for event in api.events), 1)

                module_b = root / "module-b"
                shutil.copytree(module_a, module_b)
                shutil.rmtree(module_a)
                write_configuration(module_b, {})
                tofu("init", "-backend=false", "-input=false", "-upgrade")
                tofu("apply", "-auto-approve", "-input=false", f"-var=project_id={new_project}")
                self.assertEqual(api.agents, {})
                tofu("destroy", "-auto-approve", "-input=false", f"-var=project_id={new_project}")

    @unittest.skipUnless(shutil.which("tofu"), "OpenTofu is required for the lifecycle contract test")
    def test_duplicate_remote_agent_ownership_fails_plan(self) -> None:
        module_dir = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            configuration = f'''terraform {{
  required_version = ">= 1.8.0, < 2.0.0"
}}

module "under_test" {{
  source = {json.dumps(str(module_dir))}

  project_id         = "example-project-12345"
  enable_remote_read = false
  manifest_paths = {{
    first  = {json.dumps(str(FIXTURE / "agent.json"))}
    second = {json.dumps(str(FIXTURE / "agent.json"))}
  }}
}}
'''
            (root / "main.tf").write_text(configuration, encoding="utf-8")
            subprocess.run(
                ["tofu", "init", "-backend=false", "-input=false"],
                cwd=root,
                check=True,
                text=True,
                capture_output=True,
                timeout=180,
            )
            result = subprocess.run(
                ["tofu", "plan", "-input=false"],
                cwd=root,
                text=True,
                capture_output=True,
                timeout=180,
            )

        self.assertNotEqual(result.returncode, 0)
        diagnostic = result.stdout + result.stderr
        self.assertIn("exactly one manifest/revision", diagnostic)
        self.assertIn("first/v1, second/v1", diagnostic)


if __name__ == "__main__":
    unittest.main()
