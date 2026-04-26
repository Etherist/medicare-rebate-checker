# Privacy Policy

## Overview

The Medicare Rebate Eligibility Checker is designed with privacy as a core principle. This document outlines our data handling practices.

## Data Collection

### What We Collect (and Don't Collect)

**DO collect:**
- MBS item numbers for lookup
- Patient age (for eligibility determination)
- Eligibility flags (Medicare card status, concession status, hospital status, referral status)
- Calculation results (rebate amounts, gap fees)

**DO NOT collect:**
- Patient names
- Medicare card numbers
- Addresses
- Phone numbers
- Email addresses
- Any other personally identifiable information (PII)

## Data Storage

### Local Installation (User's Responsibility)

When you install and run this software locally:
- Data stays on your machine
- Reports are saved in the `reports/` directory (configurable)
- No data is transmitted to external servers (except optional API calls to MBS Online if configured)

**Important**: You are responsible for securing any generated reports that may contain patient information.

### Cloud/SaaS Deployment (If Offered)

If a hosted version is provided:
- Data processed in memory only; no persistent storage
- Logs aggregated without PII
- Autodelete after 30 days (configurable)
- Encrypted at rest and in transit

## Data Processing

### Real-Time Only

All eligibility checks are processed in real-time:
- No persistent database of patient records
- No longitudinal tracking
- Each request is independent
- Cache stores only MBS item metadata (no patient data)

### MBS Data Source

- Uses local JSON dataset for development (bundled with repository)
- Production deployments can connect to official MBS Online API (requires authentication)
- No patient data ever sent to MBS Online

## Data Retention

### Generated Reports

- Reports stored in `reports/` directory (default)
- Retained until manually deleted
- Recommended retention: 30 days (configurable via `REPORT_RETENTION_DAYS`)
- Secure deletion recommended for sensitive reports

### Logs

- Application logs contain request metadata (item numbers, processing times, cache hits)
- No PII in logs by default
- Log rotation configured (if using production logging setup)

## Compliance

### Australian Privacy Principles (APPs)

This system is designed to support compliance with APPs:
- APP 1 – Open and transparent management: Clear privacy notice provided
- APP 2 – Anonymity and pseudonymity: Can be used without identifying patients
- APP 3 – Collection of personal information: Only minimum necessary collected
- APP 6 – Use and disclosure: Limited to stated purpose
- APP 11 – Security of personal information: Security controls implemented

### Healthcare-Specific Regulations

- Not a substitute for professional medical billing advice
- Users responsible for ensuring compliance with Medicare guidelines
- System aids calculation; final eligibility determination rests with healthcare provider

## User Responsibilities

When using this software:

1. **Secure Storage**: Protect generated reports containing patient information
2. **Access Control**: Limit who can use the system
3. **Consent**: Obtain patient consent where required by law before entering data
4. **Accuracy**: Verify calculation results against official Medicare documentation
5. **Retention**: Follow your organization's data retention policies

## Third-Party Services

### Optional: MBS Online API

If configured to use official MBS Online API:
- Requires separate authentication (not included)
- Subject to Medicare Australia's Terms of Use
- No patient data transmitted (only item numbers)
- Review MBS Online privacy policy separately

## Data Breach Response

In event of suspected data breach:
1. Immediately revoke access to any deployed instances
2. Review access logs for unusual activity
3. Notify affected parties as required by law (within 30 days for eligible data breaches under Notifiable Data Breaches scheme)
4. Report to Office of the Australian Information Commissioner (OAIC)
5. Implement remediation measures

## Changes to This Policy

This privacy policy may be updated:
- When features change data handling
- To reflect regulatory changes
- To improve clarity

Updated versions will be committed to repository with bump in version number.

## Contact

Privacy-related questions: **privacy@your-domain.com**

---

*Version: 1.0.0 | Effective: April 2026*