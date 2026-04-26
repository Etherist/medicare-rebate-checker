"""
Comprehensive test suite for Medicare Rebate Eligibility Checker agents.
Tests all four autonomous agents: MBSDataFetcher, EligibilityValidator, RebateCalculator, ReportGenerator.
"""
import json
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.mbs_fetcher import MBSDataFetcher
from agents.validator import EligibilityValidator
from agents.calculator import RebateCalculator
from agents.reporter import ReportGenerator


class TestMBSDataFetcher(unittest.TestCase):
    """Test cases for MBSDataFetcher agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fetcher = MBSDataFetcher()
        
    def test_initialization(self):
        """Test that MBSDataFetcher initializes correctly."""
        self.assertIsInstance(self.fetcher, MBSDataFetcher)
        self.assertIsNotNone(self.fetcher.data_path)
        
    def test_fetch_mbs_item_success(self):
        """Test successful fetch of an MBS item."""
        # Test with a known item
        result = self.fetcher.fetch_mbs_item('0023')
        self.assertIsNotNone(result)
        self.assertIn('item_number', result)
        self.assertEqual(result['item_number'], '0023')
        self.assertIn('description', result)
        self.assertIn('schedule_fee', result)
        
    def test_fetch_mbs_item_not_found(self):
        """Test fetching a non-existent MBS item."""
        result = self.fetcher.fetch_mbs_item('99999')
        self.assertIsNone(result)
        
    def test_fetch_mbs_item_invalid_format(self):
        """Test fetching with invalid item number format."""
        with self.assertRaises(ValueError):
            self.fetcher.fetch_mbs_item('ABC')
            
        with self.assertRaises(ValueError):
            self.fetcher.fetch_mbs_item('123')  # Too short
            
    def test_get_all_items(self):
        """Test retrieving all MBS items."""
        all_items = self.fetcher.get_all_items()
        self.assertIsInstance(all_items, dict)
        self.assertGreater(len(all_items), 0)
        # Check structure of first item
        first_item = next(iter(all_items.values()))
        self.assertIn('item_number', first_item)
        self.assertIn('description', first_item)
        
    def test_clear_cache(self):
        """Test cache clearing."""
        # Fetch an item to populate cache
        self.fetcher.fetch_mbs_item('0023')
        cache_info_before = self.fetcher.get_cache_info()
        self.assertGreater(cache_info_before['cached_items'], 0)
        
        # Clear cache
        self.fetcher.clear_cache()
        cache_info_after = self.fetcher.get_cache_info()
        self.assertEqual(cache_info_after['cached_items'], 0)


class TestEligibilityValidator(unittest.TestCase):
    """Test cases for EligibilityValidator agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = EligibilityValidator()
        
    def test_initialization(self):
        """Test that EligibilityValidator initializes correctly."""
        self.assertIsInstance(self.validator, EligibilityValidator)
        self.assertEqual(self.validator.validation_count, 0)
        
    def test_validate_eligibility_eligible(self):
        """Test eligibility validation for eligible patient."""
        mbs_item = {
            'item_number': '0023',
            'description': 'General consultation',
            'rules': {
                'medicare_card_required': True
            }
        }
        patient = {
            'age': 35,
            'has_medicare_card': True,
            'concession_status': False,
            'hospital_status': False,
            'has_referral': False
        }
        
        result = self.validator.validate_eligibility(mbs_item, patient)
        self.assertIsInstance(result, dict)
        self.assertIn('eligible', result)
        self.assertTrue(result['eligible'])
        self.assertIn('reasons', result)
        self.assertIn('errors', result)
        
    def test_validate_eligibility_no_medicare(self):
        """Test eligibility validation for patient without Medicare card."""
        mbs_item = {
            'item_number': '0023',
            'rules': {
                'medicare_card_required': True
            }
        }
        patient = {
            'age': 35,
            'has_medicare_card': False
        }
        
        result = self.validator.validate_eligibility(mbs_item, patient)
        self.assertFalse(result['eligible'])
        errors = result.get('errors', [])
        self.assertTrue(any('medicare' in e.lower() for e in errors))
        
    def test_validate_eligibility_age_restriction(self):
        """Test eligibility validation with age restrictions."""
        # Test with age restriction "70+"
        mbs_item = {
            'item_number': '7070',
            'rules': {
                'age_restriction': '70+'
            }
        }
        
        # Patient below age limit
        patient = {'age': 65, 'has_medicare_card': True}
        result = self.validator.validate_eligibility(mbs_item, patient)
        self.assertFalse(result['eligible'])
        
        # Patient at or above age limit
        patient = {'age': 70, 'has_medicare_card': True}
        result = self.validator.validate_eligibility(mbs_item, patient)
        self.assertTrue(result['eligible'])
        
    def test_validate_eligibility_age_range(self):
        """Test eligibility validation with age range."""
        mbs_item = {
            'item_number': '45-49',
            'rules': {
                'age_restriction': '45-49'
            }
        }
        
        # Within range
        patient = {'age': 47, 'has_medicare_card': True}
        result = self.validator.validate_eligibility(mbs_item, patient)
        self.assertTrue(result['eligible'])
        
        # Below range
        patient = {'age': 44, 'has_medicare_card': True}
        result = self.validator.validate_eligibility(mbs_item, patient)
        self.assertFalse(result['eligible'])
        
    def test_validate_eligibility_referral_required(self):
        """Test eligibility with referral requirement."""
        mbs_item = {
            'item_number': 'REF001',
            'rules': {
                'requires_referral': True
            }
        }
        
        # No referral provided
        patient = {'age': 35, 'has_medicare_card': True, 'has_referral': False}
        result = self.validator.validate_eligibility(mbs_item, patient)
        self.assertFalse(result['eligible'])
        
        # Referral provided
        patient = {'age': 35, 'has_medicare_card': True, 'has_referral': True}
        result = self.validator.validate_eligibility(mbs_item, patient)
        self.assertTrue(result['eligible'])
        
    def test_validate_invalid_inputs(self):
        """Test validation with invalid input data."""
        # Invalid mbs_item (not a dict) - validator should return errors, not raise
        result = self.validator.validate_eligibility("not a dict", {'age': 35})
        self.assertFalse(result['eligible'])
        self.assertIn('errors', result)
        self.assertTrue(len(result['errors']) > 0)
        
        # Missing required fields (e.g., missing rules)
        mbs_item = {'item_number': '123'}  # Missing rules
        patient = {'age': 35}
        result = self.validator.validate_eligibility(mbs_item, patient)
        # Should have errors and be not eligible
        self.assertFalse(result['eligible'])
        self.assertIn('errors', result)
        
    def test_get_statistics(self):
        """Test getting validator statistics."""
        stats = self.validator.get_statistics()
        self.assertIn('total_validations', stats)


class TestRebateCalculator(unittest.TestCase):
    """Test cases for RebateCalculator agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = RebateCalculator()
        
    def test_initialization(self):
        """Test that RebateCalculator initializes correctly."""
        self.assertIsInstance(self.calculator, RebateCalculator)
        self.assertEqual(self.calculator.calculation_count, 0)
        
    def test_calculate_rebate_basic(self):
        """Test basic rebate calculation."""
        mbs_item = {
            'item_number': '0023',
            'description': 'Consultation',
            'schedule_fee': 100.0,
            'rebate_percentage': 85.0
        }
        patient = {'age': 35}
        eligibility = {'eligible': True}
        
        result = self.calculator.calculate_rebate(mbs_item, patient, eligibility)
        
        self.assertIsInstance(result, dict)
        self.assertIn('rebate_amount', result)
        self.assertAlmostEqual(result['rebate_amount'], 85.0, places=2)
        self.assertIn('gap_fee', result)
        self.assertAlmostEqual(result['gap_fee'], 15.0, places=2)
        self.assertIn('schedule_fee', result)
        self.assertEqual(result['schedule_fee'], 100.0)
        
    def test_calculate_rebate_from_rules(self):
        """Test rebate calculation with percentage from rules."""
        mbs_item = {
            'item_number': '0023',
            'schedule_fee': 50.0,
            'rules': {
                'rebate_percentage': 75.0
            }
        }
        patient = {}
        eligibility = {'eligible': True}
        
        result = self.calculator.calculate_rebate(mbs_item, patient, eligibility)
        self.assertAlmostEqual(result['rebate_amount'], 37.5, places=2)
        self.assertAlmostEqual(result['gap_fee'], 12.5, places=2)
        
    def test_calculate_rebate_ineligible(self):
        """Test rebate calculation for ineligible patient."""
        mbs_item = {
            'item_number': '0023',
            'schedule_fee': 100.0,
            'rebate_percentage': 85.0
        }
        patient = {}
        eligibility = {'eligible': False}
        
        result = self.calculator.calculate_rebate(mbs_item, patient, eligibility)
        self.assertEqual(result['rebate_amount'], 0.0)
        self.assertEqual(result['gap_fee'], 100.0)
        
    def test_calculate_rebate_after_hours_multiplier(self):
        """Test rebate calculation with after-hours multiplier."""
        mbs_item = {
            'item_number': '0023',
            'schedule_fee': 100.0,
            'rebate_percentage': 85.0,
            'rules': {
                'after_hours_multiplier': 1.5
            }
        }
        patient = {}
        eligibility = {'eligible': True}
        
        result = self.calculator.calculate_rebate(mbs_item, patient, eligibility)
        expected_fee = 150.0  # 100 * 1.5
        expected_rebate = expected_fee * 0.85
        expected_gap = expected_fee - expected_rebate
        
        self.assertAlmostEqual(result['schedule_fee'], expected_fee, places=2)
        self.assertAlmostEqual(result['rebate_amount'], expected_rebate, places=2)
        self.assertAlmostEqual(result['gap_fee'], expected_gap, places=2)
        
    def test_calculate_multiple_items(self):
        """Test batch calculation for multiple items."""
        items_data = [
            {
                'mbs_item': {
                    'item_number': '001',
                    'schedule_fee': 100.0,
                    'rebate_percentage': 85.0
                },
                'patient': {},
                'eligibility': {'eligible': True}
            },
            {
                'mbs_item': {
                    'item_number': '002',
                    'schedule_fee': 50.0,
                    'rebate_percentage': 75.0
                },
                'patient': {},
                'eligibility': {'eligible': True}
            }
        ]
        
        result = self.calculator.calculate_multiple(items_data)
        self.assertIn('calculations', result)
        self.assertEqual(result['item_count'], 2)
        self.assertIn('summary', result)
        self.assertGreater(result['summary']['total_schedule_fee'], 0)
        
    def test_get_statistics(self):
        """Test getting calculator statistics."""
        stats = self.calculator.get_statistics()
        self.assertIn('total_calculations', stats)


class TestReportGenerator(unittest.TestCase):
    """Test cases for ReportGenerator agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.reporter = ReportGenerator(output_dir=self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_initialization(self):
        """Test that ReportGenerator initializes correctly."""
        self.assertIsInstance(self.reporter, ReportGenerator)
        self.assertEqual(str(self.reporter.output_dir), self.temp_dir)
        
    def test_generate_report_markdown(self):
        """Test generating a markdown report."""
        mbs_item = {
            'item_number': '0023',
            'description': 'General consultation',
            'category': 'general_practice'
        }
        patient = {
            'age': 35,
            'has_medicare_card': True
        }
        eligibility = {
            'eligible': True,
            'reasons': [],
            'errors': []
        }
        calculation = {
            'schedule_fee': 100.0,
            'rebate_amount': 85.0,
            'gap_fee': 15.0,
            'rebate_percentage': 85
        }
        
        # Use generate_and_save to actually create the file
        result = self.reporter.generate_and_save(
            mbs_item=mbs_item,
            patient=patient,
            eligibility=eligibility,
            calculation=calculation,
            format='markdown'
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('content', result)
        self.assertIn('file_path', result)
        self.assertTrue(os.path.exists(result['file_path']))
        
        # Check content
        with open(result['file_path'], 'r') as f:
            content = f.read()
            self.assertIn('Medicare Rebate', content)
            self.assertIn('0023', content)
            self.assertIn('General consultation', content)
            
    def test_generate_report_json(self):
        """Test generating a JSON report."""
        mbs_item = {'item_number': '0023', 'description': 'Test'}
        patient = {'age': 35}
        eligibility = {'eligible': True, 'reasons': [], 'errors': []}
        calculation = {
            'schedule_fee': 100.0,
            'rebate_amount': 85.0,
            'gap_fee': 15.0
        }
        
        result = self.reporter.generate_and_save(
            mbs_item=mbs_item,
            patient=patient,
            eligibility=eligibility,
            calculation=calculation,
            format='json'
        )
        
        self.assertIsInstance(result, dict)
        self.assertTrue(os.path.exists(result['file_path']))
        
        # Verify JSON is valid
        with open(result['file_path'], 'r') as f:
            data = json.load(f)
            self.assertEqual(data['mbs_item']['item_number'], '0023')
            
    def test_generate_report_invalid_format(self):
        """Test generating report with invalid format raises error."""
        mbs_item = {'item_number': '0023'}
        patient = {}
        eligibility = {}
        calculation = {}
        
        with self.assertRaises(ValueError):
            self.reporter.generate_report(
                mbs_item=mbs_item,
                patient=patient,
                eligibility=eligibility,
                calculation=calculation,
                format='invalid'
            )
            
    def test_generate_and_save(self):
        """Test generate_and_save convenience method."""
        mbs_item = {'item_number': '0023', 'description': 'Test'}
        patient = {'age': 35, 'has_medicare_card': True}
        eligibility = {'eligible': True, 'reasons': [], 'errors': []}
        calculation = {
            'schedule_fee': 100.0,
            'rebate_amount': 85.0,
            'gap_fee': 15.0
        }
        
        result = self.reporter.generate_and_save(
            mbs_item=mbs_item,
            patient=patient,
            eligibility=eligibility,
            calculation=calculation,
            format='markdown'
        )
        
        self.assertIn('file_path', result)
        self.assertTrue(os.path.exists(result['file_path']))
        
    def test_get_statistics(self):
        """Test getting reporter statistics."""
        stats = self.reporter.get_statistics()
        self.assertIn('total_reports', stats)
        self.assertIn('output_directory', stats)


class TestAgentIntegration(unittest.TestCase):
    """Integration tests for the agent workflow."""
    
    def setUp(self):
        """Set up test fixtures for integration testing."""
        self.fetcher = MBSDataFetcher()
        self.validator = EligibilityValidator()
        self.calculator = RebateCalculator()
        self.temp_dir = tempfile.mkdtemp()
        self.reporter = ReportGenerator(output_dir=self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_full_workflow_eligible_patient(self):
        """Test complete workflow for an eligible patient."""
        # Step 1: Fetch MBS item details (use 13200 - no age restriction)
        mbs_details = self.fetcher.fetch_mbs_item('13200')
        self.assertIsNotNone(mbs_details)
        
        # Step 2: Validate eligibility
        patient_data = {
            'age': 35,
            'has_medicare_card': True,
            'concession_status': False,
            'hospital_status': False,
            'has_referral': False
        }
        
        eligibility = self.validator.validate_eligibility(mbs_details, patient_data)
        self.assertIsInstance(eligibility, dict)
        self.assertTrue(eligibility.get('eligible', False))
        
        # Step 3: Calculate rebate
        calculation = self.calculator.calculate_rebate(
            mbs_item=mbs_details,
            patient=patient_data,
            eligibility=eligibility
        )
        
        self.assertGreater(calculation.get('rebate_amount', 0), 0)
        self.assertGreaterEqual(calculation.get('gap_fee', 0), 0)
        
        # Step 4: Generate report
        report = self.reporter.generate_and_save(
            mbs_item=mbs_details,
            patient=patient_data,
            eligibility=eligibility,
            calculation=calculation,
            format='markdown'
        )
        
        self.assertTrue(os.path.exists(report['file_path']))
        
    def test_full_workflow_ineligible_patient(self):
        """Test complete workflow for an ineligible patient."""
        # Step 1: Fetch MBS item
        mbs_details = self.fetcher.fetch_mbs_item('0023')
        self.assertIsNotNone(mbs_details)
        
        # Step 2: Validate eligibility (ineligible: no medicare)
        patient_data = {
            'age': 35,
            'has_medicare_card': False,
            'concession_status': False,
            'hospital_status': False
        }
        
        eligibility = self.validator.validate_eligibility(mbs_details, patient_data)
        self.assertFalse(eligibility.get('eligible', True))
        
        # Step 3: Calculate rebate (should be 0)
        calculation = self.calculator.calculate_rebate(
            mbs_item=mbs_details,
            patient=patient_data,
            eligibility=eligibility
        )
        
        self.assertEqual(calculation.get('rebate_amount', -1), 0.0)
        self.assertEqual(calculation.get('gap_fee', -1), mbs_details.get('schedule_fee', 0))
        
        # Step 4: Generate report
        report = self.reporter.generate_and_save(
            mbs_item=mbs_details,
            patient=patient_data,
            eligibility=eligibility,
            calculation=calculation,
            format='markdown'
        )
        
        self.assertTrue(os.path.exists(report['file_path']))


if __name__ == '__main__':
    unittest.main()