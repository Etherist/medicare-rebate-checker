"""Report Generator Agent."""
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Autonomous agent for generating rebate reports."""
    
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir) if output_dir else Path("reports")
        self.output_dir.mkdir(exist_ok=True)
        self.report_count = 0
        logger.info(f"ReportGenerator initialized with output dir: {self.output_dir}")
    
    def generate_report(self, mbs_item: Dict[str, Any], patient: Dict[str, Any], eligibility: Dict[str, Any], calculation: Dict[str, Any], format: str = "markdown") -> Dict[str, Any]:
        """Generate a comprehensive rebate report."""
        self.report_count += 1
        
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == "markdown":
            content = self._generate_markdown_report(mbs_item, patient, eligibility, calculation, timestamp)
            file_ext = ".md"
        elif format.lower() == "html":
            content = self._generate_html_report(mbs_item, patient, eligibility, calculation, timestamp)
            file_ext = ".html"
        elif format.lower() == "json":
            content = self._generate_json_report(mbs_item, patient, eligibility, calculation, timestamp)
            file_ext = ".json"
        else:
            raise ValueError(f"Unsupported report format: {format}")
        
        item_number = mbs_item.get("item_number", "unknown")
        filename = f"rebate_{item_number}_{timestamp_str}{file_ext}"
        file_path = self.output_dir / filename
        
        result = {
            "content": content,
            "format": format,
            "filename": filename,
            "file_path": str(file_path),
            "timestamp": timestamp.isoformat(),
        }
        
        logger.info(f"Generated {format} report for MBS item {item_number}")
        
        return result
    
    def save_report(self, report: Dict[str, Any]) -> str:
        """Save a generated report to disk."""
        file_path = Path(report["file_path"])
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report["content"])
        
        logger.info(f"Report saved to: {file_path}")
        return str(file_path)
    
    def generate_and_save(self, mbs_item: Dict[str, Any], patient: Dict[str, Any], eligibility: Dict[str, Any], calculation: Dict[str, Any], format: str = "markdown") -> Dict[str, Any]:
        """Generate a report and save it to disk."""
        report = self.generate_report(mbs_item, patient, eligibility, calculation, format)
        saved_path = self.save_report(report)
        report["file_path"] = saved_path
        return report
    
    def _generate_markdown_report(self, mbs_item: Dict[str, Any], patient: Dict[str, Any], eligibility: Dict[str, Any], calculation: Dict[str, Any], timestamp: datetime) -> str:
        """Generate a Markdown formatted report."""
        item_number = mbs_item.get("item_number", "N/A")
        description = mbs_item.get("description", "N/A")
        category = mbs_item.get("category", "N/A")
        
        eligible = eligibility.get("eligible", True)
        eligible_icon = "✅" if eligible else "❌"
        eligible_text = "ELIGIBLE" if eligible else "NOT ELIGIBLE"
        
        schedule_fee = calculation.get("schedule_fee", 0)
        rebate_amount = calculation.get("rebate_amount", 0)
        gap_fee = calculation.get("gap_fee", 0)
        rebate_pct = calculation.get("rebate_percentage", 0)
        coverage = calculation.get("coverage_level", "Unknown")
        
        patient_age = patient.get("age", "N/A")
        has_card = "Yes" if patient.get("has_medicare_card", True) else "No"
        has_referral = "Yes" if patient.get("has_referral", False) else "No"
        
        reasons = eligibility.get("reasons", [])
        warnings = eligibility.get("warnings", [])
        errors = eligibility.get("errors", [])
        
        lines = []
        lines.append("# Medicare Rebate Eligibility Report")
        lines.append("")
        lines.append(f"**Generated:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        lines.append("## 📋 Eligibility Summary")
        lines.append("")
        lines.append(f"{eligible_icon} **Status:** **{eligible_text}**")
        lines.append("")
        
        lines.append("## 🏥 MBS Item Details")
        lines.append("")
        lines.append(f"| Field | Value |")
        lines.append(f"|-------|-------|")
        lines.append(f"| **Item Number** | {item_number} |")
        lines.append(f"| **Description** | {description} |")
        lines.append(f"| **Category** | {category} |")
        lines.append("")
        
        lines.append("## 👤 Patient Information")
        lines.append("")
        lines.append(f"| Field | Value |")
        lines.append(f"|-------|-------|")
        lines.append(f"| **Age** | {patient_age} years |")
        lines.append(f"| **Medicare Card** | {has_card} |")
        lines.append(f"| **Referral** | {has_referral} |")
        lines.append("")
        
        lines.append("## 💰 Financial Breakdown")
        lines.append("")
        lines.append(f"| Item | Amount |")
        lines.append(f"|------|--------|")
        lines.append(f"| **Schedule Fee** | ${schedule_fee:.2f} |")
        lines.append(f"| **Medicare Rebate** | ${rebate_amount:.2f} |")
        lines.append(f"| **Gap Fee** | ${gap_fee:.2f} |")
        lines.append(f"| **Rebate %** | {rebate_pct}% |")
        lines.append(f"| **Coverage Level** | {coverage} |")
        lines.append("")
        
        if reasons:
            lines.append("## 🔍 Eligibility Details")
            lines.append("")
            for reason in reasons:
                status = reason.get("status", "")
                message = reason.get("message", "")
                check = reason.get("check", "")
                icon = "✅" if status == "PASSED" else "❌" if status == "FAILED" else "⚠️"
                lines.append(f"- {icon} **{check}**: {message}")
            lines.append("")
        
        if warnings:
            lines.append("## ⚠️ Warnings")
            lines.append("")
            for warning in warnings:
                lines.append(f"- ⚠️ {warning}")
            lines.append("")
        
        if errors:
            lines.append("## ❌ Errors")
            lines.append("")
            for error in errors:
                lines.append(f"- ❌ {error}")
            lines.append("")
        
        notes = mbs_item.get("notes")
        if notes:
            lines.append("## ℹ️ Notes")
            lines.append("")
            lines.append(f"{notes}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        lines.append("*This report was generated by the Medicare Rebate Eligibility Checker.*")
        
        return "\n".join(lines)
    
    def _generate_html_report(self, mbs_item: Dict[str, Any], patient: Dict[str, Any], eligibility: Dict[str, Any], calculation: Dict[str, Any], timestamp: datetime) -> str:
        """Generate an HTML formatted report."""
        markdown = self._generate_markdown_report(mbs_item, patient, eligibility, calculation, timestamp)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Medicare Rebate Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .eligible {{ color: #27ae60; font-weight: bold; }}
        .not-eligible {{ color: #e74c3c; font-weight: bold; }}
    </style>
</head>
<body>
{markdown.replace(chr(10), '<br>')}
</body>
</html>"""
        
        return html
    
    def _generate_json_report(self, mbs_item: Dict[str, Any], patient: Dict[str, Any], eligibility: Dict[str, Any], calculation: Dict[str, Any], timestamp: datetime) -> str:
        """Generate a JSON formatted report."""
        report_data = {
            "report_type": "Medicare Rebate Eligibility",
            "generated_at": timestamp.isoformat(),
            "mbs_item": mbs_item,
            "patient": patient,
            "eligibility": eligibility,
            "calculation": calculation,
        }
        
        return json.dumps(report_data, indent=2, default=str)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get generator statistics."""
        return {
            "total_reports": self.report_count,
            "output_directory": str(self.output_dir),
        }


def generate_report(mbs_item: Dict[str, Any], patient: Dict[str, Any], eligibility: Dict[str, Any], calculation: Dict[str, Any], format: str = "markdown") -> Dict[str, Any]:
    """Convenience function to generate a report."""
    generator = ReportGenerator()
    return generator.generate_report(mbs_item, patient, eligibility, calculation, format)
