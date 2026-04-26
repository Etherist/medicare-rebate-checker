"""Eligibility Validator Agent."""
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class EligibilityValidator:
    """Autonomous agent for validating Medicare rebate eligibility."""
    
    def __init__(self):
        self.validation_count = 0
        logger.info("EligibilityValidator initialized")
    
    def validate_eligibility(self, mbs_item: Dict[str, Any], patient: Dict[str, Any]) -> Dict[str, Any]:
        """Validate patient eligibility for an MBS item rebate."""
        self.validation_count += 1
        
        result = {
            "eligible": True,
            "reasons": [],
            "warnings": [],
            "errors": [],
            "timestamp": datetime.now().isoformat(),
        }
        
        input_errors = self._validate_inputs(mbs_item, patient)
        if input_errors:
            result["errors"].extend(input_errors)
            result["eligible"] = False
            logger.error(f"Input validation failed: {input_errors}")
            return result
        
        rules = mbs_item.get("rules", {})
        
        self._check_medicare_card(patient, rules, result)
        self._check_age_restriction(patient, rules, result)
        self._check_referral_requirement(patient, rules, result)
        self._check_bulk_billing(patient, rules, result)
        
        if result["errors"]:
            result["eligible"] = False
        
        logger.info(
            f"Eligibility check for MBS {mbs_item.get('item_number')}: "
            f"{'ELIGIBLE' if result['eligible'] else 'NOT ELIGIBLE'}"
        )
        
        return result
    
    def _validate_inputs(self, mbs_item: Dict[str, Any], patient: Dict[str, Any]) -> list:
        """Validate input data structures."""
        errors = []
        
        if not isinstance(mbs_item, dict):
            errors.append("MBS item must be a dictionary")
        elif "item_number" not in mbs_item:
            errors.append("MBS item must contain 'item_number'")
        elif "rules" not in mbs_item:
            errors.append("MBS item must contain 'rules'")
        
        if not isinstance(patient, dict):
            errors.append("Patient data must be a dictionary")
        elif "age" not in patient:
            errors.append("Patient data must contain 'age'")
        elif not isinstance(patient["age"], (int, float)):
            errors.append("Patient age must be a number")
        elif patient["age"] < 0 or patient["age"] > 150:
            errors.append("Patient age must be between 0 and 150")
        
        return errors
    
    def _check_medicare_card(self, patient: Dict[str, Any], rules: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Check if patient has a valid Medicare card."""
        requires_card = rules.get("medicare_card_required", True)
        has_card = patient.get("has_medicare_card", True)
        
        if requires_card and not has_card:
            result["eligible"] = False
            result["errors"].append("Medicare card is required for this service")
            result["reasons"].append({
                "check": "Medicare card requirement",
                "status": "FAILED",
                "message": "Patient does not have a Medicare card",
            })
        else:
            result["reasons"].append({
                "check": "Medicare card requirement",
                "status": "PASSED",
                "message": "Medicare card requirement satisfied",
            })
    
    def _check_age_restriction(self, patient: Dict[str, Any], rules: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Check if patient meets age restrictions."""
        age_restriction = rules.get("age_restriction")
        patient_age = patient["age"]
        
        if not age_restriction:
            result["reasons"].append({
                "check": "Age restriction",
                "status": "PASSED",
                "message": "No age restrictions apply",
            })
            return
        
        eligible = False
        
        if age_restriction == "70+":
            eligible = patient_age >= 70
            restriction_text = "70 years or older"
        elif age_restriction == "45-49":
            eligible = 45 <= patient_age <= 49
            restriction_text = "between 45 and 49 years"
        elif "-" in age_restriction:
            try:
                min_age, max_age = map(int, age_restriction.split("-"))
                eligible = min_age <= patient_age <= max_age
                restriction_text = f"between {min_age} and {max_age} years"
            except ValueError:
                logger.error(f"Invalid age restriction format: {age_restriction}")
                result["warnings"].append(f"Could not parse age restriction: {age_restriction}")
                return
        else:
            try:
                min_age = int(age_restriction)
                eligible = patient_age >= min_age
                restriction_text = f"{min_age} years or older"
            except ValueError:
                logger.error(f"Invalid age restriction format: {age_restriction}")
                result["warnings"].append(f"Could not parse age restriction: {age_restriction}")
                return
        
        if eligible:
            result["reasons"].append({
                "check": "Age restriction",
                "status": "PASSED",
                "message": f"Patient is {restriction_text}",
            })
        else:
            result["eligible"] = False
            result["errors"].append(
                f"Age restriction not met: must be {restriction_text}"
            )
            result["reasons"].append({
                "check": "Age restriction",
                "status": "FAILED",
                "message": f"Patient is {patient_age} years old, must be {restriction_text}",
            })
    
    def _check_referral_requirement(self, patient: Dict[str, Any], rules: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Check if patient has required referral."""
        requires_referral = rules.get("requires_referral", False)
        has_referral = patient.get("has_referral", False)
        
        if requires_referral and not has_referral:
            result["eligible"] = False
            result["errors"].append("Referral is required for this service")
            result["reasons"].append({
                "check": "Referral requirement",
                "status": "FAILED",
                "message": "Patient does not have a referral",
            })
        elif requires_referral and has_referral:
            result["reasons"].append({
                "check": "Referral requirement",
                "status": "PASSED",
                "message": "Patient has required referral",
            })
        else:
            result["reasons"].append({
                "check": "Referral requirement",
                "status": "PASSED",
                "message": "No referral required",
            })
    
    def _check_bulk_billing(self, patient: Dict[str, Any], rules: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Check bulk billing eligibility (informational)."""
        bulk_billing_eligible = rules.get("bulk_billing_eligible", True)
        
        if not bulk_billing_eligible:
            result["warnings"].append(
                "This service is not bulk billing eligible. Patient may have out-of-pocket costs."
            )
            result["reasons"].append({
                "check": "Bulk billing",
                "status": "WARNING",
                "message": "Service is not bulk billing eligible",
            })
        else:
            result["reasons"].append({
                "check": "Bulk billing",
                "status": "PASSED",
                "message": "Service is bulk billing eligible",
            })
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get validator statistics."""
        return {
            "total_validations": self.validation_count,
        }


def validate_eligibility(mbs_item: Dict[str, Any], patient: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to validate eligibility."""
    validator = EligibilityValidator()
    return validator.validate_eligibility(mbs_item, patient)
