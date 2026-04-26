"""
Test suite for Medicare Rebate Eligibility Checker application interfaces.
Tests CLI, Streamlit app, and FastAPI endpoints.
"""
import json
import os
import sys
import tempfile
import unittest
from io import BytesIO
from unittest.mock import patch, MagicMock, mock_open

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import app modules
from app.cli import main as cli_main
from app.main import app as fastapi_app


class TestCLIInterface(unittest.TestCase):
    """Test cases for Command Line Interface."""
    
    def test_cli_help(self):
        """Test that CLI can be invoked."""
        # The CLI entry point should be callable
        assert callable(cli_main)
        
    def test_cli_invalid_mbs_item(self):
        """Test CLI with invalid MBS item format."""
        original_argv = sys.argv
        try:
            sys.argv = ['cli.py', '--mbs-item', 'ABC', '--age', '35', '--has-medicare-card', 'True']
            cli_main()
        except SystemExit:
            pass  # Expected exit on error
        except Exception as e:
            self.fail(f"CLI raised unexpected exception: {e}")
        finally:
            sys.argv = original_argv


class TestFastAPIInterface(unittest.TestCase):
    """Test cases for FastAPI REST API interface."""
    
    def setUp(self):
        """Set up test client."""
        self.client = TestClient(fastapi_app)
        
    def test_fastapi_app_creation(self):
        """Test that FastAPI app is created successfully."""
        assert fastapi_app is not None
        assert hasattr(fastapi_app, 'routes')
        
    def test_root_endpoint(self):
        """Test root endpoint returns API info."""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        self.assertIn('name', data)
        self.assertIn('version', data)
        
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        
    def test_api_docs_endpoint(self):
        """Test that API documentation endpoint is accessible."""
        response = self.client.get("/docs")
        assert response.status_code == 200
        
    def test_openapi_json_endpoint(self):
        """Test OpenAPI JSON endpoint."""
        response = self.client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        
    @patch('app.main.fetcher')
    @patch('app.main.eligibility_validator')
    @patch('app.main.calculator')
    @patch('app.main.reporter')
    def test_check_rebate_endpoint_success(self, mock_reporter, mock_calculator, mock_validator, mock_fetcher):
        """Test the rebate check endpoint with valid data."""
        # Setup mocks
        mock_fetcher.fetch_mbs_item.return_value = {
            'item_number': '0023',
            'description': 'General consultation',
            'schedule_fee': 100.0,
            'rebate_percentage': 85.0,
            'rules': {}
        }
        
        mock_validator.validate_eligibility.return_value = {
            'eligible': True,
            'reasons': [],
            'errors': []
        }
        
        mock_calculator.calculate_rebate.return_value = {
            'schedule_fee': 100.0,
            'rebate_amount': 85.0,
            'gap_fee': 15.0,
            'rebate_percentage': 85
        }
        
        mock_reporter.generate_and_save.return_value = {
            'file_path': '/tmp/test_report.md'
        }
        
        response = self.client.post("/check-rebate", json={
            "mbs_item": "0023",
            "age": 35,
            "has_medicare_card": True,
            "concession_status": False,
            "hospital_status": False,
            "has_referral": False
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["eligible"] == True
        assert data["rebate_amount"] == 85.0
        assert data["gap_fee"] == 15.0
        assert "report_path" in data
        
    def test_check_rebate_endpoint_invalid_mbs_item(self):
        """Test rebate check endpoint with non-existent MBS item."""
        response = self.client.post("/check-rebate", json={
            "mbs_item": "99999",
            "age": 35,
            "has_medicare_card": True,
            "concession_status": False,
            "hospital_status": False
        })
        # Should return 404 for not found
        assert response.status_code == 404
        
    def test_check_rebate_endpoint_invalid_input(self):
        """Test rebate check endpoint with invalid input (missing required fields)."""
        response = self.client.post("/check-rebate", json={
            "mbs_item": "0023"
            # Missing age, has_medicare_card
        })
        # Should return validation error
        assert response.status_code == 422
        
    def test_get_mbs_item_endpoint(self):
        """Test getting a specific MBS item."""
        response = self.client.get("/mbs-items/0023")
        assert response.status_code == 200
        data = response.json()
        self.assertIn('item_number', data)
        
    def test_list_mbs_items_endpoint(self):
        """Test listing MBS items."""
        response = self.client.get("/mbs-items")
        assert response.status_code == 200
        data = response.json()
        self.assertIn('count', data)
        self.assertIn('items', data)
        self.assertGreater(data['count'], 0)
        
    def test_filter_mbs_items_by_category(self):
        """Test filtering MBS items by category."""
        response = self.client.get("/mbs-items?category=general_practice")
        assert response.status_code == 200
        data = response.json()
        for item in data['items']:
            if item.get('category'):
                assert item['category'] == 'general_practice'


class TestStreamlitInterface(unittest.TestCase):
    """Test cases for Streamlit interface."""
    
    def test_streamlit_app_import(self):
        """Test that Streamlit app can be imported."""
        try:
            import app.streamlit_app as streamlit_app
            assert hasattr(streamlit_app, 'main')
        except ImportError:
            pytest.skip("Streamlit not available in test environment")
            
    def test_streamlit_file_exists(self):
        """Test that Streamlit app file exists."""
        streamlit_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'app', 'streamlit_app.py')
        assert os.path.exists(streamlit_path)
        assert os.path.isfile(streamlit_path)


class TestApplicationIntegration(unittest.TestCase):
    """Integration tests for the application."""
    
    def test_agent_imports_in_app(self):
        """Test that agents can be imported by app modules."""
        try:
            from agents import mbs_fetcher
            from agents import validator
            from agents import calculator
            from agents import reporter
            assert all([mbs_fetcher, validator, calculator, reporter])
        except ImportError as e:
            self.fail(f"Failed to import agents: {e}")
            
    def test_app_modules_import(self):
        """Test that all app modules can be imported."""
        try:
            from app import cli
            from app import main
            assert hasattr(cli, 'main')
            assert hasattr(main, 'app')
        except ImportError as e:
            self.fail(f"Failed to import app modules: {e}")
            
    def test_fastapi_client_creation(self):
        """Test that FastAPI test client can be created."""
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        assert client is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])