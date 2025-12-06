# Přidat do pillsee-backend/app/data/sukl_enhanced_processor.py

"""
Vylepšený SÚKL processor s vícezdrojovou integrací
Rozšíření současné sukl_data_downloader.py implementace
"""

import asyncio
import aiohttp
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime, timedelta
import hashlib
import json

logger = logging.getLogger(__name__)

class EnhancedSUKLProcessor:
    """Rozšíření současné SÚKL integrace o další zdroje a optimalizace"""
    
    def __init__(self):
        # Rozšířené zdroje dat
        self.data_sources = {
            # Oficiální SÚKL OpenData (nejvyšší priorita)
            'official_opendata': {
                'priority': 1,
                'urls': [
                    'https://opendata.sukl.cz/soubory/NKOD/DLP/nkod_dlp_lecivepripravky.csv',
                    'https://opendata.sukl.cz/soubory/NKOD/DLP/nkod_dlp_atc.csv',
                    'https://opendata.sukl.cz/soubory/NKOD/DLP/nkod_dlp_lecivelatky.csv'
                ],
                'encoding': 'utf-8',
                'separator': ';'
            },
            
            # SÚKL Monthly updates (střední priorita)
            'monthly_updates': {
                'priority': 2,
                'urls': [
                    'https://opendata.sukl.cz/soubory/DLP_RELEASE/DLP{date}.zip',
                    'https://opendata.sukl.cz/soubory/SODERECEPT/DLPTESTPRODUKCE.zip'
                ],
                'encoding': 'cp1250',
                'separator': ';'
            },
            
            # API Store jako backup (nízká priorita)
            'api_store_backup': {
                'priority': 3,
                'urls': ['https://api.store/czechia-api/sukl.cz/medicines'],
                'format': 'json',
                'requires_transformation': True
            }
        }
        
        self.session = None
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(exist_ok=True, parents=True)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60),
            headers={'User-Agent': 'PillSee/1.0 (+https://pillsee.app)'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_best_data_source(self) -> Tuple[str, Dict]:
        """Najde nejlepší dostupný zdroj dat podle priority a dostupnosti"""
        
        for source_name, source_config in sorted(
            self.data_sources.items(), 
            key=lambda x: x[1]['priority']
        ):
            logger.info(f"Testuji zdroj: {source_name}")
            
            if await self._test_source_availability(source_config):
                logger.info(f"✅ Nejlepší zdroj: {source_name}")
                return source_name, source_config
                
        logger.warning("⚠️ Žádný zdroj není dostupný")
        return None, None
    
    async def _test_source_availability(self, source_config: Dict) -> bool:
        """Test dostupnosti zdroje dat"""
        urls = source_config['urls']
        
        for url in urls[:1]:  # Testuj pouze první URL
            try:
                # Pro date placeholdery použij aktuální datum
                if '{date}' in url:
                    date_str = datetime.now().strftime('%Y%m%d')
                    url = url.format(date=date_str)
                
                async with self.session.head(url) as response:
                    if response.status == 200:
                        return True
                        
            except Exception as e:
                logger.debug(f"Zdroj {url} nedostupný: {e}")
                continue
                
        return False
    
    async def download_enhanced_data(self) -> Optional[pd.DataFrame]:
        """Stáhne data z nejlepšího dostupného zdroje s vylepšeními"""
        
        source_name, source_config = await self.get_best_data_source()
        
        if not source_config:
            logger.error("Žádný zdroj dat není dostupný")
            return None
            
        logger.info(f"Stahuji data ze zdroje: {source_name}")
        
        # Stažení podle typu zdroje
        if source_config.get('format') == 'json':
            return await self._download_json_source(source_config)
        else:
            return await self._download_csv_source(source_config)
    
    async def _download_csv_source(self, source_config: Dict) -> Optional[pd.DataFrame]:
        """Stažení a zpracování CSV zdrojů"""
        
        urls = source_config['urls']
        encoding = source_config.get('encoding', 'utf-8')
        separator = source_config.get('separator', ';')
        
        combined_data = []
        
        for url in urls:
            try:
                # Handle date placeholders
                if '{date}' in url:
                    # Zkusí několik posledních dat
                    for days_back in range(10):
                        date = datetime.now() - timedelta(days=days_back)
                        date_url = url.format(date=date.strftime('%Y%m%d'))
                        
                        async with self.session.get(date_url) as response:
                            if response.status == 200:
                                url = date_url
                                break
                    else:
                        continue  # Žádné datum nefungovalo
                
                logger.info(f"Stahuji: {url}")
                
                async with self.session.get(url) as response:
                    if response.status != 200:
                        continue
                        
                    content = await response.text(encoding=encoding)
                    
                    # Zpracování CSV
                    if url.endswith('.zip'):
                        df = await self._process_zip_content(content, separator)
                    else:
                        df = pd.read_csv(
                            pd.StringIO(content), 
                            sep=separator,
                            encoding=encoding,
                            dtype=str,  # Zachování všech dat jako string
                            on_bad_lines='skip'
                        )
                    
                    if not df.empty:
                        combined_data.append(df)
                        logger.info(f"✅ Načteno {len(df)} záznamů z {url}")
                        
            except Exception as e:
                logger.warning(f"Chyba při stahování {url}: {e}")
                continue
        
        if combined_data:
            # Spojení všech dataframů
            result_df = pd.concat(combined_data, ignore_index=True)
            result_df = self._normalize_columns(result_df)
            return result_df
            
        return None
    
    async def _download_json_source(self, source_config: Dict) -> Optional[pd.DataFrame]:
        """Stažení a transformace JSON zdroje (API Store)"""
        
        url = source_config['urls'][0]
        
        try:
            # API Store často vyžaduje parametry
            params = {'limit': 1000, 'offset': 0}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Transformace z API Store formátu
                    df = self._transform_api_store_data(data)
                    logger.info(f"✅ Načteno {len(df)} záznamů z API Store")
                    return df
                    
        except Exception as e:
            logger.error(f"Chyba při stahování JSON dat: {e}")
            
        return None
    
    def _transform_api_store_data(self, json_data: Dict) -> pd.DataFrame:
        """Transformuje API Store data do standardního formátu"""
        
        # API Store má jiný formát, mapujeme na SÚKL strukturu
        records = []
        
        items = json_data.get('data', []) if isinstance(json_data, dict) else json_data
        
        for item in items:
            record = {
                'nazev': item.get('name', ''),
                'ucinne_latky': item.get('active_substance', ''),
                'sila': item.get('strength', ''),
                'lekova_forma': item.get('dosage_form', ''),
                'drzitel_rozhodnuti': item.get('registration_holder', ''),
                'registracni_cislo': item.get('registration_number', ''),
                'atc_kod': item.get('atc_code', ''),
                'indikace': item.get('indications', ''),
                'davkovani': item.get('dosage', ''),
                'nezadouci_ucinky': item.get('side_effects', ''),
                'kontraindikace': item.get('contraindications', ''),
                'interakce': item.get('interactions', '')
            }
            records.append(record)
        
        return pd.DataFrame(records)
    
    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalizuje názvy sloupců do standardního formátu"""
        
        # Mapování různých variant názvů sloupců na standardní
        column_mapping = {
            'název': 'nazev',
            'name': 'nazev',
            'nazev_pripravku': 'nazev',
            'leciva_latka': 'ucinne_latky',
            'účinné_látky': 'ucinne_latky',
            'active_ingredients': 'ucinne_latky',
            'léková_forma': 'lekova_forma',
            'dosage_form': 'lekova_forma',
            'forma': 'lekova_forma',
            'síla': 'sila',
            'strength': 'sila',
            'držitel_rozhodnutí': 'drzitel_rozhodnuti',
            'registration_holder': 'drzitel_rozhodnuti',
            'výrobce': 'drzitel_rozhodnuti'
        }
        
        # Aplikuj mapování (case-insensitive)
        df_columns_lower = {col.lower(): col for col in df.columns}
        renamed_columns = {}
        
        for old_name, new_name in column_mapping.items():
            if old_name.lower() in df_columns_lower:
                renamed_columns[df_columns_lower[old_name.lower()]] = new_name
        
        df = df.rename(columns=renamed_columns)
        
        # Základní čištění dat
        string_columns = ['nazev', 'ucinne_latky', 'lekova_forma', 'drzitel_rozhodnuti']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        return df
    
    async def _process_zip_content(self, content: bytes, separator: str) -> pd.DataFrame:
        """Zpracování ZIP archivů s CSV soubory"""
        import zipfile
        import io
        
        combined_df = pd.DataFrame()
        
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
                csv_files = [f for f in zip_file.namelist() if f.endswith('.csv')]
                
                for csv_file in csv_files:
                    with zip_file.open(csv_file) as f:
                        df = pd.read_csv(
                            f, 
                            sep=separator, 
                            encoding='cp1250',
                            dtype=str,
                            on_bad_lines='skip'
                        )
                        
                        if not combined_df.empty:
                            combined_df = pd.concat([combined_df, df], ignore_index=True)
                        else:
                            combined_df = df
                            
        except Exception as e:
            logger.error(f"Chyba při zpracování ZIP: {e}")
            
        return combined_df
    
    async def get_data_with_fallback(self) -> pd.DataFrame:
        """Hlavní metoda s pokročilým fallback systémem"""
        
        # Pokus o stažení skutečných dat
        df = await self.download_enhanced_data()
        
        if df is not None and len(df) > 1000:  # Požadavek na minimální počet záznamů
            logger.info(f"✅ Úspěšně načteno {len(df)} skutečných záznamů")
            
            # Uložení do cache
            cache_path = self.cache_dir / f"sukl_data_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(cache_path, index=False, encoding='utf-8')
            
            return df
        
        # Fallback na cache
        logger.warning("🔄 Používám cached data")
        cached_df = await self._load_from_cache()
        if cached_df is not None:
            return cached_df
        
        # Ultimate fallback na rozšířená mock data
        logger.warning("🔧 Používám rozšířená mock data")
        return self._create_enhanced_mock_data()
    
    async def _load_from_cache(self) -> Optional[pd.DataFrame]:
        """Načte nejnovější data z cache"""
        
        cache_files = list(self.cache_dir.glob("sukl_data_*.csv"))
        if not cache_files:
            return None
            
        # Seřaď podle data
        latest_cache = max(cache_files, key=lambda x: x.stat().st_mtime)
        
        # Zkontroluj stáří (max 7 dní)
        age_days = (datetime.now().timestamp() - latest_cache.stat().st_mtime) / 86400
        if age_days > 7:
            logger.warning("Cache data jsou příliš stará")
            return None
            
        try:
            df = pd.read_csv(latest_cache, encoding='utf-8')
            logger.info(f"✅ Načteno {len(df)} záznamů z cache")
            return df
        except Exception as e:
            logger.error(f"Chyba při načítání cache: {e}")
            return None
    
    def _create_enhanced_mock_data(self) -> pd.DataFrame:
        """Vytvoří rozšířená mock data pro fallback"""
        
        # Ještě více realistických českých léků pro lepší testování
        mock_data = {
            'nazev': [
                'PARALEN 500MG', 'BRUFEN 400MG', 'ASPIRIN 100MG', 'IBALGIN 400MG',
                'VOLTAREN EMULGEL 1%', 'NUROFEN 200MG', 'ACYLPYRIN 500MG', 'TRAMAL 50MG',
                'COLDREX', 'THERAFLU', 'IMODIUM 2MG', 'DULCOLAX 5MG',
                'STREPSILS', 'SEPTOLETE', 'OTRIVIN 0,1%', 'NASIVIN 0,05%',
                'FASTUM GEL 2,5%', 'BENGAY KRÉM', 'DOLGIT KRÉM 5%', 'WOBENZYM',
                'CELASKON 1000MG', 'BEROCCA', 'PHARMATON', 'GERIMAX',
                'ALGIFEN 400MG', 'IBUPROM 200MG', 'TANTUM VERDE', 'DITHIADEN',
                'MUCOSOLVAN', 'BРОНХИПРЕТ', 'STOPANGIN', 'KORYLAN',
                'LEVOCETIRIZIN 5MG', 'DESLORATADIN 5MG', 'XYZAL', 'AERIUS',
                'OMEPRAZOL 20MG', 'LANSOPRAZOL 30MG', 'PANTOPRAZOL 40MG', 'ESOMEPRAZOL 40MG'
            ],
            'ucinne_latky': [
                'Paracetamolum', 'Ibuprofenum', 'Acidum acetylsalicylicum', 'Ibuprofenum',
                'Diclofenac natricum', 'Ibuprofenum', 'Acidum acetylsalicylicum', 'Tramadolum',
                'Paracetamolum + Phenylephrinuم', 'Paracetamolum', 'Loperamidium', 'Bisacodylum',
                'Amylmetacresolum', 'Benzydaminum', 'Xylometazolinium', 'Oxymetazolinium',
                'Ketoprofenum', 'Methyl salicylas', 'Ibuprofenum', 'Pancreatin + Tripsin',
                'Acidum ascorbicum', 'B-complex + C', 'Ginseng + vitaminy', 'Multivitaminy',
                'Ibuprofenum', 'Ibuprofenum', 'Benzydaminum', 'Dimetindenum',
                'Ambroxolum', 'Thymus + Primula', 'Tyrothricinum', 'Dihydroergocristinum',
                'Levocetirizinum', 'Desloratadinum', 'Levocetirizinum', 'Desloratadinum',
                'Omeprazolum', 'Lansoprazolum', 'Pantoprazolum', 'Esomeprazolum'
            ],
            'indikace': [
                'Mírná až středně silná bolest, horečka',
                'Bolest, zánět, horečka',
                'Prevence kardiovaskulárních příhod',
                'Bolest, zánět, horečka',
                'Lokální léčba bolesti svalů a kloubů',
                'Bolest, horečka u dětí a dospělých',
                'Bolest, horečka, zánětlivé stavy',
                'Středně silná až silná bolest',
                'Příznaky nachlazení a chřipky',
                'Symptomatická léčba chřipky',
                'Akutní a chronický průjem',
                'Obstipace, zácpa',
                'Bolest v krku, záněty dutiny ústní',
                'Zánět dutiny ústní a hltanu',
                'Nosní kongesce, rýma',
                'Nosní kongesce u kojenců',
                'Povrchová flebitida, kontúze',
                'Revmatická bolest svalů',
                'Lokální protizánětlivá léčba',
                'Poruchy trávení, enzymová terapie',
                'Prevence a léčba nedostatku vitamínu C',
                'Nedostatek vitamínů skupiny B',
                'Únava, vyčerpání, rekonvalescence',
                'Zlepšení paměti, koncentrace',
                'Bolest, zánět, horečka',
                'Bolest, horečka',
                'Bolest v krku a dutině ústní',
                'Alergické reakce, svědění',
                'Produktivní kašel',
                'Kašel, nachlazení',
                'Infekce dutiny ústní a hltanu',
                'Migréna, bolest hlavy',
                'Alergická rýma, kopřivka',
                'Alergická rýma, kopřivka',
                'Alergická rýma, kopřivka',
                'Alergická rýma, kopřivka',
                'Žaludeční vředy, refluxní choroba',
                'Žaludeční vředy, refluxní choroba',
                'Žaludeční vředy, refluxní choroba',
                'Žaludeční vředy, refluxní choroba'
            ]
        }
        
        df = pd.DataFrame(mock_data)
        
        # Přidání dalších sloupců
        df['lekova_forma'] = ['Potahované tablety'] * len(df)
        df['drzitel_rozhodnuti'] = ['Mock Pharma Ltd.'] * len(df)
        df['registracni_cislo'] = [f'MOCK/{i:04d}/TEST' for i in range(len(df))]
        df['atc_kod'] = ['N02BE01'] * len(df)  # Simplified
        
        logger.info(f"✅ Vytvořeno {len(df)} enhanced mock záznamů")
        return df

# Rozšíření současného SUKLDataProcessor
async def enhance_current_sukl_integration():
    """Funkce pro rozšíření současné implementace"""
    
    async with EnhancedSUKLProcessor() as processor:
        # Získání dat s pokročilým fallback systémem  
        df = await processor.get_data_with_fallback()
        
        if df is not None:
            # Integrace s současným vector store systémem
            # Toto by se připojilo k současnému MedicationVectorStore
            return df
        
    return None

if __name__ == "__main__":
    # Test enhanced processoru
    async def test():
        async with EnhancedSUKLProcessor() as processor:
            df = await processor.get_data_with_fallback()
            print(f"Načteno {len(df)} záznamů")
            print("Sloupce:", list(df.columns))
            print("Ukázka dat:")
            print(df.head())
    
    asyncio.run(test())