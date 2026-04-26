"""
FastAPI REST API for Medicare Rebate Eligibility Checker.
Provides HTTP endpoints for programmatic access to the agent system.
"""
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field, field_validator
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from agents.mbs_fetcher import MBSDataFetcher
from agents.validator import EligibilityValidator
from agents.calculator import RebateCalculator
from agents.reporter import ReportGenerator


# Initialize FastAPI app
app = FastAPI(
    title="Medicare Rebate Eligibility Checker API",
    description="REST API for checking Medicare rebate eligibility using autonomous agents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Initialize agents
fetcher = MBSDataFetcher()
eligibility_validator = EligibilityValidator()
calculator = RebateCalculator()
reporter = ReportGenerator()

# Ensure reports directory exists
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)


# Pydantic models for request/response validation
class RebateCheckRequest(BaseModel):
    """Request model for rebate check."""
    mbs_item: str = Field(..., min_length=1, max_length=10, description="MBS item number")
    age: int = Field(..., ge=0, le=150, description="Patient age in years")
    has_medicare_card: bool = Field(..., description="Whether patient has a valid Medicare card")
    concession_status: bool = Field(default=False, description="Patient concession status")
    hospital_status: bool = Field(default=False, description="Whether patient is admitted to hospital")
    has_referral: bool = Field(default=False, description="Whether patient has a required referral")
    output_format: Optional[str] = Field(default="markdown", description="Report format (markdown, json, html)")
    
    @field_validator('mbs_item')
    @classmethod
    def validate_mbs_item(cls, v):
        """Validate MBS item format."""
        if not v.isdigit():
            raise ValueError('MBS item must contain only digits')
        return v


class RebateCheckResponse(BaseModel):
    """Response model for rebate check."""
    eligible: bool
    rebate_amount: float
    gap_fee: float
    schedule_fee: float
    mbs_item: str
    description: str
    reason: str
    processing_time_ms: Optional[float] = None
    report_path: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str


@app.get("/", tags=["General"])
async def root():
    """Root endpoint - provides API information."""
    return {
        "name": "Medicare Rebate Eligibility Checker API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )


@app.post("/check-rebate", response_model=RebateCheckResponse, tags=["Rebate"])
async def check_rebate(request: RebateCheckRequest):
    """
    Check Medicare rebate eligibility and calculate rebate amount.
    
    This endpoint orchestrates the full agent workflow:
    1. Fetches MBS item details
    2. Validates patient eligibility
    3. Calculates rebate and gap fees
    4. Generates a report
    """
    import time
    start_time = time.time()
    
    try:
        # Step 1: Fetch MBS item details
        mbs_details = fetcher.fetch_mbs_item(request.mbs_item)
        if not mbs_details:
            raise HTTPException(
                status_code=404,
                detail=f"MBS item '{request.mbs_item}' not found"
            )
        
        # Step 2: Validate eligibility
        patient_data = {
            'age': request.age,
            'has_medicare_card': request.has_medicare_card,
            'concession_status': request.concession_status,
            'hospital_status': request.hospital_status,
            'has_referral': request.has_referral
        }
        
        eligibility_result = eligibility_validator.validate_eligibility(
            mbs_item=mbs_details,
            patient=patient_data
        )
        
        is_eligible = eligibility_result.get('eligible', False)
        errors = eligibility_result.get('errors', [])
        reason = '; '.join(errors) if errors else 'Eligible'
        
        # Step 3: Calculate rebate
        calculation_result = calculator.calculate_rebate(
            mbs_item=mbs_details,
            patient=patient_data,
            eligibility=eligibility_result
        )
        
        rebate_amount = calculation_result.get('rebate_amount', 0.0)
        gap_fee = calculation_result.get('gap_fee', 0.0)
        schedule_fee = calculation_result.get('schedule_fee', 0.0)
        
        # Step 4: Generate report (if requested)
        report_path = None
        if request.output_format:
            # Use fast generate_and_save for immediate file creation
            report_result = reporter.generate_and_save(
                mbs_item=mbs_details,
                patient=patient_data,
                eligibility=eligibility_result,
                calculation=calculation_result,
                format=request.output_format
            )
            report_path = report_result.get('file_path')
        
        processing_time = (time.time() - start_time) * 1000
        
        return RebateCheckResponse(
            eligible=is_eligible,
            rebate_amount=rebate_amount,
            gap_fee=gap_fee,
            schedule_fee=schedule_fee,
            mbs_item=request.mbs_item,
            description=mbs_details.get('description', ''),
            reason=reason,
            processing_time_ms=round(processing_time, 2),
            report_path=report_path
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/mbs-items/{item_number}", tags=["MBS"])
async def get_mbs_item(item_number: str):
    """Get details for a specific MBS item."""
    details = fetcher.fetch_mbs_item(item_number)
    if not details:
        raise HTTPException(
            status_code=404,
            detail=f"MBS item '{item_number}' not found"
        )
    return details


@app.get("/mbs-items", tags=["MBS"])
async def list_mbs_items(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in descriptions")
):
    """List MBS items, optionally filtered."""
    all_items = fetcher.get_all_items()
    items_list = list(all_items.values())
    
    if category:
        items_list = [item for item in items_list if item.get('category') == category]
    
    if search:
        search_lower = search.lower()
        items_list = [item for item in items_list if search_lower in item.get('description', '').lower()]
    
    return {
        "count": len(items_list),
        "items": items_list
    }


@app.get("/reports/{filename}", tags=["Reports"])
async def download_report(filename: str):
    """Download a generated report file."""
    file_path = REPORTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Report '{filename}' not found"
        )
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='text/plain' if filename.endswith('.md') else 'application/json'
    )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def server_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)