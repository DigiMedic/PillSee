# Přidat do pillsee-backend/app/database/enhanced_vector_store.py

"""
Vylepšený vector store s optimalizacemi pro PillSee
Rozšíření současné vector_store.py implementace
"""

from typing import List, Dict, Optional, Tuple
import asyncio
import logging
from datetime import datetime, timedelta
import hashlib
import json
import numpy as np
from functools import lru_cache
import redis
from supabase import create_client
import openai

logger = logging.getLogger(__name__)

class EnhancedMedicationVectorStore:
    """Rozšíření současného vector store o caching a optimalizace"""
    
    def __init__(self, supabase_client, openai_client, redis_client=None):
        self.supabase = supabase_client
        self.openai = openai_client
        self.redis = redis_client  # Volitelné pro caching
        
        # Cache konfigurace
        self.embedding_cache = {}  # In-memory cache jako fallback
        self.cache_ttl = 3600  # 1 hodina
        
        # Search optimalizace
        self.similarity_threshold = 0.3  # Minimální podobnost
        self.max_results = 20
        
        # Batch processing
        self.batch_size = 50
        
    async def search_medications_enhanced(
        self, 
        query: str, 
        limit: int = 10,
        filters: Optional[Dict] = None,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        Vylepšené vyhledávání s caching a optimalizacemi
        """
        try:
            # Cache klíč pro query
            cache_key = self._get_cache_key(query, limit, filters)
            
            # Zkus cache nejdříve
            if use_cache:
                cached_results = await self._get_from_cache(cache_key)
                if cached_results:
                    logger.info("✅ Vráceno z cache")
                    return cached_results
            
            # Generování embeddings s cache
            query_embedding = await self._get_embedding_cached(query)
            if not query_embedding:
                logger.error("Nepodařilo se získat embedding")
                return []
            
            # Optimalizované vyhledávání v databázi
            results = await self._search_with_filters(
                query_embedding, 
                limit, 
                filters
            )
            
            # Post-processing a skórování
            enhanced_results = await self._enhance_results(results, query)
            
            # Uložení do cache
            if use_cache:
                await self._save_to_cache(cache_key, enhanced_results)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Chyba při enhanced search: {e}")
            # Fallback na základní vyhledávání
            return await self._fallback_search(query, limit)
    
    async def _get_embedding_cached(self, text: str) -> Optional[List[float]]:
        """Získá embedding s caching pro opakované dotazy"""
        
        # Hash pro cache klíč
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        
        # Zkus in-memory cache
        if text_hash in self.embedding_cache:
            cache_entry = self.embedding_cache[text_hash]
            if datetime.now() - cache_entry['timestamp'] < timedelta(seconds=self.cache_ttl):
                logger.debug("Embedding z in-memory cache")
                return cache_entry['embedding']
        
        # Zkus Redis cache
        if self.redis:
            try:
                cached = await self.redis.get(f"embedding:{text_hash}")
                if cached:
                    logger.debug("Embedding z Redis cache")
                    return json.loads(cached)
            except Exception as e:
                logger.debug(f"Redis cache miss: {e}")
        
        # Generuj nový embedding
        try:
            response = await self.openai.embeddings.create(
                model="text-embedding-3-small",
                input=text,
                dimensions=512
            )
            
            embedding = response.data[0].embedding
            
            # Uložení do cache
            cache_entry = {
                'embedding': embedding,
                'timestamp': datetime.now()
            }
            
            # In-memory cache (s limitem velikosti)
            if len(self.embedding_cache) > 1000:
                # Vymaž nejstarší
                oldest_key = min(
                    self.embedding_cache.keys(), 
                    key=lambda k: self.embedding_cache[k]['timestamp']
                )
                del self.embedding_cache[oldest_key]
            
            self.embedding_cache[text_hash] = cache_entry
            
            # Redis cache
            if self.redis:
                try:
                    await self.redis.setex(
                        f"embedding:{text_hash}", 
                        self.cache_ttl, 
                        json.dumps(embedding)
                    )
                except Exception as e:
                    logger.debug(f"Redis cache save failed: {e}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Chyba při generování embedding: {e}")
            return None
    
    async def _search_with_filters(
        self, 
        query_embedding: List[float], 
        limit: int,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Optimalizované vyhledávání s filtry"""
        
        try:
            # Základní podobnostní vyhledávání
            rpc_query = self.supabase.rpc(
                'match_medications',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': self.similarity_threshold,
                    'match_count': min(limit * 2, self.max_results)  # Více výsledků pro filtrování
                }
            )
            
            # Aplikace filtrů
            if filters:
                if 'atc_code' in filters:
                    rpc_query = rpc_query.ilike('atc_kod', f"%{filters['atc_code']}%")
                
                if 'manufacturer' in filters:
                    rpc_query = rpc_query.ilike('drzitel_rozhodnuti', f"%{filters['manufacturer']}%")
                
                if 'active_ingredient' in filters:
                    rpc_query = rpc_query.ilike('ucinne_latky', f"%{filters['active_ingredient']}%")
                
                if 'dosage_form' in filters:
                    rpc_query = rpc_query.ilike('lekova_forma', f"%{filters['dosage_form']}%")
            
            response = rpc_query.execute()
            
            if response.data:
                return response.data[:limit]  # Omez na požadovaný počet
            
        except Exception as e:
            logger.error(f"Chyba při DB vyhledávání: {e}")
        
        return []
    
    async def _enhance_results(self, results: List[Dict], original_query: str) -> List[Dict]:
        """Post-processing výsledků s dodatečným skórováním"""
        
        enhanced = []
        query_lower = original_query.lower()
        
        for result in results:
            # Základní similarity score z databáze
            base_similarity = result.get('similarity', 0.0)
            
            # Dodatečné skórování na základě exact matches
            bonus_score = 0.0
            
            # Bonus za exact match v názvu
            name = result.get('nazev', '').lower()
            if query_lower in name:
                bonus_score += 0.2
                if query_lower == name:
                    bonus_score += 0.3  # Exact match bonus
            
            # Bonus za match v účinné látce
            active = result.get('ucinne_latky', '').lower() 
            if query_lower in active:
                bonus_score += 0.15
            
            # Bonus za match v indikacích
            indications = result.get('indikace', '').lower()
            if query_lower in indications:
                bonus_score += 0.1
            
            # Finální score
            final_similarity = min(base_similarity + bonus_score, 1.0)
            result['enhanced_similarity'] = final_similarity
            
            # Přidání confidence kategorie
            if final_similarity >= 0.8:
                result['confidence'] = 'high'
            elif final_similarity >= 0.6:
                result['confidence'] = 'medium'
            else:
                result['confidence'] = 'low'
            
            enhanced.append(result)
        
        # Seřazení podle enhanced similarity
        enhanced.sort(key=lambda x: x['enhanced_similarity'], reverse=True)
        
        return enhanced
    
    def _get_cache_key(self, query: str, limit: int, filters: Optional[Dict]) -> str:
        """Generuje cache klíč pro query"""
        
        cache_data = {
            'query': query.lower().strip(),
            'limit': limit,
            'filters': filters or {}
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_string.encode()).hexdigest()[:16]
    
    async def _get_from_cache(self, cache_key: str) -> Optional[List[Dict]]:
        """Načte výsledky z cache"""
        
        if self.redis:
            try:
                cached = await self.redis.get(f"search:{cache_key}")
                if cached:
                    return json.loads(cached)
            except Exception as e:
                logger.debug(f"Cache get failed: {e}")
        
        return None
    
    async def _save_to_cache(self, cache_key: str, results: List[Dict]):
        """Uloží výsledky do cache"""
        
        if self.redis and results:
            try:
                await self.redis.setex(
                    f"search:{cache_key}", 
                    self.cache_ttl, 
                    json.dumps(results)
                )
            except Exception as e:
                logger.debug(f"Cache save failed: {e}")
    
    async def _fallback_search(self, query: str, limit: int) -> List[Dict]:
        """Fallback vyhledávání při chybách"""
        
        try:
            # Jednoduchý text search bez embeddings
            response = self.supabase.table('medications').select('*').or_(
                f'nazev.ilike.%{query}%,'
                f'ucinne_latky.ilike.%{query}%,'
                f'indikace.ilike.%{query}%'
            ).limit(limit).execute()
            
            if response.data:
                # Přidání základního skórování
                for result in response.data:
                    result['similarity'] = 0.5  # Střední skóre pro text search
                    result['confidence'] = 'medium'
                
                return response.data
                
        except Exception as e:
            logger.error(f"Fallback search failed: {e}")
        
        return []
    
    async def batch_update_embeddings(self, medications: List[Dict]):
        """Batch aktualizace embeddings pro lepší výkon"""
        
        logger.info(f"Batch update {len(medications)} embeddings...")
        
        # Zpracování v batch dávkách
        for i in range(0, len(medications), self.batch_size):
            batch = medications[i:i + self.batch_size]
            
            try:
                # Připravení textů pro embedding
                texts = []
                for med in batch:
                    text = self._create_embedding_text(med)
                    texts.append(text)
                
                # Batch generování embeddings
                response = await self.openai.embeddings.create(
                    model="text-embedding-3-small",
                    input=texts,
                    dimensions=512
                )
                
                # Batch uložení do databáze
                updates = []
                for j, embedding_data in enumerate(response.data):
                    updates.append({
                        'id': batch[j]['id'],
                        'embedding': embedding_data.embedding
                    })
                
                # Batch upsert
                self.supabase.table('medications').upsert(updates).execute()
                
                logger.info(f"✅ Batch {i//self.batch_size + 1} dokončen")
                
                # Rate limiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Chyba v batch {i//self.batch_size + 1}: {e}")
                continue
    
    def _create_embedding_text(self, medication: Dict) -> str:
        """Vytvoří optimalizovaný text pro embedding"""
        
        parts = []
        
        # Název (nejvyšší váha)
        if medication.get('nazev'):
            parts.append(f"Název: {medication['nazev']}")
        
        # Účinná látka
        if medication.get('ucinne_latky'):
            parts.append(f"Účinná látka: {medication['ucinne_latky']}")
        
        # Indikace (důležité pro vyhledávání podle účelu)
        if medication.get('indikace'):
            parts.append(f"Indikace: {medication['indikace']}")
        
        # Léková forma a síla
        if medication.get('lekova_forma'):
            parts.append(f"Forma: {medication['lekova_forma']}")
        
        if medication.get('sila'):
            parts.append(f"Síla: {medication['sila']}")
        
        # ATC kód pro klasifikaci
        if medication.get('atc_kod'):
            parts.append(f"ATC: {medication['atc_kod']}")
        
        return " | ".join(parts)
    
    async def get_search_analytics(self) -> Dict:
        """Analytics pro optimalizaci vyhledávání"""
        
        analytics = {
            'cache_stats': {
                'in_memory_size': len(self.embedding_cache),
                'redis_available': self.redis is not None
            },
            'search_stats': {
                'similarity_threshold': self.similarity_threshold,
                'max_results': self.max_results,
                'batch_size': self.batch_size
            }
        }
        
        if self.redis:
            try:
                # Redis cache statistiky
                info = await self.redis.info()
                analytics['redis_stats'] = {
                    'used_memory': info.get('used_memory_human', 'N/A'),
                    'connected_clients': info.get('connected_clients', 0)
                }
            except:
                pass
        
        return analytics

# Optimalizovaný wrapper pro současný systém
class OptimizedMedicationSearch:
    """Wrapper pro integraci s současným PillSee systémem"""
    
    def __init__(self, settings):
        self.settings = settings
        self.enhanced_store = None
        self._init_components()
    
    def _init_components(self):
        """Inicializace komponent"""
        
        # Supabase client
        supabase = create_client(
            self.settings.supabase_url, 
            self.settings.supabase_service_key or self.settings.supabase_anon_key
        )
        
        # OpenAI client
        openai_client = openai.AsyncOpenAI(api_key=self.settings.openai_api_key)
        
        # Redis client (volitelný)
        redis_client = None
        try:
            import aioredis
            redis_url = getattr(self.settings, 'redis_url', None)
            if redis_url:
                redis_client = aioredis.from_url(redis_url)
        except ImportError:
            logger.info("Redis není dostupný, používám in-memory cache")
        
        # Enhanced store
        self.enhanced_store = EnhancedMedicationVectorStore(
            supabase, 
            openai_client, 
            redis_client
        )
    
    async def search(
        self, 
        query: str, 
        limit: int = 10, 
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Hlavní search metoda pro integraci s workflow"""
        
        if not self.enhanced_store:
            raise ValueError("Enhanced store není inicializován")
        
        return await self.enhanced_store.search_medications_enhanced(
            query, 
            limit, 
            filters, 
            use_cache=True
        )
    
    async def get_analytics(self) -> Dict:
        """Získání analytics dat"""
        
        if not self.enhanced_store:
            return {}
        
        return await self.enhanced_store.get_search_analytics()

# Export pro použití v současném workflow
__all__ = [
    'EnhancedMedicationVectorStore', 
    'OptimizedMedicationSearch'
]