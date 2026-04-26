"""Rebate Calculator Agent."""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RebateCalculator:
    """Autonomous agent for calculating Medicare rebates."""
    
    def __init__(self):
        self.calculation_count = 0
        logger.info("RebateCalculator initialized")
    
    def calculate_rebate(self, mbs_item: Dict[str, Any], patient: Dict[str, Any], eligibility: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calculate rebate amount and gap fee for an MBS item."""
        self.calculation_count += 1
        
        schedule_fee = self._get_schedule_fee(mbs_item)
        if schedule_fee is None:
            logger.error("Could not determine schedule fee")
            return self._error_result("Invalid MBS item: missing fee information")
        
        rebate_percentage = self._get_rebate_percentage(mbs_item, patient, eligibility)
        
        rebate_amount = round(schedule_fee * (rebate_percentage / 100), 2)
        gap_fee = round(schedule_fee - rebate_amount, 2)
        
        coverage_level = self._get_coverage_level(rebate_percentage)
        
        after_hours_multiplier = mbs_item.get("rules", {}).get("after_hours_multiplier", 1.0)
        if after_hours_multiplier != 1.0:
            original_fee = schedule_fee
            schedule_fee = round(schedule_fee * after_hours_multiplier, 2)
            rebate_amount = round(schedule_fee * (rebate_percentage / 100), 2)
            gap_fee = round(schedule_fee - rebate_amount, 2)
            logger.info(f"Applied after-hours multiplier: {after_hours_multiplier}x")
        
        result = {
            "schedule_fee": schedule_fee,
            "rebate_amount": rebate_amount,
            "gap_fee": gap_fee,
            "rebate_percentage": rebate_percentage,
            "coverage_level": coverage_level,
            "after_hours_multiplier": after_hours_multiplier,
            "calculation_timestamp": datetime.now().isoformat(),
        }
        
        if eligibility is not None:
            result["eligible"] = eligibility.get("eligible", True)
            result["eligibility_errors"] = eligibility.get("errors", [])
        
        logger.info(
            f"Calculated rebate for MBS {mbs_item.get('item_number')}: "
            f"${rebate_amount} (gap: ${gap_fee})"
        )
        
        return result
    
    def calculate_multiple(self, items_data: list[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate rebates for multiple MBS items."""
        calculations = []
        total_schedule = 0
        total_rebate = 0
        total_gap = 0
        
        for item_data in items_data:
            mbs_item = item_data.get("mbs_item")
            patient = item_data.get("patient", {})
            eligibility = item_data.get("eligibility")
            
            if not mbs_item:
                logger.warning("Missing MBS item in batch calculation")
                continue
            
            calc = self.calculate_rebate(mbs_item, patient, eligibility)
            calculations.append({
                "item_number": mbs_item.get("item_number"),
                "description": mbs_item.get("description"),
                "calculation": calc,
            })
            
            total_schedule += calc["schedule_fee"]
            total_rebate += calc["rebate_amount"]
            total_gap += calc["gap_fee"]
        
        summary = {
            "total_schedule_fee": round(total_schedule, 2),
            "total_rebate": round(total_rebate, 2),
            "total_gap_fee": round(total_gap, 2),
            "average_coverage": round(
                (total_rebate / total_schedule * 100) if total_schedule > 0 else 0, 1
            ),
        }
        
        return {
            "calculations": calculations,
            "summary": summary,
            "item_count": len(calculations),
        }
    
    def _get_schedule_fee(self, mbs_item: Dict[str, Any]) -> Optional[float]:
        """Extract schedule fee from MBS item."""
        fee = mbs_item.get("schedule_fee")
        if fee is None:
            fee = mbs_item.get("fee")
        
        try:
            return float(fee)
        except (TypeError, ValueError):
            return None
    
    def _get_rebate_percentage(self, mbs_item: Dict[str, Any], patient: Dict[str, Any], eligibility: Optional[Dict[str, Any]]) -> float:
        """Determine the rebate percentage for this item/patient."""
        # Eligibility takes priority: if patient is not eligible, rebate is 0%
        if eligibility and not eligibility.get("eligible", True):
            return 0.0
        
        # Check for explicit rebate percentage on the item
        item_percentage = mbs_item.get("rebate_percentage")
        if item_percentage is not None:
            return float(item_percentage)
        
        # Check for percentage in rules
        rules = mbs_item.get("rules", {})
        rules_percentage = rules.get("rebate_percentage")
        if rules_percentage is not None:
            return float(rules_percentage)
        
        # Default to 100% if no specific percentage defined and eligible
        return 100.0
    
    def _get_coverage_level(self, rebate_percentage: float) -> str:
        """Get descriptive coverage level based on percentage."""
        if rebate_percentage >= 100:
            return "Full Coverage"
        elif rebate_percentage >= 85:
            return "High Coverage"
        elif rebate_percentage >= 70:
            return "Moderate Coverage"
        elif rebate_percentage >= 50:
            return "Partial Coverage"
        elif rebate_percentage > 0:
            return "Minimal Coverage"
        else:
            return "No Coverage"
    
    def _error_result(self, message: str) -> Dict[str, Any]:
        """Return error result."""
        return {
            "schedule_fee": 0.0,
            "rebate_amount": 0.0,
            "gap_fee": 0.0,
            "rebate_percentage": 0,
            "coverage_level": "Error",
            "after_hours_multiplier": 1.0,
            "calculation_timestamp": datetime.now().isoformat(),
            "error": message,
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get calculator statistics."""
        return {
            "total_calculations": self.calculation_count,
        }


def calculate_rebate(mbs_item: Dict[str, Any], patient: Dict[str, Any], eligibility: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to calculate rebate."""
    calculator = RebateCalculator()
    return calculator.calculate_rebate(mbs_item, patient, eligibility)
