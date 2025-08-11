"""
Text Processor pro zpracování dotazů na české léky pomocí RAG
Integrace s OpenAI GPT-4o-mini a PostgreSQL pgvector databází
"""

from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.callbacks import get_openai_callback
import logging
from typing import Dict, List, Any

from ..config import settings
from ..models import TextProcessingResult

logger = logging.getLogger(__name__)

class TextProcessor:
    """Processor pro textové dotazy s RAG implementací"""
    
    def __init__(self, vector_store):
        """
        Inicializace text processoru
        
        Args:
            vector_store: Instance MedicationVectorStore
        """
        self.vector_store = vector_store
        self.llm = ChatOpenAI(
            model=settings.openai_text_model,
            temperature=0.1,  # Nízká teplota pro konzistentní medicínské odpovědi
            max_tokens=800,
            openai_api_key=settings.openai_api_key
        )
        
        # Vytvoření českého medicínského promptu
        self.prompt_template = self._create_czech_medical_prompt()
        
    def process_text_query(self, query: str) -> TextProcessingResult:
        """
        Zpracování textového dotazu na lék pomocí RAG
        
        Args:
            query: Textový dotaz v češtině
            
        Returns:
            TextProcessingResult: Strukturovaná odpověď
        """
        logger.info(f"Zpracovávám textový dotaz: '{query[:50]}...'")
        
        try:
            # Preprocessing dotazu
            processed_query = self._preprocess_query(query)
            
            # Vytvoření retrieval chain
            qa_chain = self._create_retrieval_chain()
            
            # Spuštění RAG pipeline s callback pro tracking
            with get_openai_callback() as cb:
                result = qa_chain.run(processed_query)
                
                logger.info(f"OpenAI usage - Tokens: {cb.total_tokens}, Cost: ${cb.total_cost:.4f}")
            
            # Získání zdrojů z vector search
            sources = self._get_source_documents(processed_query)
            
            # Určení confidence na základě kvality výsledku
            confidence = self._assess_response_confidence(result, sources)
            
            # Přidání povinného disclaimeru
            enhanced_answer = self._add_medical_disclaimers(result)
            
            logger.info(f"Textový dotaz zpracován úspěšně (confidence: {confidence})")
            
            return TextProcessingResult(
                answer=enhanced_answer,
                sources=[source.get("name", "Neznámý zdroj") for source in sources],
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Chyba při zpracování textového dotazu: {str(e)}")
            return TextProcessingResult(
                answer=f"Omlouvám se, nastala chyba při zpracování dotazu: {str(e)}\n\nProsím zkuste přeformulovat dotaz nebo kontaktujte lékárnu.",
                sources=[],
                confidence="low"
            )
    
    def _create_czech_medical_prompt(self) -> PromptTemplate:
        """Vytvoření českého medicínského prompt template"""
        
        template = """
        Jste odborný farmaceutický asistent specializující se na české léčivé přípravky. 
        Odpovídáte pouze na základě ověřených informací z oficiální databáze SÚKL.

        KONTEXT Z DATABÁZE SÚKL:
        {context}

        DOTAZ PACIENTA:
        {question}

        INSTRUKCE PRO ODPOVĚĎ:

        1. JAZYK: Odpovězte pouze v češtině s správnou medicínskou terminologií

        2. STRUKTURA ODPOVĚDI:
           - Začněte názvem léku a účinnou látkou
           - Pokračujte základními informacemi (forma, síla, indikace)
           - Přidejte důležité informace (dávkování, kontraindikace, nežádoucí účinky)
           - Zakončete praktickými informacemi (předpisovost, cena)

        3. BEZPEČNOSTNÍ ZÁSADY:
           - Používejte pouze informace z poskytnutého kontextu
           - Pokud informace není dostupná, jasně to uveďte
           - NIKDY neposkytujte diagnózy nebo doporučení léčby
           - Vždy odkažte na konzultaci s lékařem/lékárníkem

        4. FORMÁT ODPOVĚDI:
           **Název přípravku**: [název]
           **Účinná látka**: [INN název]
           **Léková forma a síla**: [forma, síla]
           **Indikace**: [k čemu se používá]
           **Dávkování**: [pokud je známo]
           **Důležitá upozornění**: [kontraindikace, nežádoucí účinky]
           **Předpisovost**: [s/bez předpisu]
           **Orientační cena**: [pokud je známa]

        5. NENÍ-LI INFORMACE DOSTUPNÁ:
           "Tuto informaci nemám k dispozici v aktuální databázi SÚKL."

        ODPOVĚĎ:
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def _preprocess_query(self, query: str) -> str:
        """
        Preprocessing textového dotazu
        
        Args:
            query: Původní dotaz
            
        Returns:
            str: Zpracovaný dotaz
        """
        # Základní čištění
        processed = query.strip()
        
        # Rozpoznání typů dotazů a optimalizace
        query_lower = processed.lower()
        
        # Dotazy na název léku
        if any(pattern in query_lower for pattern in ["co je", "jaký je", "co to je"]):
            processed = f"Informace o léku: {processed}"
        
        # Dotazy na účinnou látku  
        elif "účinná látka" in query_lower or "obsahuje" in query_lower:
            processed = f"Účinná látka léku: {processed}"
        
        # Dotazy na dávkování
        elif any(pattern in query_lower for pattern in ["dávkování", "kolik", "jak často"]):
            processed = f"Dávkování léku: {processed}"
        
        # Dotazy na interakce
        elif "interakce" in query_lower or "užívat s" in query_lower:
            processed = f"Lékové interakce: {processed}"
        
        logger.debug(f"Preprocessed query: {processed}")
        return processed
    
    def _create_retrieval_chain(self) -> RetrievalQA:
        """Vytvoření RAG retrieval chain"""
        
        vector_store_instance = self.vector_store.setup_vector_store()
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vector_store_instance.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}  # Top 5 nejrelevantnějších dokumentů
            ),
            chain_type_kwargs={"prompt": self.prompt_template},
            return_source_documents=False  # Handled separately for better control
        )
        
        return qa_chain
    
    def _get_source_documents(self, query: str) -> List[Dict[str, Any]]:
        """
        Získání zdrojových dokumentů pro transparency
        
        Args:
            query: Zpracovaný dotaz
            
        Returns:
            List[Dict]: Metadata zdrojových dokumentů
        """
        try:
            search_results = self.vector_store.search_medications(
                query=query,
                limit=5,
                similarity_threshold=0.6
            )
            
            return [result["metadata"] for result in search_results]
            
        except Exception as e:
            logger.warning(f"Nepodařilo se získat zdroje: {e}")
            return []
    
    def _assess_response_confidence(self, response: str, sources: List[Dict]) -> str:
        """
        Hodnocení kvality odpovědi
        
        Args:
            response: Generovaná odpověď
            sources: Zdrojové dokumenty
            
        Returns:
            str: Confidence level (high/medium/low)
        """
        # Hodnocení na základě délky odpovědi
        if len(response.strip()) < 50:
            return "low"
        
        # Hodnocení na základě počtu zdrojů
        if not sources:
            return "low"
        elif len(sources) < 2:
            return "medium"
        
        # Hodnocení na základě obsahu odpovědi
        positive_indicators = [
            "účinná látka", "indikace", "dávkování", 
            "síla", "tablety", "mg", "ml"
        ]
        
        response_lower = response.lower()
        found_indicators = sum(1 for indicator in positive_indicators 
                             if indicator in response_lower)
        
        if found_indicators >= 4:
            return "high"
        elif found_indicators >= 2:
            return "medium"
        else:
            return "low"
    
    def _add_medical_disclaimers(self, answer: str) -> str:
        """
        Přidání povinných zdravotních disclaimerů
        
        Args:
            answer: Původní odpověď
            
        Returns:
            str: Odpověď s disclaimery
        """
        disclaimer = settings.medical_disclaimer
        
        # Přidání disclaimeru na konec
        enhanced_answer = f"{answer.strip()}\n\n---\n{disclaimer.strip()}"
        
        return enhanced_answer
    
    def process_medication_comparison(self, medication1: str, medication2: str) -> TextProcessingResult:
        """
        Porovnání dvou léků
        
        Args:
            medication1: První lék k porovnání
            medication2: Druhý lék k porovnání
            
        Returns:
            TextProcessingResult: Porovnání léků
        """
        query = f"Porovnání léků {medication1} a {medication2} - účinné látky, indikace, rozdíly"
        
        logger.info(f"Porovnávám léky: {medication1} vs {medication2}")
        
        return self.process_text_query(query)
    
    def search_by_symptoms(self, symptoms: str) -> TextProcessingResult:
        """
        Vyhledání léků podle symptomů (s velkým upozoněním)
        
        Args:
            symptoms: Popis symptomů
            
        Returns:
            TextProcessingResult: Možné léky s důrazným disclaimerem
        """
        # Silné upozornění že nejde o diagnózu
        warning_query = f"""
        UPOZORNĚNÍ: Následující informace NEJSOU lékařská diagnóza ani doporučení léčby.
        
        Hledám léky které se OBECNĚ používají při symptomech: {symptoms}
        
        DŮLEŽITÉ: Vždy se poraďte s lékařem před užitím jakéhokoliv léku.
        """
        
        logger.warning(f"Symptom-based search: {symptoms}")
        
        result = self.process_text_query(warning_query)
        
        # Přidání extra varování
        result.answer = f"⚠️ **DŮLEŽITÉ VAROVÁNÍ**: Tyto informace nejsou lékařskou radou!\n\n{result.answer}"
        result.confidence = "low"  # Vždy nízká confidence pro symptom queries
        
        return result