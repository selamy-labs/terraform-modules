# Changelog

All notable changes to this repository are documented here. Versions follow
[semantic versioning](https://semver.org/) and are git tags (`vX.Y.Z`); import a
module pinned to a tag with `?ref=vX.Y.Z`. Entries are derived from the merged
history at each tag.

## [v0.9.0] - 2026-08-27

### Added
- Immutable Gemini Developer API managed-agent module with normalized directory
  manifests, typed active-revision outputs, runtime-only secret resolution,
  drift reporting, reconciliation, lifecycle contract tests, and generic
  examples.

## [v0.8.0] - 2026-06-21

### Changed
- Extend monitoring policy conditions (#21).

## [v0.7.0] - 2026-06-19

### Changed
- Extend GSM secret IAM migration support (#20).

## [v0.6.0] - 2026-06-18

### Added
- Provider-portable runner-cluster contract (#15).

## [v0.5.0] - 2026-06-18

### Added
- Canonical agent module (#14).

### Changed
- Unify the `selamy-skills` plugin pin to v0.34.0 (#13).

## [v0.4.0] - 2026-06-17

### Added
- MIT LICENSE (#10).
- Canonical-ingest-by-default bootstrap guide; list the arc module (#8).

### Changed
- Declare the `selamy-skills` plugin pinned to v0.27.3 (#9).
- Move the `arc-runner-scale-set` module to the public `speedforge/terraform-modules` (#11).

## [v0.3.0] - 2026-06-17

### Added
- `arc-runner-scale-set` module (#7).

## [v0.2.0] - 2026-06-17

### Changed
- Widen the google provider constraint to `>= 5.0, < 7.0` for 6.x adoption (#6).

## [v0.1.0] - 2026-06-17

### Added
- Initial reusable OpenTofu modules (#1).

### Changed
- Pin module sources with `?ref=` and add a `tofu fmt` CI gate (#5).
- Harden CI: trivy scanning and regenerated terraform-docs READMEs (#2, #3, #4).
