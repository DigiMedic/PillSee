"""
OpenAI GPT-4 Vision Processor pro rozpoznávání českých léků z obrázků
Specializován na český text a farmaceutické obaly
"""

from openai import OpenAI
import base64
import json
import logging
from typing import Optional, Dict, Any
from PIL import Image
import io

from ..config import settings
from ..models import VisionResult

logger = logging.getLogger(__name__)

class VisionProcessor:
    """GPT-4 Vision processor pro rozpoznání léků z obrázků"""
    
    def __init__(self):
        """Inicializace OpenAI klienta"""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_vision_model
        self.max_tokens = 500
        
    def process_medication_image(self, image_data: str) -> VisionResult:
        """
        Zpracování obrázku léku pomocí GPT-4 Vision
        
        Args:
            image_data: Base64 encoded obrázek
            
        Returns:
            VisionResult: Strukturovaný výsledek rozpoznání
        """
        logger.info("Spouštím rozpoznávání léku z obrázku pomocí GPT-4 Vision")
        
        try:
            # Validace a příprava obrázku
            processed_image = self._preprocess_image(image_data)
            
            # Vytvoření prompt pro českého lékaře-specialistu
            system_prompt = self._create_czech_medical_prompt()
            
            # OpenAI Vision API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyzujte tento obrázek léku a extrahujte všechny viditelné informace:"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": processed_image,
                                    "detail": "high"  # Vysoké rozlišení pro lepší rozpoznání textu
                                }
                            }
                        ]
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.1  # Nízká teplota pro konzistentní výsledky
            )
            
            # Zpracování odpovědi
            content = response.choices[0].message.content
            result_data = self._parse_vision_response(content)
            
            # Validace kvality rozpoznání
            result_data = self._validate_recognition_quality(result_data)
            
            logger.info(f"Vision rozpoznání dokončeno s confidence: {result_data.get('confidence_score', 0.0):.2f}")
            
            return VisionResult(**result_data)
            
        except Exception as e:
            logger.error(f"Chyba při Vision zpracování: {str(e)}")
            return VisionResult(
                name="Chyba při rozpoznání",
                confidence_score=0.0,
                warning=f"Nepodařilo se rozpoznat lék z obrázku: {str(e)}"
            )
    
    def _preprocess_image(self, image_data: str) -> str:
        """
        Předzpracování obrázku pro lepší rozpoznání
        
        Args:
            image_data: Base64 encoded obrázek
            
        Returns:
            str: Zpracovaný obrázek jako data URL
        """
        try:
            # Detekce formátu
            if image_data.startswith('data:image'):
                return image_data
            
            # Dekódování base64
            if image_data.startswith('/9j/') or image_data.startswith('iVBORw0KGgo'):
                # Detekce JPEG/PNG
                image_bytes = base64.b64decode(image_data)
                
                # Validace velikosti
                if len(image_bytes) > settings.max_image_size_mb * 1024 * 1024:
                    raise ValueError(f"Obrázek je příliš velký (max {settings.max_image_size_mb}MB)")
                
                # Určení formátu
                image = Image.open(io.BytesIO(image_bytes))
                format_type = image.format.lower()
                
                if format_type == 'jpeg':
                    mime_type = 'image/jpeg'
                elif format_type == 'png':
                    mime_type = 'image/png'
                else:
                    # Konverze na JPEG pokud není podporovaný formát
                    if image.mode in ('RGBA', 'LA', 'P'):
                        # Convert to RGB for JPEG
                        rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                        rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                        image = rgb_image
                    
                    buffer = io.BytesIO()
                    image.save(buffer, format='JPEG', quality=85)
                    image_data = base64.b64encode(buffer.getvalue()).decode()
                    mime_type = 'image/jpeg'
                
                return f"data:{mime_type};base64,{image_data}"
            
            else:
                raise ValueError("Nerozpoznaný formát obrázku")
                
        except Exception as e:
            logger.error(f"Chyba při předzpracování obrázku: {e}")
            raise ValueError(f"Nepodařilo se zpracovat obrázek: {e}")
    
    def _create_czech_medical_prompt(self) -> str:
        """Vytvoření specializovaného promptu pro české léky"""
        return """
        Jste expert na české farmaceutické přípravky s hlubokými znalostmi české lékařské terminologie.
        
        Vaším úkolem je analyzovat obrázek obalu léku a extrahovat následující informace:
        
        POVINNÉ ÚDAJE K ROZPOZNÁNÍ:
        1. Obchodní název přípravku (často velké písmo na přední straně)
        2. Účinná látka (může být uvedena jako INN nebo český název)
        3. Síla/koncentrace (mg, ml, %, atd.)
        4. Léková forma (tablety, sirup, mast, atd.)
        5. Výrobce/držitel rozhodnutí
        6. Registrační číslo (format: XX/YYYY/ZZ-C)
        
        INSTRUKCE PRO ROZPOZNÁNÍ:
        - Zaměřte se na český text a terminologie
        - Rozlište mezi obchodním názvem a účinnou látkou
        - Pozor na podobné názvy různých síl téhož léku
        - Registrační číslo je obvykle malé písmo na spodku/boku
        - Pokud text není jasně čitelný, označte jako "není viditelné"
        
        VÝSTUP VE FORMÁTU JSON:
        {
          "name": "přesný obchodní název",
          "active_ingredient": "účinná látka (INN nebo český název)",
          "strength": "síla s jednotkami",
          "form": "léková forma",
          "manufacturer": "výrobce", 
          "registration_number": "registrační číslo",
          "confidence_score": 0.0-1.0,
          "extracted_text": "veškerý rozpoznaný text"
        }
        
        DŮLEŽITÉ: Odpovězte POUZE validním JSON objektem, žádný další text.
        """
    
    def _parse_vision_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parsování odpovědi z GPT-4 Vision
        
        Args:
            response_text: Raw odpověď od API
            
        Returns:
            Dict: Zparsovaná data
        """
        try:
            # Pokus o přímé JSON parsování
            result = json.loads(response_text.strip())
            
            # Validace povinných polí
            required_fields = ["name", "confidence_score"]
            for field in required_fields:
                if field not in result:
                    result[field] = "není viditelné" if field != "confidence_score" else 0.0
            
            return result
            
        except json.JSONDecodeError:
            logger.warning("GPT-4 Vision nevrátil validní JSON, parsovávám ručně")
            
            # Fallback manual parsing
            result = {
                "name": "není viditelné",
                "active_ingredient": "není viditelné", 
                "strength": "není viditelné",
                "form": "není viditelné",
                "manufacturer": "není viditelné",
                "registration_number": "není viditelné",
                "confidence_score": 0.3,
                "extracted_text": response_text
            }
            
            # Pokus o extrakci alespoň základních informací z textu
            text_lower = response_text.lower()
            
            if any(keyword in text_lower for keyword in ["paralen", "brufen", "aspirin"]):
                result["confidence_score"] = 0.5
                
            return result
    
    def _validate_recognition_quality(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validace kvality rozpoznání a přidání varování
        
        Args:
            result_data: Rozpoznaná data
            
        Returns:
            Dict: Data s validací a varováními
        """
        confidence = result_data.get("confidence_score", 0.0)
        
        # Snížení confidence pokud chybí kritické údaje
        name = result_data.get("name", "")
        active_ingredient = result_data.get("active_ingredient", "")
        
        if not name or name == "není viditelné":
            confidence = max(0.0, confidence - 0.3)
            result_data["warning"] = "Nepodařilo se rozpoznat název léku"
        
        if not active_ingredient or active_ingredient == "není viditelné":
            confidence = max(0.0, confidence - 0.2)
        
        # Kategorizace varování podle confidence
        if confidence < 0.4:
            result_data["warning"] = "Velmi nízká spolehlivost rozpoznání. Zkuste obrázek s lepším osvětlením nebo z jiného úhlu."
        elif confidence < 0.6:
            result_data["warning"] = "Nízká spolehlivost rozpoznání. Doporučujeme ověřit informace."
        elif confidence < 0.8:
            result_data["warning"] = "Střední spolehlivost rozpoznání. Zkontrolujte správnost údajů."
        
        result_data["confidence_score"] = round(confidence, 2)
        
        return result_data
    
    def validate_against_sukl(self, vision_result: VisionResult, vector_store) -> VisionResult:
        """
        Validace výsledků vision proti databázi SÚKL
        
        Args:
            vision_result: Výsledek z vision processing
            vector_store: Instance MedicationVectorStore
            
        Returns:
            VisionResult: Obohacený a validovaný výsledek
        """
        if not vision_result.name or vision_result.name == "není viditelné":
            logger.info("Chybí název pro SÚKL validaci")
            return vision_result
        
        logger.info(f"Validuji proti SÚKL: {vision_result.name}")
        
        try:
            # Použití vector store pro validaci
            validation_result = vector_store.validate_medication_info(vision_result.dict())
            
            # Update vision result s validací
            for key, value in validation_result.items():
                if hasattr(vision_result, key):
                    setattr(vision_result, key, value)
            
            return vision_result
            
        except Exception as e:
            logger.error(f"Chyba při SÚKL validaci: {e}")
            vision_result.warning = "Nepodařilo se ověřit informace v databázi SÚKL"
            return vision_result