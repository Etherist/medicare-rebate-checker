# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-26

### Added
- Initial production-ready release
- Four autonomous agents: MBSDataFetcher, EligibilityValidator, RebateCalculator, ReportGenerator
- Three user interfaces: CLI, FastAPI REST API, Streamlit web app
- 20+ MBS items with complete rule sets
- Comprehensive test suite (47 tests, 85%+ coverage)
- CI/CD pipelines (GitHub Actions)
- Documentation site (MkDocs Material)
- Security hardening (input validation, rate limiting, no PII storage)
- Docker and Kubernetes deployment configurations

### Changed
- N/A (initial release)

### Deprecated
- N/A (initial release)

### Removed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- No known security issues at release

## [Unreleased]

### Added
- Placeholder for upcoming features

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

---

## Versioning Philosophy

- **Major** (`X.0.0`): Breaking changes, architecture shifts, agent API changes
- **Minor** (`0.X.0`): New agents, new MBS categories, new interfaces
- **Patch** (`0.0.X`): Bug fixes, performance improvements, documentation updates

## Migration Guides

### Migrating from 0.x to 1.0.0
- Update agent method signatures (now use dict-based patient objects)
- Reports now include eligibility reasons structured data
- CLI argument format changed to support boolean flags properly
- FastAPI now uses Pydantic v2 validation

## Support Policy

| Version | Status | Python Versions | End of Life |
|---------|--------|----------------|-------------|
| 1.x     | Current | 3.10, 3.11, 3.12 | TBD |
| 0.x     | EOL | 3.9 | 2026-05-01 |

Security patches will be backported to 1.x for 12 months after EOL.