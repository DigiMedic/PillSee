"""
Pytest configuration and fixtures
"""

import pytest
import tempfile
import os
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.models import MedicationInfo

@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    with patch('app.ai.vision_processor.OpenAI') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        
        # Mock vision response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"name": "PARALEN 500MG", "active_ingredient": "Paracetamolum", "confidence_score": 0.9}'
        mock_instance.chat.completions.create.return_value = mock_response
        
        yield mock_instance

@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing"""
    with patch('app.database.vector_store.create_client') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def sample_medication():
    """Sample medication info for testing"""
    return MedicationInfo(
        name="PARALEN 500MG",
        active_ingredient="Paracetamolum", 
        strength="500 mg",
        form="Potahované tablety",
        manufacturer="Zentiva, k.s.",
        indication="Mírná až středně silná bolest, horečka"
    )

@pytest.fixture
def sample_sukl_csv():
    """Create temporary SÚKL CSV file for testing"""
    csv_content = """NAZEV,UCINNE_LATKY,SILA,LEKOVA_FORMA,DRZITEL_ROZHODNUTI,REGISTRACNI_CISLO
PARALEN 500MG,Paracetamolum,500 mg,Potahované tablety,Zentiva k.s.,16/123/69-C
BRUFEN 400MG,Ibuprofenum,400 mg,Potahované tablety,Mylan Ireland Limited,83/456/92-C"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='windows-1250') as f:
        f.write(csv_content)
        f.flush()
        
        yield f.name
        
    # Cleanup
    os.unlink(f.name)

@pytest.fixture
def base64_test_image():
    """Base64 encoded test image"""
    # Minimal valid JPEG header in base64
    return "/9j/4AAQSkZJRgABAQEAAAAAAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/wA=="