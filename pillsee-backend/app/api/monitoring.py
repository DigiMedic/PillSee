# Přidat do pillsee-backend/app/api/monitoring.py

"""
Rozšířené API endpointy pro monitoring PillSee systému
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, List, Optional
import logging
import asyncio
from datetime import datetime, timedelta
import json

from ..config import settings
from ..database.enhanced_vector_store import OptimizedMedicationSearch
from ..data.sukl_enhanced_processor import EnhancedSUKLProcessor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["monitoring"])

# Globální instance pro monitoring
search_instance = None
sukl_processor = None

def get_search_instance() -> OptimizedMedicationSearch:
    """Dependency pro search instanci"""
    global search_instance
    if not search_instance:
        search_instance = OptimizedMedicationSearch(settings)
    return search_instance

def get_sukl_processor() -> EnhancedSUKLProcessor:
    """Dependency pro SÚKL processor"""
    global sukl_processor
    if not sukl_processor:
        sukl_processor = EnhancedSUKLProcessor()
    return sukl_processor

@router.get("/health/detailed")
async def detailed_health_check(
    search: OptimizedMedicationSearch = Depends(get_search_instance)
):
    """Rozšířený health check s podrobnými informacemi"""
    
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {},
        "performance": {},
        "data_sources": {}
    }
    
    try:
        # Test databázového připojení
        start_time = datetime.now()
        test_results = await search.search("test", limit=1)
        db_response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        health_data["components"]["database"] = {
            "status": "healthy" if test_results is not None else "unhealthy",
            "response_time_ms": round(db_response_time, 2),
            "test_query_results": len(test_results) if test_results else 0
        }
        
    except Exception as e:
        health_data["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_data["status"] = "degraded"
    
    try:
        # Test OpenAI připojení
        import openai
        client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        
        start_time = datetime.now()
        test_embedding = await client.embeddings.create(
            model="text-embedding-3-small",
            input="test",
            dimensions=512
        )
        openai_response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        health_data["components"]["openai"] = {
            "status": "healthy",
            "response_time_ms": round(openai_response_time, 2),
            "embedding_model": "text-embedding-3-small",
            "embedding_dimensions": len(test_embedding.data[0].embedding)
        }
        
    except Exception as e:
        health_data["components"]["openai"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_data["status"] = "unhealthy"
    
    try:
        # Analytics z enhanced search
        analytics = await search.get_analytics()
        health_data["performance"]["search_analytics"] = analytics
        
    except Exception as e:
        logger.warning(f"Analytics failed: {e}")
    
    return health_data

@router.get("/data-sources/status")
async def data_sources_status(
    processor: EnhancedSUKLProcessor = Depends(get_sukl_processor)
):
    """Status dostupnosti různých datových zdrojů"""
    
    sources_status = {}
    
    async with processor:
        # Test všech zdrojů
        for source_name, source_config in processor.data_sources.items():
            try:
                is_available = await processor._test_source_availability(source_config)
                
                sources_status[source_name] = {
                    "available": is_available,
                    "priority": source_config['priority'],
                    "urls": source_config['urls'],
                    "last_checked": datetime.now().isoformat()
                }
                
                if is_available:
                    sources_status[source_name]["status"] = "healthy"
                else:
                    sources_status[source_name]["status"] = "unhealthy"
                    
            except Exception as e:
                sources_status[source_name] = {
                    "available": False,
                    "status": "error",
                    "error": str(e),
                    "last_checked": datetime.now().isoformat()
                }
    
    # Doporučení nejlepšího zdroje
    available_sources = [
        (name, config) for name, config in sources_status.items()
        if config.get("available", False)
    ]
    
    if available_sources:
        best_source = min(available_sources, key=lambda x: x[1]["priority"])
        recommended_source = best_source[0]
    else:
        recommended_source = "mock_data"
    
    return {
        "sources": sources_status,
        "recommended_source": recommended_source,
        "total_available": len(available_sources),
        "last_check": datetime.now().isoformat()
    }

@router.post("/data-sources/refresh")
async def refresh_data_sources(
    background_tasks: BackgroundTasks,
    processor: EnhancedSUKLProcessor = Depends(get_sukl_processor),
    search: OptimizedMedicationSearch = Depends(get_search_instance)
):
    """Vynucené obnovení dat ze zdrojů"""
    
    async def refresh_task():
        """Background task pro refresh dat"""
        try:
            logger.info("Začínám refresh SÚKL dat...")
            
            async with processor:
                # Stažení nejnovějších dat
                df = await processor.get_data_with_fallback()
                
                if df is not None and len(df) > 0:
                    # Konverze na formát pro vector store
                    medications = df.to_dict('records')
                    
                    # Batch update embeddings
                    if hasattr(search.enhanced_store, 'batch_update_embeddings'):
                        await search.enhanced_store.batch_update_embeddings(medications)
                    
                    logger.info(f"✅ Refresh dokončen - {len(medications)} záznamů")
                else:
                    logger.warning("⚠️ Refresh selhal - žádná data")
                    
        except Exception as e:
            logger.error(f"❌ Chyba při refresh: {e}")
    
    # Přidání do background tasks
    background_tasks.add_task(refresh_task)
    
    return {
        "status": "refresh_started",
        "message": "Refresh dat byl zahájen na pozadí",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/search/analytics")
async def search_analytics(
    search: OptimizedMedicationSearch = Depends(get_search_instance)
):
    """Analytiky vyhledávání pro optimalizaci"""
    
    try:
        analytics = await search.get_analytics()
        
        # Přidání dalších metrik
        analytics["recommendations"] = []
        
        # Cache recommendations
        cache_stats = analytics.get("cache_stats", {})
        if cache_stats.get("in_memory_size", 0) > 800:
            analytics["recommendations"].append({
                "type": "cache_optimization",
                "message": "In-memory cache je skoro plný, zvažte zvýšení limitu nebo čištění",
                "priority": "medium"
            })
        
        if not cache_stats.get("redis_available", False):
            analytics["recommendations"].append({
                "type": "performance",
                "message": "Redis není dostupný - embedding cache používá pouze paměť",
                "priority": "low"
            })
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při získávání analytics: {e}")

@router.get("/performance/metrics")
async def performance_metrics(
    search: OptimizedMedicationSearch = Depends(get_search_instance)
):
    """Metriky výkonu systému"""
    
    metrics = {
        "search_performance": {},
        "database_performance": {},
        "recommendations": []
    }
    
    try:
        # Test rychlosti vyhledávání s různými typy dotazů
        test_queries = [
            ("paralen", "common_drug"),
            ("antibiotika", "category"),
            ("bolest hlavy", "symptom"),
            ("xyz123nonexistent", "nonexistent")
        ]
        
        for query, query_type in test_queries:
            start_time = datetime.now()
            results = await search.search(query, limit=5)
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            metrics["search_performance"][query_type] = {
                "query": query,
                "response_time_ms": round(response_time, 2),
                "results_count": len(results) if results else 0,
                "avg_confidence": sum(
                    r.get('enhanced_similarity', 0) for r in (results or [])
                ) / max(len(results or []), 1)
            }
            
            # Performance recommendations
            if response_time > 1000:  # > 1s
                metrics["recommendations"].append({
                    "type": "performance",
                    "message": f"Pomalý response pro {query_type} dotazy ({response_time:.0f}ms)",
                    "priority": "high"
                })
            
            # Malý delay mezi testy
            await asyncio.sleep(0.1)
    
    except Exception as e:
        metrics["error"] = str(e)
    
    return metrics

@router.get("/database/stats")
async def database_statistics():
    """Statistiky databáze"""
    
    try:
        from ..database.vector_store import MedicationVectorStore
        
        # Získání základních statistik z databáze
        vector_store = MedicationVectorStore()
        stats = vector_store.get_database_stats()
        
        # Rozšířené statistiky
        extended_stats = {
            **stats,
            "table_sizes": {},
            "index_stats": {},
            "data_quality": {}
        }
        
        # Můžete přidat další SQL dotazy pro podrobné statistiky
        
        return extended_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Nepodařilo se získat databázové statistiky"
        }

@router.post("/cache/clear")
async def clear_cache(
    search: OptimizedMedicationSearch = Depends(get_search_instance)
):
    """Vyčištění cache pro testing"""
    
    cleared_items = 0
    
    try:
        # Vyčištění in-memory cache
        if hasattr(search.enhanced_store, 'embedding_cache'):
            cleared_items += len(search.enhanced_store.embedding_cache)
            search.enhanced_store.embedding_cache.clear()
        
        # Vyčištění Redis cache
        if hasattr(search.enhanced_store, 'redis') and search.enhanced_store.redis:
            try:
                # Najdi všechny PillSee cache klíče
                keys = await search.enhanced_store.redis.keys("embedding:*")
                keys.extend(await search.enhanced_store.redis.keys("search:*"))
                
                if keys:
                    await search.enhanced_store.redis.delete(*keys)
                    cleared_items += len(keys)
                    
            except Exception as e:
                logger.warning(f"Redis cache clear failed: {e}")
        
        return {
            "status": "cache_cleared",
            "cleared_items": cleared_items,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při čištění cache: {e}")

@router.get("/logs/recent")
async def get_recent_logs(limit: int = 100):
    """Získání posledních logů pro debugging"""
    
    try:
        # Číst z log souboru pokud existuje
        log_file = "sukl_import.log"  # Používá se v současném systému
        
        if not Path(log_file).exists():
            return {"logs": [], "message": "Log soubor neexistuje"}
        
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Poslední N řádků
        recent_lines = lines[-limit:] if len(lines) > limit else lines
        
        logs = []
        for line in recent_lines:
            if line.strip():
                logs.append({
                    "message": line.strip(),
                    "timestamp": datetime.now().isoformat()  # Simplified
                })
        
        return {
            "logs": logs,
            "total_lines": len(recent_lines),
            "log_file": log_file
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Nepodařilo se načíst logy"
        }

# Přidání do hlavní aplikace
def include_monitoring_routes(app):
    """Funkce pro přidání monitoring routes do hlavní aplikace"""
    app.include_router(router)

# Export
__all__ = ["router", "include_monitoring_routes"]