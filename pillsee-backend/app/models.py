"""
Pydantic modely pro PillSee API
Definice datových struktur pro request/response a interní zpracování
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional
from datetime import datetime

class TextQuery(BaseModel):
    """Model pro textový dotaz na lék"""
    query: str = Field(..., min_length=1, max_length=500, description="Textový dotaz v češtině")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Dotaz nemůže být prázdný')
        return v.strip()

class ImageQuery(BaseModel):
    """Model pro dotaz s obrázkem léku"""
    image_data: str = Field(..., description="Base64 encoded obrázek obalu léku")
    
    @validator('image_data')
    def validate_image_data(cls, v):
        if not v.strip():
            raise ValueError('Obrázek nemůže být prázdný')
        # Základní validace base64 formátu
        if not v.startswith(('data:image', '/9j/', 'iVBORw0KGgo')):  # JPEG/PNG signatures
            raise ValueError('Neplatný formát obrázku')
        return v.strip()

class MedicationInfo(BaseModel):
    """Strukturované informace o léku z databáze SÚKL"""
    name: Optional[str] = Field(None, description="Obchodní název léku")
    active_ingredient: Optional[str] = Field(None, description="Účinná látka (INN)")
    strength: Optional[str] = Field(None, description="Síla léku (mg, ml, atd.)")
    form: Optional[str] = Field(None, description="Léková forma")
    manufacturer: Optional[str] = Field(None, description="Výrobce/držitel rozhodnutí")
    registration_number: Optional[str] = Field(None, description="Registrační číslo")
    atc_code: Optional[str] = Field(None, description="ATC kód")
    indication: Optional[str] = Field(None, description="Terapeutické indikace")
    contraindication: Optional[str] = Field(None, description="Kontraindikace")
    side_effects: Optional[str] = Field(None, description="Nežádoucí účinky")
    interactions: Optional[str] = Field(None, description="Interakce s jinými léky")
    dosage: Optional[str] = Field(None, description="Dávkování")
    price: Optional[str] = Field(None, description="Orientační cena")
    prescription_required: Optional[str] = Field(None, description="Předpisovost")

class VisionResult(BaseModel):
    """Výsledek rozpoznání léku z obrázku pomocí GPT-4 Vision"""
    name: str = Field(..., description="Rozpoznaný název léku")
    active_ingredient: str = Field(default="není viditelné", description="Rozpoznaná účinná látka")
    strength: str = Field(default="není viditelné", description="Rozpoznaná síla")
    form: str = Field(default="není viditelné", description="Rozpoznaná léková forma") 
    manufacturer: str = Field(default="není viditelné", description="Rozpoznaný výrobce")
    registration_number: str = Field(default="není viditelné", description="Rozpoznané reg. číslo")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Spolehlivost rozpoznání (0-1)")
    warning: Optional[str] = Field(None, description="Varování při nízké spolehlivosti")
    validated: Optional[bool] = Field(None, description="Validováno proti databázi SÚKL")
    sukl_matches: Optional[List[Dict[str, Any]]] = Field(None, description="Shody v SÚKL databázi")

class TextProcessingResult(BaseModel):
    """Výsledek zpracování textového dotazu"""
    answer: str = Field(..., description="Strukturovaná odpověď na dotaz")
    sources: List[str] = Field(default_factory=list, description="Zdroje informací")
    confidence: str = Field(..., description="Míra spolehlivosti (high/medium/low)")
    
class APIResponse(BaseModel):
    """Standardní API odpověď"""
    status: str = Field(..., description="Status odpovědi (success/error)")
    data: Dict[Any, Any] = Field(default_factory=dict, description="Data odpovědi")
    error: str = Field(default="", description="Chybová zpráva pokud status=error")
    disclaimer: str = Field(default="", description="Povinný zdravotní disclaimer")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp odpovědi")

class SessionData(BaseModel):
    """Model pro anonymní session data (sessionStorage)"""
    session_id: str = Field(..., description="Jedinečný identifikátor relace")
    created_at: datetime = Field(default_factory=datetime.now, description="Čas vytvoření")
    last_activity: datetime = Field(default_factory=datetime.now, description="Poslední aktivita")
    query_count: int = Field(default=0, description="Počet dotazů v relaci")

class MedicationSearchQuery(BaseModel):
    """Model pro vyhledávání v databázi SÚKL"""
    query_text: str = Field(..., description="Text pro vyhledání")
    search_type: str = Field(default="similarity", description="Typ vyhledávání (similarity/exact)")
    limit: int = Field(default=5, ge=1, le=20, description="Počet výsledků")
    include_inactive: bool = Field(default=False, description="Zahrnout neregistrované léky")

class SUKLDataRecord(BaseModel):
    """Model pro jeden záznam z SÚKL databáze"""
    nazev: Optional[str] = Field(None, description="Název přípravku")
    ucinne_latky: Optional[str] = Field(None, description="Účinné látky")
    sila: Optional[str] = Field(None, description="Síla")
    lekova_forma: Optional[str] = Field(None, description="Léková forma")
    drzitel_rozhodnuti: Optional[str] = Field(None, description="Držitel rozhodnutí")
    registracni_cislo: Optional[str] = Field(None, description="Registrační číslo")
    atc_kod: Optional[str] = Field(None, description="ATC kód")
    indikace: Optional[str] = Field(None, description="Indikace")
    kontraindikace: Optional[str] = Field(None, description="Kontraindikace")
    nezadouci_ucinky: Optional[str] = Field(None, description="Nežádoucí účinky")
    interakce: Optional[str] = Field(None, description="Interakce")
    davkovani: Optional[str] = Field(None, description="Dávkování")
    cena: Optional[str] = Field(None, description="Cena")
    predpisovost: Optional[str] = Field(None, description="Předpisovost")
    
    def to_medication_info(self) -> MedicationInfo:
        """Konverze na standardní MedicationInfo model"""
        return MedicationInfo(
            name=self.nazev,
            active_ingredient=self.ucinne_latky,
            strength=self.sila,
            form=self.lekova_forma,
            manufacturer=self.drzitel_rozhodnuti,
            registration_number=self.registracni_cislo,
            atc_code=self.atc_kod,
            indication=self.indikace,
            contraindication=self.kontraindikace,
            side_effects=self.nezadouci_ucinky,
            interactions=self.interakce,
            dosage=self.davkovani,
            price=self.cena,
            prescription_required=self.predpisovost
        )

class ErrorResponse(BaseModel):
    """Model pro chybové odpovědi"""
    status: str = Field(default="error", description="Vždy 'error'")
    error_code: str = Field(..., description="Kód chyby")
    error_message: str = Field(..., description="Popis chyby")
    details: Optional[str] = Field(None, description="Podrobnosti chyby") 
    timestamp: datetime = Field(default_factory=datetime.now, description="Čas chyby")

class HealthCheckResponse(BaseModel):
    """Model pro health check endpoint"""
    status: str = Field(default="healthy", description="Stav služby")
    service: str = Field(default="PillSee API", description="Název služby")
    version: str = Field(default="1.0.0", description="Verze API")
    timestamp: datetime = Field(default_factory=datetime.now, description="Čas kontroly")
    dependencies: Dict[str, str] = Field(default_factory=dict, description="Stav závislostí")

# Konstanty pro validaci
class Constants:
    """Konstanty používané v aplikaci"""
    
    # Limity pro dotazy
    MAX_QUERY_LENGTH = 500
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB v bytech
    
    # Rate limiting
    TEXT_QUERY_LIMIT = "10/minute"
    IMAGE_QUERY_LIMIT = "5/minute"
    
    # Confidemce thresholds
    HIGH_CONFIDENCE_THRESHOLD = 0.8
    MEDIUM_CONFIDENCE_THRESHOLD = 0.6
    LOW_CONFIDENCE_THRESHOLD = 0.4
    
    # Session
    SESSION_TIMEOUT_MINUTES = 30
    
    # Supported image formats
    SUPPORTED_IMAGE_FORMATS = ["image/jpeg", "image/png", "image/webp"]
    
    # Czech medical disclaimer
    MEDICAL_DISCLAIMER = """
    UPOZORNĚNÍ: Tyto informace slouží pouze pro informativní účely a nenahrazují 
    odbornou lékařskou radu, diagnózu nebo léčbu. Vždy se poraďte s kvalifikovaným 
    zdravotnickým odborníkem před užitím jakéhokoliv léku.
    """