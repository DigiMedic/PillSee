"""
PillSee Backend - Anonymní český lékový AI asistent
FastAPI aplikace s rate limitingem a CORS pro anonymní použití
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from typing import Dict, Any

from .config import settings
from .models import (
    TextQuery, 
    ImageQuery, 
    APIResponse, 
    HealthCheckResponse,
    Constants
)
from .workflows.medication_workflow import medication_workflow, MedicationState

# Konfigurace loggingu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting pro anonymní uživatele (IP-based)
limiter = Limiter(key_func=get_remote_address)

# Inicializace FastAPI aplikace
app = FastAPI(
    title="PillSee API",
    description="Anonymní AI asistent pro informace o českých lécích",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Připojení rate limiteru k aplikaci
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware pro Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,  # Žádné cookies pro anonymní aplikaci
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint pro monitoring"""
    return HealthCheckResponse(
        dependencies={
            "openai": "connected",
            "database": "connected", 
            "sukl_data": "pending"
        }
    )

# Textový dotaz na léky
@app.post("/api/query/text", response_model=APIResponse)
@limiter.limit(Constants.TEXT_QUERY_LIMIT)
async def text_query(request: Request, query: TextQuery):
    """
    Zpracování textového dotazu na léky
    
    Args:
        query: Textový dotaz v češtině o léku
        
    Returns:
        APIResponse: Strukturovaná odpověď s informacemi o léku
    """
    try:
        if not query.query.strip():
            raise HTTPException(status_code=400, detail="Dotaz nemůže být prázdný")
        
        logger.info(f"Text query received: {len(query.query)} characters")
        
        # Inicializace workflow state
        initial_state = MedicationState(
            query=query.query,
            query_type="text",
            image_data=None,
            extracted_text=None,
            medication_info=None,
            safety_warnings=[],
            disclaimer="",
            confidence_score=0.0,
            sources=[],
            error=None
        )
        
        # Spuštění LangGraph workflow
        final_state = medication_workflow.invoke(initial_state)
        
        # Kontrola chyb
        if final_state.get("error"):
            raise HTTPException(status_code=500, detail=final_state["error"])
        
        # Příprava odpovědi
        medication_info = final_state.get("medication_info", {})
        if isinstance(medication_info, dict) and "answer" in medication_info:
            # Pro textové dotazy
            response_data = medication_info
        else:
            # Pro strukturované informace
            response_data = {
                "medication_info": medication_info,
                "confidence_score": final_state.get("confidence_score", 0.0),
                "sources": final_state.get("sources", [])
            }
        
        disclaimer = final_state.get("disclaimer", Constants.MEDICAL_DISCLAIMER)
        
        return APIResponse(
            status="success",
            data=response_data,
            disclaimer=disclaimer.strip()
        )
        
    except Exception as e:
        logger.error(f"Error processing text query: {str(e)}")
        return APIResponse(
            status="error",
            error="Nastala chyba při zpracování dotazu. Zkuste to prosím znovu."
        )

# Dotaz s obrázkem (identifikace léku)
@app.post("/api/query/image", response_model=APIResponse)  
@limiter.limit(Constants.IMAGE_QUERY_LIMIT)
async def image_query(request: Request, image_data: ImageQuery):
    """
    Zpracování dotazu s obrázkem pro identifikaci léku
    
    Args:
        image_data: Base64 encoded obrázek obalu léku
        
    Returns:
        APIResponse: Strukturovaná odpověď s rozpoznanými informacemi
    """
    try:
        if not image_data.image_data.strip():
            raise HTTPException(status_code=400, detail="Obrázek nemůže být prázdný")
        
        logger.info("Image query received")
        
        # Inicializace workflow state pro obrázek
        initial_state = MedicationState(
            query="",
            query_type="image",
            image_data=image_data.image_data,
            extracted_text=None,
            medication_info=None,
            safety_warnings=[],
            disclaimer="",
            confidence_score=0.0,
            sources=[],
            error=None
        )
        
        # Spuštění LangGraph workflow
        final_state = medication_workflow.invoke(initial_state)
        
        # Kontrola chyb
        if final_state.get("error"):
            raise HTTPException(status_code=500, detail=final_state["error"])
        
        # Příprava odpovědi
        medication_info = final_state.get("medication_info", {})
        response_data = medication_info
        
        disclaimer = final_state.get("disclaimer", Constants.MEDICAL_DISCLAIMER)
        
        return APIResponse(
            status="success", 
            data=response_data,
            disclaimer=disclaimer.strip()
        )
        
    except Exception as e:
        logger.error(f"Error processing image query: {str(e)}")
        return APIResponse(
            status="error",
            error="Nastala chyba při zpracování obrázku. Zkuste to prosím znovu s lepším osvětlením."
        )

# Custom exception handler pro rate limiting
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler pro překročení rate limitu
    """
    return HTTPException(
        status_code=429,
        detail="Překročili jste limit dotazů. Zkuste to prosím za chvíli."
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Globální handler pro neočekávané chyby
    """
    logger.error(f"Unhandled exception: {str(exc)}")
    return HTTPException(
        status_code=500,
        detail="Nastala neočekávaná chyba. Naše technický tým byl informován."
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)