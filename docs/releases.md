# Release Process

This document describes how to create a new release of the Medicare Rebate Checker.

## Versioning

We use [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH
```

Examples:
- `1.0.0` – initial stable release
- `1.1.0` – added new agent, backward compatible
- `1.1.1` – bug fix, no new features
- `2.0.0` – breaking changes to agent API

## Release Checklist

- [ ] All tests pass on CI (including matrix of Python versions)
- [ ] Code coverage ≥ 85%
- [ ] No security warnings (`make security` clean)
- [ ] Documentation built successfully (`make docs-build`)
- [ ] CHANGELOG.md updated with new version
- [ ] Version numbers updated in:
  - `pyproject.toml` (version = "X.Y.Z")
  - `src/__init__.py` (if present)
  - `docs/index.md` (if version mentioned)
- [ ] Docker image built and tested
- [ ] Kubernetes manifests version-tagged (if applicable)
- [ ] GitHub Release draft created

## Automated Release (GitHub Actions)

### Option A: Using release-please (Recommended)

1. Ensure your PRs follow [Conventional Commits](https://www.conventionalcommits.org/).
2. Merge PRs to `main` branch.
3. `release-please` action will automatically:
   - Determine version bump based on commit messages
   - Update CHANGELOG.md
   - Create a GitHub release draft

4. Review and publish the draft release.

### Option B: Manual Release

1. **Create release branch from main**
   ```bash
   git checkout main
   git pull upstream main
   git checkout -b release/v1.0.0
   ```

2. **Update version numbers**
   - Edit `pyproject.toml`: `version = "1.0.0"`
   - Commit: `git commit -am "chore: bump version to 1.0.0"`

3. **Create tag**
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push upstream main --tags
   ```

4. **Create GitHub Release**
   - Go to https://github.com/your-username/medicare-rebate-checker/releases/new
   - Choose tag `v1.0.0`
   - Title: `v1.0.0`
   - Description: Copy CHANGELOG entry for this version
   - Attach built artifacts (optional):
     - Docker image pushed to registry
     - Wheels: `uv build`
   - Publish release

5. **Post-release**
   - Create `main` branch backport if needed: `git checkout -b chore/backport-1.0.1`
   - Update `develop` branch with version bump from release if necessary

## Release Types

### Full Release

- Includes Docker image push
- Helm chart version bump
- Documentation deployment
- Announcement on project channels

### Hotfix Release

For critical security fixes:

1. Branch from latest release tag:
   ```bash
   git checkout -b hotfix/1.0.1 v1.0.0
   ```
2. Apply fix, commit with `fix:` prefix
3. Follow manual release steps (but version is `1.0.1`)
4. Merge back to `main` and `develop`

### Alpha/Beta/RC

Pre-releases for testing:

```bash
# Create pre-release tag
git tag -a v1.1.0-rc.1 -m "Release candidate 1 for v1.1.0"
git push upstream --tags

# On GitHub, mark as pre-release
```

Users install with:
```bash
pip install medicare-rebate-checker==1.1.0rc1
```

## Post-Release Tasks

### 1. Update Deployment

```bash
# Update Docker image tags in k8s manifests
sed -i 's|medicare-rebate-checker:latest|medicare-rebate-checker:v1.0.0|g' k8s/*.yaml

# Commit
git add k8s/
git commit -m "chore: update image tag to v1.0.0"
```

### 2. Deploy to Production

```bash
# Apply new manifests
kubectl apply -f k8s/

# Verify rollout
kubectl rollout status deployment/medicare-checker-api -n healthcare
```

### 3. Monitor

Observe metrics for 24h:
- Error rates
- Latency
- Cache hit ratio

### 4. Announce

- Update project README badge versions
- Post to project mailing list / Discord
- Tweet / LinkedIn post (optional)
- Update Wikipedia / external links if applicable

## Rollback Procedure

If release introduces critical bug:

```bash
# Kubernetes
kubectl rollout undo deployment/medicare-checker-api -n healthcare

# Docker Compose
docker-compose pull medicare-checker:previous-tag
docker-compose up -d

# Or revert Git tag & redeploy
git revert <release-commit>
```

Create new hotfix release ASAP.

## Release Artifacts

Each release should produce:

| Artifact | Location | Description |
|-----------|----------|-------------|
| Source tarball | GitHub Release (`*.tar.gz`) | Source code distribution |
| Wheel | GitHub Release (`*.whl`) | Built distribution |
| Docker image | Docker Hub / GHCR | `your-username/medicare-rebate-checker:v1.0.0` |
| Helm chart | GitHub Release (chart package) | `.tgz` package |
| Documentation | GitHub Pages | Updated site automatically |
| SBOM | GitHub Release (`bom.xml`) | Software Bill of Materials (CycloneDX) |

## Version Compatibility Matrix

| API Version | Agent Protocol | Compatible Python |
|-------------|----------------|------------------|
| 1.0.x       | v1             | 3.10–3.12        |
| 0.x         | v0 (legacy)    | 3.9–3.11         |

When introducing breaking changes:
- Bump MAJOR version
- Update protocol version
- Provide migration guide in release notes

---

*Last updated: April 2026*