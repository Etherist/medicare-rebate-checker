# Compliance & Regulatory Information

## Overview

The Medicare Rebate Eligibility Checker is designed to assist healthcare providers with Medicare billing compliance. This document outlines relevant regulations and how the system supports compliance.

## Australian Healthcare Regulations

### Medicare Benefits Schedule (MBS)

The system implements rules from the **Health Insurance Act 1973** and associated MBS regulations:

- Item-specific eligibility criteria
- Schedule fee determinations
- Rebate percentage rules
- Bulk billing provisions

**Important**: The software provides computational assistance only. Ultimate responsibility for correct billing rests with the healthcare provider.

### Privacy Act 1988 & Australian Privacy Principles (APPs)

**APP Compliance Features**:
- **Data minimisation**: Only collects necessary data for eligibility calculation
- **Purpose limitation**: Data used solely for rebate calculation
- **Security**: Implemented security controls (encryption, access control)
- **Access**: Users can export/delete their data (via file system operations)

### Health Records Act (State-Based)

The system does not store health records beyond what is explicitly entered. Users must comply with state-based health records legislation for report retention.

## International Considerations

For deployments outside Australia:
- Adapt MBS rules to local healthcare schemes
- Ensure compliance with local data sovereignty laws
- Review cross-border data transfer restrictions

## Industry Standards & Frameworks

### ISO/IEC 27001:2022 (Information Security)

The architecture follows ISO 27001 Annex A controls:

| Control | Implementation |
|---------|----------------|
| A.5 – Information security policies | Documented in SECURITY.md |
| A.7 – Human resource security | Role-based access principles |
| A.8 – Asset management | Asset inventory maintained |
| A.9 – Access control | Need-to-know basis, no default secrets |
| A.12 – Operations security | Change management, logging |
| A.13 – Communications security | TLS for external connections |
| A.14 – System acquisition | Secure development lifecycle |
| A.15 – Supplier relationships | Dependency scanning |
| A.16 – Incident management | Logging and alerting hooks |
| A.17 – Business continuity | Containerised deployment |
| A.18 – Compliance | Regular security scans |

### NIST Cybersecurity Framework (CSF)

- **Identify**: Asset inventory (code, dependencies, infrastructure)
- **Protect**: Access controls, encryption, security training
- **Detect**: Logging, monitoring, anomaly detection hooks
- **Respond**: Incident response procedures in SECURITY.md
- **Recover**: Backup and restore documentation

### SOC 2 Type II (Trust Services Criteria)

**Security**: Multi-factor authentication, encryption, firewall configuration  
**Availability**: Redundant deployment options (K8s), health checks  
**Processing Integrity**: Validation logic tested, input sanitisation  
**Confidentiality**: Access controls, encrypted storage  
**Privacy**: Privacy policy adherence, data handling procedures

## Healthcare-Specific Compliance

### HIPAA (United States)

If adapting for US healthcare (HIPAA):
- Map MBS rules to CPT/HCPCS codes
- Implement Business Associate Agreements (BAAs)
- Enable audit trails for PHI access
- Encrypt all ePHI at rest and in transit
- Implement automatic logoff

### GDPR (European Union)

For EU deployments:
- Data Protection Impact Assessment (DPIA) recommended
- Right to erasure implemented (delete reports)
- Data portability via JSON export
- Data protection by design and by default

### My Health Records Act 2012 (Australia)

If integrating with Australian My Health Record:
- Comply with the My Health Record System Operator's rules
- Operator-generated access numbers required
- Additional audit and reporting obligations

## Audit & Logging Requirements

### Logged Events

All agent operations should log:
- Request timestamp
- MBS item number
- Patient age bracket (not exact age)
- Eligibility result (boolean)
- Rebate amount
- Processing duration
- Cache hit/miss status

**Never log**:
- Patient identifiers
- Exact birth dates
- Medicare card numbers

### Log Retention

- Minimum 7 years for audit purposes (per Australian tax requirements)
- Secure log storage with integrity verification
- Log rotation to prevent disk exhaustion

### Audit Trail Format

```json
{
  "timestamp": "2026-04-26T14:31:29.123Z",
  "event": "eligibility_check",
  "mbs_item": "13200",
  "age_bracket": "30-39",
  "eligible": true,
  "rebate_amount": 39.75,
  "processing_time_ms": 127,
  "cache_hit": false,
  "user_id": "clinician_123",  // configured, not PII
  "session_id": "abc-123-def"
}
```

## Certification & Accreditation

### Healthcare Environment Requirements

For use in Australian healthcare settings:
- Not an approved medical device (Class I software exempt)
- Not a substitute for Medicare's official determination
- Healthcare provider remains responsible for billing accuracy

### Cloud Provider Compliance

If deploying to cloud (AWS, Azure, GCP):
- Leverage provider's compliance certifications (IRAP, ISO 27001, etc.)
- Configure VPC, security groups, IAM according to best practices
- Use provider's healthcare compliance offerings

## Regulatory Updates

MBS items and rules change regularly (typically quarterly). The system expects:

1. Regular updates to `src/data/mbs_items.json` from official sources
2. Versioned releases of this software when MBS rules change
3. Configuration option to specify MBS data version

## Reporting Non-Compliance

If you identify a compliance issue:
1. Stop using the affected functionality
2. Report to: **compliance@your-domain.com**
3. Include version number and steps to reproduce
4. We will assess and remediate per our incident management process

## Disclaimer

This software is provided "as-is" for assistance purposes only. It does not guarantee Medicare rebate approval. Users must:
- Verify results against official MBS documentation
- Stay current with MBS rule changes
- Maintain professional judgment in billing decisions

---

*Last reviewed: April 2026 | Next review: October 2026*