# Roadmap

Future directions for the Medicare Rebate Checker.

## v1.x Series (Current)

**v1.0** – First stable release ✅

- [x] 4 autonomous agents
- [x] CLI, FastAPI, Streamlit interfaces
- [x] 20 MBS items
- [x] Comprehensive test suite
- [x] CI/CD pipelines
- [x] Documentation site

**v1.1** *(Planned Q3 2026)*

- [ ] **Telehealth Support**: After-hours and telehealth-specific items
- [ ] **Bulk Billing Incentives**: Additional calculations for bulk billing incentives
- [ ] **Public Healthcare**: State-based public hospital rules
- [ ] **Private Health Insurance**: Integration with private insurer rebates
- [ ] **Bulk Import**: CSV upload for batch processing
- [ ] **Report Templates**: Customisable branding (logo, colors)
- [ ] **Export to PDF**: Direct PDF generation

## v2.x Series (Future)

**v2.0** *(Planned 2027)*

- [ ] **Plugin Architecture**: Load external agent modules dynamically
- [ ] **Workflow Engine**: Sequence multiple agents for complex scenarios
- [ ] **MBS Online Integration**: Live data updates with authentication
- [ ] **Advanced Analytics**: Dashboard of utilisation patterns (aggregated, no PII)
- [ ] **Multi-Region**: Support for NZ, UK, US coding systems
- [ ] **AI Assistance**: LLM-powered natural language queries (optional)
- [ ] **FHIR Compatibility**: Interface with electronic health records
- [ ] **Mobile App**: React Native or Flutter client

## Known Limitations

| Limitation | Workaround | Target Fix |
|------------|------------|------------|
| No real-time MBS updates | Manual JSON update | v2.0 (API integration) |
| Limited to item-level checks | Manual multiple-item sums | v1.1 (batching) |
| No patient history | Manual record-keeping | v2.0 (optional secure storage) |
| Australian Medicare only | Internationalisation | v2.0 (regional modules) |

## Feature Requests

We track feature requests via GitHub issues. Popular requests:

- [ ] Ability to save patient history (with encryption)
- [ ] Export to PDF via WeasyPrint
- [ ] SMS/email report delivery
- [ ] Integration with practice management software (Medical Director, Best Practice)
- [ ] Multi-language support (e.g., Arabic, Mandarin)
- [ ] Voice input for patient details
- [ ] Offline mode with Progressive Web App (PWA)
- [ ] Docker image size optimisation (<200MB)

## Community Ideas

Have a suggestion? Open a GitHub issue with the "enhancement" label or upvote existing ones.

## Contributing

Want to implement a feature? Check [Contributing](../CONTRIBUTING.md) and reach out to maintainers first to avoid duplicated effort.

---

*This roadmap is subject to change based on community input and funding.*