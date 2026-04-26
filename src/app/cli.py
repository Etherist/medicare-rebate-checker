"""
Command-Line Interface for Medicare Rebate Eligibility Checker.
Provides a simple terminal-based interface for checking rebates.
"""
import argparse
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from agents.mbs_fetcher import MBSDataFetcher
from agents.validator import EligibilityValidator
from agents.calculator import RebateCalculator
from agents.reporter import ReportGenerator


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Medicare Rebate Eligibility Checker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --mbs-item 13200 --age 35 --has-medicare-card True
  %(prog)s --mbs-item 23 --age 70 --has-medicare-card True --concession-status True
        """
    )
    
    parser.add_argument(
        '--mbs-item',
        type=str,
        required=True,
        help='MBS item number (e.g., 13200, 23)'
    )
    parser.add_argument(
        '--age',
        type=int,
        required=True,
        help='Patient age in years'
    )
    parser.add_argument(
        '--has-medicare-card',
        type=str,
        required=True,
        choices=['True', 'true', 'False', 'false', 'yes', 'no'],
        help='Whether patient has a valid Medicare card'
    )
    parser.add_argument(
        '--concession-status',
        type=str,
        default='False',
        choices=['True', 'true', 'False', 'false', 'yes', 'no'],
        help='Patient concession status (e.g., pensioner)'
    )
    parser.add_argument(
        '--hospital-status',
        type=str,
        default='False',
        choices=['True', 'true', 'False', 'false', 'yes', 'no'],
        help='Whether patient is admitted to hospital'
    )
    parser.add_argument(
        '--has-referral',
        type=str,
        default='False',
        choices=['True', 'true', 'False', 'false', 'yes', 'no'],
        help='Whether patient has a referral (if required)'
    )
    parser.add_argument(
        '--output-format',
        type=str,
        default='markdown',
        choices=['markdown', 'json', 'html'],
        help='Report output format'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='reports',
        help='Directory to save reports'
    )
    
    args = parser.parse_args()
    
    # Convert string boolean values to actual booleans
    has_medicare = args.has_medicare_card.lower() in ('true', 'yes')
    concession = args.concession_status.lower() in ('true', 'yes')
    hospital = args.hospital_status.lower() in ('true', 'yes')
    has_referral = args.has_referral.lower() in ('true', 'yes')
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    try:
        # Initialize agents
        fetcher = MBSDataFetcher()
        validator = EligibilityValidator()
        calculator = RebateCalculator()
        reporter = ReportGenerator(output_dir=args.output_dir)
        
        print(f"🔍 Processing MBS Item: {args.mbs_item}")
        print(f"   Patient Age: {args.age}")
        print(f"   Medicare Card: {has_medicare}")
        print()
        
        # Step 1: Fetch MBS item details
        print("📦 Fetching MBS item details...")
        mbs_details = fetcher.fetch_mbs_item(args.mbs_item)
        if not mbs_details:
            print(f"❌ MBS item '{args.mbs_item}' not found.")
            sys.exit(1)
        print(f"   Found: {mbs_details.get('description', 'Unknown')}")
        print(f"   Schedule Fee: ${mbs_details.get('schedule_fee', 0):.2f}")
        print()
        
        # Step 2: Validate eligibility
        print("✅ Validating eligibility...")
        patient_data = {
            'age': args.age,
            'has_medicare_card': has_medicare,
            'concession_status': concession,
            'hospital_status': hospital,
            'has_referral': has_referral
        }
        
        eligibility_result = validator.validate_eligibility(
            mbs_item=mbs_details,
            patient=patient_data
        )
        
        is_eligible = eligibility_result.get('eligible', False)
        reasons = eligibility_result.get('reasons', [])
        errors = eligibility_result.get('errors', [])
        
        print(f"   Result: {'Eligible' if is_eligible else 'Not Eligible'}")
        if errors:
            for error in errors:
                print(f"   Error: {error}")
        print()
        
        # Step 3: Calculate rebate
        print("💰 Calculating rebate and gap fee...")
        calculation_result = calculator.calculate_rebate(
            mbs_item=mbs_details,
            patient=patient_data,
            eligibility=eligibility_result
        )
        
        rebate_amount = calculation_result.get('rebate_amount', 0.0)
        gap_fee = calculation_result.get('gap_fee', 0.0)
        schedule_fee = calculation_result.get('schedule_fee', mbs_details.get('schedule_fee', 0.0))
        
        print(f"   Rebate Amount: ${rebate_amount:.2f}")
        print(f"   Gap Fee: ${gap_fee:.2f}")
        print()
        
        # Step 4: Generate report
        print("📄 Generating report...")
        
        # The generate_and_save method expects specific parameters
        report_result = reporter.generate_and_save(
            mbs_item=mbs_details,
            patient=patient_data,
            eligibility=eligibility_result,
            calculation=calculation_result,
            format=args.output_format
        )
        
        report_path = report_result.get('file_path', '')
        print(f"   Report saved to: {report_path}")
        print()
        
        # Summary
        print("=" * 50)
        print("✅ Process completed successfully!")
        print(f"   MBS Item: {args.mbs_item}")
        print(f"   Eligible: {'Yes' if is_eligible else 'No'}")
        print(f"   Rebate: ${rebate_amount:.2f}")
        print(f"   Gap Fee: ${gap_fee:.2f}")
        print(f"   Report: {report_path}")
        
    except KeyboardInterrupt:
        print("\n❌ Process interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()