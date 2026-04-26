# Security Policy

## Supported Versions

| Version | Supported          |
|---------|-------------------|
| 1.x     | ✅ Active support |
| 0.x     | ❌ End of Life    |

## Reporting a Vulnerability

We take security issues seriously. If you discover a vulnerability, please follow these steps:

### **DO NOT** open a public GitHub issue for security vulnerabilities.

Instead, email the security team at: **security@your-domain.com**

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)
- Your contact information

We will respond within **48 hours** with an acknowledgement and timeline for addressing.

## Security Measures

### Data Protection

- **No PII Storage**: The system does NOT store personally identifiable information
- **Input Validation**: All user inputs validated via Pydantic schemas
- **Rate Limiting**: Configurable rate limiting on API endpoints
- **Secure Headers**: Security headers enabled (HSTS, CSP, etc.)

### Secrets Management

- Secrets stored in Kubernetes Secrets or environment variables
- Never commit credentials or API keys
- Use `.env.example` as template; actual `.env` is gitignored

### Supply Chain Security

- Dependencies scanned with `safety` and `bandit`
- SBOM generated for each release
- Automated Dependabot updates enabled
- Minimal dependency set

### Infrastructure Security

- Containers run as non-root user
- Minimal attack surface (slim Python base images)
- Regular security updates (via CI)
- Read-only filesystem mounts where possible

### Compliance

- Designed with Australian Privacy Principles in mind
- Healthcare data handling follows best practices
- Audit logging for eligibility checks

## Best Practices for Deployers

1. **Change all default passwords/secrets** before production deployment
2. **Enable TLS** for all external endpoints (use provided Ingress with cert-manager)
3. **Configure firewall rules** to restrict access
4. **Regularly update dependencies** (`uv sync --upgrade`)
5. **Monitor logs** for suspicious activity
6. **Implement WAF** (Web Application Firewall) for API protection
7. **Enable audit logging** to track eligibility checks
8. **Rotate secrets** periodically (90-day minimum)

## Known Security Considerations

- **MBS Data Source**: Current implementation uses local JSON for demo. Production use requires authenticated MBS Online API integration.
- **Cache**: Redis cache should be deployed with authentication and TLS in production
- **Reports**: Generated reports may contain PHI - secure storage required

## Security Checklist for Production

- [ ] All default passwords changed
- [ ] TLS/SSL configured for all endpoints
- [ ] Rate limiting enabled and tuned
- [ ] Audit logging to external system
- [ ] Container scanning in CI/CD pipeline
- [ ] Vulnerability scanning scheduled (weekly minimum)
- [ ] Backup and disaster recovery plan documented
- [ ] Incident response plan established
- [ ] Penetration test completed
- [ ] Security training for operations team

## Responsible Disclosure

We follow responsible disclosure practices:
1. Reporter notifies us privately
2. We acknowledge within 48 hours
3. We investigate and develop fix
4. We disclose after patch release (typically 90 days)
5. Reporter credited (unless anonymity requested)

## Contact

Security issues: **security@your-domain.com**
General questions: Open GitHub issue with `security` label

---

*Last updated: April 2026*