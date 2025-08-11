"""
Tests for PillSee API endpoints
"""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    def test_health_check_success(self, client):
        """Test successful health check"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "PillSee API"
        assert data["version"] == "1.0.0"


class TestTextQueryEndpoint:
    """Tests for text query endpoint"""
    
    def test_text_query_success(self, client, mock_supabase):
        """Test successful text query"""
        with patch('app.workflows.medication_workflow.medication_workflow') as mock_workflow:
            # Mock workflow response
            mock_workflow.invoke.return_value = {
                "medication_info": {
                    "answer": "PARALEN 500MG je analgetikum s paracetamolem.",
                    "sources": ["SÚKL databáze"]
                },
                "disclaimer": "Lékařské upozornění",
                "confidence_score": 0.9
            }
            
            response = client.post(
                "/api/query/text",
                json={"query": "Co je to Paralen?"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "success"
            assert "answer" in data["data"]
            assert data["disclaimer"]
    
    def test_text_query_empty(self, client):
        """Test text query with empty string"""
        response = client.post(
            "/api/query/text",
            json={"query": ""}
        )
        assert response.status_code == 400
    
    def test_text_query_too_long(self, client):
        """Test text query that's too long"""
        long_query = "a" * 1000
        response = client.post(
            "/api/query/text", 
            json={"query": long_query}
        )
        # Should be handled by Pydantic validation
        assert response.status_code == 422
    
    def test_text_query_rate_limit(self, client):
        """Test rate limiting on text queries"""
        # Mock successful workflow
        with patch('app.workflows.medication_workflow.medication_workflow') as mock_workflow:
            mock_workflow.invoke.return_value = {
                "medication_info": {"answer": "test"},
                "disclaimer": "test"
            }
            
            # Send many requests quickly 
            for i in range(12):  # More than 10/minute limit
                response = client.post(
                    "/api/query/text",
                    json={"query": f"test query {i}"}
                )
                
                if i < 10:
                    assert response.status_code == 200
                else:
                    assert response.status_code == 429  # Rate limited


class TestImageQueryEndpoint:
    """Tests for image query endpoint"""
    
    def test_image_query_success(self, client, base64_test_image, mock_supabase):
        """Test successful image query"""
        with patch('app.workflows.medication_workflow.medication_workflow') as mock_workflow:
            mock_workflow.invoke.return_value = {
                "medication_info": {
                    "name": "PARALEN 500MG",
                    "active_ingredient": "Paracetamolum",
                    "confidence_score": 0.85
                },
                "disclaimer": "Lékařské upozornění"
            }
            
            response = client.post(
                "/api/query/image",
                json={"image_data": base64_test_image}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "success"
            assert "name" in data["data"]
            assert data["disclaimer"]
    
    def test_image_query_empty(self, client):
        """Test image query with empty data"""
        response = client.post(
            "/api/query/image",
            json={"image_data": ""}
        )
        assert response.status_code == 400
    
    def test_image_query_invalid_base64(self, client):
        """Test image query with invalid base64"""
        response = client.post(
            "/api/query/image",
            json={"image_data": "invalid_base64"}
        )
        # Should be caught by Pydantic validation or workflow
        assert response.status_code in [400, 422, 500]
    
    def test_image_query_rate_limit(self, client, base64_test_image):
        """Test rate limiting on image queries (5/minute)"""
        with patch('app.workflows.medication_workflow.medication_workflow') as mock_workflow:
            mock_workflow.invoke.return_value = {
                "medication_info": {"name": "test"},
                "disclaimer": "test"
            }
            
            # Send more than 5 requests
            for i in range(7):
                response = client.post(
                    "/api/query/image",
                    json={"image_data": base64_test_image}
                )
                
                if i < 5:
                    assert response.status_code == 200
                else:
                    assert response.status_code == 429


class TestCORSHeaders:
    """Tests for CORS configuration"""
    
    def test_cors_headers_present(self, client):
        """Test CORS headers are properly set"""
        response = client.options(
            "/api/query/text",
            headers={"Origin": "http://localhost:3000"}
        )
        
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
    
    def test_cors_allowed_origins(self, client):
        """Test that allowed origins work"""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert response.status_code == 200
        # Should not block allowed origin


class TestErrorHandling:
    """Tests for error handling"""
    
    def test_workflow_error_handling(self, client):
        """Test error handling when workflow fails"""
        with patch('app.workflows.medication_workflow.medication_workflow') as mock_workflow:
            # Mock workflow to raise exception
            mock_workflow.invoke.side_effect = Exception("Database connection failed")
            
            response = client.post(
                "/api/query/text",
                json={"query": "test"}
            )
            
            assert response.status_code == 500
            data = response.json()
            assert data["status"] == "error"
    
    def test_invalid_json_handling(self, client):
        """Test handling of invalid JSON"""
        response = client.post(
            "/api/query/text",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_missing_fields_handling(self, client):
        """Test handling of missing required fields"""
        response = client.post(
            "/api/query/text",
            json={}  # Missing 'query' field
        )
        
        assert response.status_code == 422  # Validation error


class TestSecurityHeaders:
    """Tests for security headers and configurations"""
    
    def test_no_credentials_allowed(self, client):
        """Test that credentials are not allowed (anonymous app)"""
        response = client.get("/health")
        
        # Should not have any authentication-related headers
        assert "set-cookie" not in response.headers.keys()
        assert "authorization" not in response.headers.keys()
    
    def test_content_type_validation(self, client):
        """Test content type validation"""
        response = client.post(
            "/api/query/text",
            data="query=test",  # Form data instead of JSON
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Should expect JSON
        assert response.status_code in [422, 415]


class TestCzechMedicalScenarios:
    """Tests specific to Czech medication scenarios"""
    
    def test_czech_medication_names(self, client):
        """Test with real Czech medication names"""
        with patch('app.workflows.medication_workflow.medication_workflow') as mock_workflow:
            mock_workflow.invoke.return_value = {
                "medication_info": {
                    "answer": "PARALEN je paracetamol pro tlumení bolesti."
                },
                "disclaimer": "Lékařské upozornění"
            }
            
            czech_queries = [
                "Co je to Paralen?",
                "Brufen 400 mg účinky",
                "Aspirin kontraindikace",
                "Ibuprofen dávkování"
            ]
            
            for query in czech_queries:
                response = client.post(
                    "/api/query/text",
                    json={"query": query}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "success"
    
    def test_medical_disclaimer_present(self, client):
        """Test that medical disclaimers are always present"""
        with patch('app.workflows.medication_workflow.medication_workflow') as mock_workflow:
            mock_workflow.invoke.return_value = {
                "medication_info": {"answer": "test"},
                "disclaimer": "UPOZORNĚNÍ: Informace nenahrazují lékařskou radu"
            }
            
            response = client.post(
                "/api/query/text",
                json={"query": "test"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Disclaimer must be present and non-empty
            assert data["disclaimer"]
            assert "UPOZORNĚNÍ" in data["disclaimer"] or "upozornění" in data["disclaimer"]