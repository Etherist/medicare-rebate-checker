# Agent Workflow & Collaboration

## Detailed Agent Specifications

### 1. MBSDataFetcher Agent

**Role**: Data retrieval and caching layer.

**Responsibilities**:
- Load MBS item data from JSON source
- Provide cache-first retrieval with TTL
- Support bulk fetching and search operations
- Failover to local JSON if remote source unavailable

**Public Interface**:
- `fetch_mbs_item(item_number: str) -> Optional[Dict]`
- `get_all_items() -> Dict[str, Dict]`
- `clear_cache()`
- `get_cache_info() -> Dict`

### 2. EligibilityValidator Agent

**Role**: Rule engine for Medicare eligibility.

**Responsibilities**:
- Validate patient eligibility against item rules
- Check Medicare card requirement
- Enforce age restrictions (e.g., 70+, 45-49)
- Verify referral requirements
- Identify bulk billing eligibility

**Public Interface**:
- `validate_eligibility(mbs_item: Dict, patient: Dict) -> Dict`

**Validation Rules Supported**:
- `medicare_card_required` (bool)
- `age_restriction` (string: "70+", "45-49", "min-max")
- `requires_referral` (bool)
- `bulk_billing_eligible` (bool)

### 3. RebateCalculator Agent

**Role**: Financial computation engine.

**Responsibilities**:
- Determine applicable rebate percentage
- Handle after-hours multipliers
- Calculate gap fees
- Apply bulk billing adjustments
- Support batch calculations

**Public Interface**:
- `calculate_rebate(mbs_item: Dict, patient: Dict, eligibility: Optional[Dict]) -> Dict`
- `calculate_multiple(items_data: List[Dict]) -> Dict`

**Computation Details**:
- Uses Decimal precision for financial accuracy
- Rounds to 2 decimal places (cents)
- Overrides percentage to 0% for ineligible patients

### 4. ReportGenerator Agent

**Role**: Output generation and formatting.

**Responsibilities**:
- Generate human-readable reports (Markdown)
- Produce machine-readable formats (JSON)
- Optionally create HTML for web display
- Save reports to filesystem with timestamps

**Public Interface**:
- `generate_report(mbs_item, patient, eligibility, calculation, format) -> Dict`
- `generate_and_save(...) -> Dict`
- `save_report(report) -> str`

**Report Sections**:
- Eligibility summary with icons
- MBS item details table
- Patient information
- Financial breakdown
- Eligibility details (reasons, warnings, errors)

## Interaction Sequence

1. **User Request** arrives via CLI / API / UI
2. **MBSDataFetcher** loads item metadata from cache or JSON
3. **EligibilityValidator** checks patient against item rules
4. **RebateCalculator** computes rebate based on eligibility outcome
5. **ReportGenerator** formats and saves the results
6. **Response** returned to user with report path

Each agent operates independently; failures in one agent do not cascade due to defensive programming and clear error boundaries.