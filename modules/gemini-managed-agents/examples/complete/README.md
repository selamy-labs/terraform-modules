# Complete example

This example shows a directory-defined agent with a skill, workspace source,
typed output, evaluation cases, a tool-scoped remote MCP server, and a default
deny network allowlist.

The header credential is an immutable Secret Manager version reference. The
reconciler resolves its value only while calling the API; the value never enters
the module input, output, or state.
