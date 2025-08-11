"""
LangGraph workflow pro zpracování dotazů na léky
Orchestrace AI agentů pro text i obrázek dotazy
"""

from langgraph.graph import StateGraph, END
from typing import Dict, Any, Optional, List, TypedDict
import logging

from ..ai.vision_processor import VisionProcessor
from ..ai.text_processor import TextProcessor
from ..database.vector_store import MedicationVectorStore
from ..config import settings

logger = logging.getLogger(__name__)

class MedicationState(TypedDict):
    """Stavový model pro medication workflow"""
    query: str
    query_type: str  # "text" nebo "image"
    image_data: Optional[str]
    extracted_text: Optional[str]
    medication_info: Optional[Dict[str, Any]]
    safety_warnings: List[str]
    disclaimer: str
    confidence_score: float
    sources: List[str]
    error: Optional[str]

def extract_medication_from_image(state: MedicationState) -> MedicationState:
    """
    Použít GPT-4 Vision k extrakci informací z obrázku léku
    
    Args:
        state: Aktuální stav workflow obsahující image_data
        
    Returns:
        MedicationState: Aktualizovaný stav s extrahovanými informacemi
    """
    logger.info("Spouštím extraci léku z obrázku pomocí GPT-4 Vision")
    
    try:
        if not state.get("image_data"):
            state["error"] = "Chybí obrázek pro zpracování"
            return state
            
        # Inicializace vision processoru
        vision_processor = VisionProcessor()
        
        # GPT-4 Vision zpracování
        vision_result = vision_processor.process_medication_image(state["image_data"])
        
        # Uložení výsledků do state
        state["medication_info"] = vision_result.dict()
        state["confidence_score"] = vision_result.confidence_score
        state["extracted_text"] = f"Název: {vision_result.name}"
        
        if vision_result.warning:
            if not state.get("safety_warnings"):
                state["safety_warnings"] = []
            state["safety_warnings"].append(vision_result.warning)
        
        logger.info(f"Vision extraction completed with confidence: {state['confidence_score']:.2f}")
        return state
        
    except Exception as e:
        logger.error(f"Error in vision extraction: {str(e)}")
        state["error"] = f"Chyba při rozpoznání obrázku: {str(e)}"
        return state

def search_sukl_database(state: MedicationState) -> MedicationState:
    """
    Vyhledat informace o léku v databázi SÚKL pomocí RAG
    
    Args:
        state: Stav obsahující dotaz nebo extrahované informace
        
    Returns:
        MedicationState: Stav obohacený o informace z SÚKL databáze
    """
    logger.info("Vyhledávám v databázi SÚKL")
    
    try:
        # Inicializace vector store
        vector_store = MedicationVectorStore()
        
        # Určit search query na základě typu dotazu
        if state["query_type"] == "image":
            search_query = state.get("extracted_text", "")
            if state.get("medication_info", {}).get("name"):
                search_query = state["medication_info"]["name"]
        else:
            search_query = state["query"]
            
        if not search_query.strip():
            state["error"] = "Chybí dotaz pro vyhledání v databázi"
            return state
        
        if state["query_type"] == "text":
            # Pro textové dotazy použijeme RAG s text processorem
            text_processor = TextProcessor(vector_store)
            result = text_processor.process_text_query(search_query)
            
            # Uložení výsledků
            state["medication_info"] = {
                "answer": result.answer,
                "sources": result.sources,
                "confidence": result.confidence
            }
            state["sources"] = result.sources
            state["confidence_score"] = 0.9 if result.confidence == "high" else (0.7 if result.confidence == "medium" else 0.4)
            
        else:
            # Pro image dotazy použijeme vyhledání podobných léků
            search_results = vector_store.search_medications(
                query=search_query,
                limit=5,
                similarity_threshold=0.6
            )
            
            if search_results:
                # Použijeme nejlepší match
                best_match = search_results[0]
                best_metadata = best_match["metadata"]
                
                # Sloučit s existujícími informacemi z vision
                if state.get("medication_info"):
                    # Obohacení informací z databáze
                    for key, value in best_metadata.items():
                        if value and (key not in state["medication_info"] or 
                                    state["medication_info"][key] == "není viditelné"):
                            state["medication_info"][key] = value
                else:
                    state["medication_info"] = best_metadata
                    
                state["sources"] = [metadata.get("name", "SÚKL databáze") for metadata in [result["metadata"] for result in search_results[:3]]]
                
                # Validace pomocí vector store
                if state.get("medication_info"):
                    vision_processor = VisionProcessor()
                    validated_info = vision_processor.validate_against_sukl(
                        state["medication_info"], 
                        vector_store
                    )
                    state["medication_info"] = validated_info.dict() if hasattr(validated_info, 'dict') else validated_info
                    
            else:
                logger.warning(f"Žádné výsledky pro dotaz: {search_query}")
                if not state.get("safety_warnings"):
                    state["safety_warnings"] = []
                state["safety_warnings"].append("Informace o tomto léku nebyly nalezeny v databázi SÚKL")
        
        logger.info("SÚKL database search completed successfully")
        return state
        
    except Exception as e:
        logger.error(f"Error in SÚKL search: {str(e)}")
        state["error"] = f"Chyba při vyhledávání v databázi: {str(e)}"
        return state

def add_safety_disclaimers(state: MedicationState) -> MedicationState:
    """
    Přidat povinná zdravotní upozornění a disclaimery v češtině
    
    Args:
        state: Stav obsahující informace o léku
        
    Returns:
        MedicationState: Stav s přidanými bezpečnostními upozorněními
    """
    logger.info("Přidávám bezpečnostní upozornění a disclaimery")
    
    try:
        # Základní bezpečnostní upozornění
        safety_warnings = []
        
        # Kontrola kontraindikací
        if state.get("medication_info", {}).get("contraindication"):
            safety_warnings.append("⚠️ Zkontrolujte kontraindikace před užitím")
            
        # Kontrola interakcí
        if state.get("medication_info", {}).get("interactions"):  
            safety_warnings.append("⚠️ Informujte se o možných interakcích s jinými léky")
            
        # Kontrola předpisovosti
        prescription_req = state.get("medication_info", {}).get("prescription_required", "")
        if "předpis" in prescription_req.lower():
            safety_warnings.append("⚠️ Tento lék vyžaduje lékařský předpis")
            
        # Obecná upozornění pro konkrétní typy léků
        med_name = state.get("medication_info", {}).get("name", "").lower()
        if any(keyword in med_name for keyword in ["antibio", "kortiko", "psycho"]):
            safety_warnings.append("⚠️ Tento typ léku vyžaduje zvláštní pozornost při užívání")
            
        state["safety_warnings"] = safety_warnings
        
        # Povinný disclaimer z konfigurace
        disclaimer = settings.medical_disclaimer + """
        
        Informace pocházejí z oficiální databáze SÚKL, ale mohou se změnit. 
        Pro nejaktuálnější informace kontaktujte lékárnu nebo lékaře.
        """
        
        state["disclaimer"] = disclaimer.strip()
        
        logger.info(f"Added {len(safety_warnings)} safety warnings and disclaimer")
        return state
        
    except Exception as e:
        logger.error(f"Error adding safety disclaimers: {str(e)}")
        # Disclaimer je kritický, takže ho přidáme i při chybě
        state["disclaimer"] = """
        UPOZORNĚNÍ: Tyto informace slouží pouze pro informativní účely a nenahrazují 
        odbornou lékařskou radu. Vždy se poraďte s lékařem před užitím léků.
        """
        return state

def validate_and_enhance_info(state: MedicationState) -> MedicationState:
    """
    Validovat a vylepšit informace o léku
    Kontrola konzistence a doplnění chybějících údajů
    """
    logger.info("Validuji a vylepšuji informace o léku")
    
    try:
        medication_info = state.get("medication_info", {})
        
        # Kontrola povinných polí
        required_fields = ["name", "active_ingredient"]
        missing_fields = [field for field in required_fields if not medication_info.get(field)]
        
        if missing_fields:
            logger.warning(f"Missing required fields: {missing_fields}")
            state["confidence_score"] = max(0.0, state.get("confidence_score", 0.0) - 0.2)
            
        # Normalizace českých názvů
        if medication_info.get("name"):
            medication_info["name"] = medication_info["name"].upper().strip()
            
        # Kontrola konzistence síly a formy
        strength = medication_info.get("strength", "")
        form = medication_info.get("form", "")
        
        if strength and form:
            if "tablety" in form.lower() and "mg" not in strength:
                logger.warning("Inconsistent strength/form combination detected")
                
        state["medication_info"] = medication_info
        
        logger.info("Validation and enhancement completed")
        return state
        
    except Exception as e:
        logger.error(f"Error in validation: {str(e)}")
        return state

# Sestavení LangGraph workflow
def create_medication_workflow() -> StateGraph:
    """
    Vytvoří a vrátí LangGraph workflow pro zpracování dotazů na léky
    
    Returns:
        StateGraph: Sestavený workflow graf
    """
    workflow = StateGraph(MedicationState)
    
    # Přidání uzlů do workflow
    workflow.add_node("extract_image", extract_medication_from_image)
    workflow.add_node("search_database", search_sukl_database) 
    workflow.add_node("validate_info", validate_and_enhance_info)
    workflow.add_node("add_disclaimers", add_safety_disclaimers)
    
    # Definování entry point
    workflow.set_entry_point("route_query")
    
    # Routing function
    def route_query(state: MedicationState) -> str:
        """Route na základě typu dotazu"""
        if state["query_type"] == "image":
            return "extract_image"
        else:
            return "search_database"
    
    # Přidání routing node
    workflow.add_node("route_query", route_query)
    workflow.add_conditional_edges(
        "route_query",
        route_query,
        {
            "extract_image": "extract_image",
            "search_database": "search_database"
        }
    )
    
    # Pro image dotazy: extract -> search -> validate -> disclaimers  
    workflow.add_edge("extract_image", "search_database")
    
    # Pro text dotazy: search -> validate -> disclaimers
    workflow.add_edge("search_database", "validate_info")
    workflow.add_edge("validate_info", "add_disclaimers") 
    workflow.add_edge("add_disclaimers", END)
    
    logger.info("Medication workflow created successfully")
    return workflow

# Globální instance workflow - zkompilovaný
medication_workflow = create_medication_workflow().compile()