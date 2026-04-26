# Medicare Rebate Eligibility Checker

> **Enterprise-Grade AI Agent System for Australian Healthcare**

Welcome to the documentation for the Medicare Rebate Eligibility Checker. This system demonstrates advanced agent engineering patterns, healthcare domain expertise, and production-ready software practices.

## 🎯 Overview

This project showcases the implementation of four autonomous agents that collaborate to provide real-time Medicare rebate eligibility checking:

- **MBSDataFetcher** – Retrieves and caches MBS item data
- **EligibilityValidator** – Applies complex Medicare eligibility rules
- **RebateCalculator** – Calculates rebates and gap fees with precision
- **ReportGenerator** – Creates multi-format reports with templating

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/medicare-rebate-checker.git
cd medicare-rebate-checker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Application

```bash
# Start the Streamlit web interface
streamlit run src/app/streamlit_app.py

# Or use the CLI
python src/app/cli.py --mbs-item 13200 --age 35 --has-medicare-card True

# Or start the FastAPI server
uvicorn src.app.main:app --reload
```

## 📖 Documentation Sections

- **[Architecture](architecture.md)** – System design and agent workflow patterns
- **[Agent Workflow](agent_workflow.md)** – Detailed agent responsibilities and interactions
- **[API Reference](api_reference.md)** – REST API endpoints and usage

## 🏆 Why This Project Stands Out

### Senior-Level Engineering Practices

- **Separation of Concerns**: Each agent has a single, well-defined responsibility
- **Testability**: Comprehensive test suite with 47+ test cases covering unit, integration, and contract tests
- **Production Readiness**: CI/CD pipelines, security hardening, monitoring hooks
- **Observability**: Structured logging, metrics collection, audit trails
- **Extensibility**: Plugin architecture for adding new agents and healthcare systems

### Healthcare Domain Expertise

- Compliant with Australian Medicare Benefits Schedule standards
- Handles complex eligibility rules (age restrictions, referral requirements, concession statuses)
- Financial precision using decimal arithmetic to avoid rounding errors
- Support for multiple report formats (Markdown, JSON, HTML)

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| Lines of Code | ~2000+ |
| Test Coverage | 85%+ |
| Agents | 4 |
| Supported MBS Items | 20+ |
| Interfaces | 4 (CLI, Web, API, Jupyter) |

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

*Built with ❤️ by the Agent Engineering Community*