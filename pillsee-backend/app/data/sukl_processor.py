"""
SÚKL Data Processor - Zpracování českých lékových dat
Zvládá win-1250 encoding a strukturuje data pro vector embedding
"""

import pandas as pd
import chardet
import logging
import os
from typing import List, Dict, Optional
from pathlib import Path

from ..models import SUKLDataRecord, MedicationInfo

logger = logging.getLogger(__name__)

class SUKLDataProcessor:
    """Processor pro zpracování SÚKL CSV dat s českým kódováním"""
    
    def __init__(self, data_dir: str = "data"):
        self.encoding = 'windows-1250'  # SÚKL používá win-1250
        self.data_dir = Path(data_dir)
        self.supported_encodings = ['windows-1250', 'utf-8', 'iso-8859-2', 'cp1252']
        
    def load_sukl_csv(self, file_path: str) -> pd.DataFrame:
        """
        Načíst SÚKL CSV data se správným kódováním
        
        Args:
            file_path: Cesta k SÚKL CSV souboru
            
        Returns:
            pd.DataFrame: Načtená a očištěná data
            
        Raises:
            FileNotFoundError: Pokud soubor neexistuje
            ValueError: Pokud data nelze načíst
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"SÚKL CSV soubor nenalezen: {file_path}")
            
        logger.info(f"Načítám SÚKL data z: {file_path}")
        
        # Pokus o detekci encoding
        detected_encoding = self._detect_encoding(file_path)
        
        # Postupně zkouším různá kódování a oddělovače
        for encoding in [detected_encoding] + self.supported_encodings:
            if encoding is None:
                continue
                
            # Zkusíme různé oddělovače (čárka pro NKOD, středník pro starší data)
            for separator in [',', ';', '\t']:
                try:
                    logger.debug(f"Zkouším kódování: {encoding} s oddělovačem '{separator}'")
                    df = pd.read_csv(
                        file_path, 
                        encoding=encoding,
                        sep=separator,
                        low_memory=False
                    )
                    
                    # Pokud má více než 5 sloupců, pravděpodobně je to správné
                    if len(df.columns) > 5:
                        logger.info(f"Úspěšně načteno {len(df)} záznamů s kódováním {encoding} a oddělovačem '{separator}'")
                        return self._clean_czech_text(df)
                        
                except (UnicodeDecodeError, UnicodeError) as e:
                    logger.debug(f"Kódování {encoding} s oddělovačem '{separator}' selhalo: {e}")
                    continue
                except Exception as e:
                    logger.debug(f"Chyba při načítání s {encoding} a '{separator}': {e}")
                    continue
                
        # Fallback s ignore errory
        try:
            logger.warning("Používám fallback s ignorováním chyb")
            df = pd.read_csv(
                file_path, 
                encoding=self.encoding, 
                sep=';',
                errors='ignore',
                low_memory=False
            )
            return self._clean_czech_text(df)
        except Exception as e:
            raise ValueError(f"Nepodařilo se načíst SÚKL data: {e}")
    
    def _detect_encoding(self, file_path: str) -> Optional[str]:
        """Detekce kódování souboru"""
        try:
            with open(file_path, 'rb') as f:
                # Přečti prvních 100KB pro detekci
                raw_data = f.read(100000)
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                confidence = result['confidence']
                
                logger.debug(f"Detekované kódování: {encoding} (confidence: {confidence:.2f})")
                
                # Pouze pokud jsme si jisti
                if confidence > 0.8:
                    return encoding
                    
        except Exception as e:
            logger.debug(f"Detekce kódování selhala: {e}")
            
        return None
  
    def _clean_czech_text(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Čištění a normalizace českého textu
        
        Args:
            df: Vstupní DataFrame
            
        Returns:
            pd.DataFrame: Očištěný DataFrame
        """
        logger.info("Čistím a normalizuji české texty")
        
        # Kopie pro bezpečnost
        df = df.copy()
        
        # Čištění textových sloupců
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].dtype == 'object':
                # Trim whitespace
                df[col] = df[col].astype(str).str.strip()
                
                # Nahrazení prázdných stringů NaN
                df[col] = df[col].replace(['', 'nan', 'NaN', 'null', 'NULL'], pd.NA)
                
                # Normalizace českých znaków (případně)
                # Ponecháváme české znaky - neodstraňujeme diakritiku
                # df[col] = df[col].str.normalize('NFD').str.encode('ascii', errors='ignore').str.decode('ascii')
                
        # Odstranění úplně prázdných řádků
        df = df.dropna(how='all')
        
        logger.info(f"Očištěno, zbývá {len(df)} záznamů")
        return df
    
    def extract_medication_info(self, df: pd.DataFrame) -> List[MedicationInfo]:
        """
        Extrakce strukturovaných informací o lécích pro embedding
        
        Args:
            df: SÚKL DataFrame
            
        Returns:
            List[MedicationInfo]: Seznam strukturovaných informací o lécích
        """
        logger.info("Extraktuji informace o lécích")
        medications = []
        
        # Mapování SÚKL sloupců na naše modely 
        # Podporuje jak testovací data, tak skutečné SÚKL NKOD formáty
        column_mapping = {
            'name': ['NAZEV', 'nazev', 'název'],
            'active_ingredient': ['UCINNE_LATKY', 'ucinne_latky', 'účinné_látky'], 
            'strength': ['SILA', 'sila', 'síla'],
            'form': ['LEKOVA_FORMA', 'lekova_forma', 'léková_forma', 'FORMA'],
            'manufacturer': ['DRZITEL_ROZHODNUTI', 'drzitel_rozhodnuti', 'držitel_rozhodnutí', 'DRZ'],
            'registration_number': ['REGISTRACNI_CISLO', 'registracni_cislo', 'registrační_číslo', 'REG'],
            'atc_code': ['ATC_KOD', 'atc_kod', 'atc_kód', 'ATC_WHO'],
            'indication': ['INDIKACE', 'indikace'],
            'contraindication': ['KONTRAINDIKACE', 'kontraindikace'], 
            'side_effects': ['NEZADOUCI_UCINKY', 'nezadouci_ucinky', 'nežádoucí_účinky'],
            'interactions': ['INTERAKCE', 'interakce'],
            'dosage': ['DAVKOVANI', 'davkovani', 'dávkování'],
            'price': ['CENA', 'cena'],
            'prescription_required': ['PREDPISOVOST', 'predpisovost', 'VYDEJ'],
            
            # Další pole z oficiálního SÚKL NKOD
            'packaging': ['BALENI'],
            'route': ['CESTA'],
            'supplement': ['DOPLNEK'],
            'container': ['OBAL'],
            'code': ['KOD_SUKL'],
            'human': ['H'],
            'expiration': ['V_PLATDO'],
            'unlimited': ['NEOMEZ'],
            'ean': ['EAN']
        }
        
        # Zjištění dostupných sloupců
        available_columns = df.columns.tolist()
        logger.debug(f"Dostupné sloupce: {available_columns}")
        
        # Mapování skutečných sloupců
        actual_mapping = {}
        for our_field, possible_cols in column_mapping.items():
            for col in possible_cols:
                if col in available_columns:
                    actual_mapping[our_field] = col
                    break
        
        logger.debug(f"Použité mapování: {actual_mapping}")
        
        for idx, row in df.iterrows():
            try:
                # Vytvoření medication info
                med_data = {}
                for our_field, sukl_col in actual_mapping.items():
                    value = row.get(sukl_col, '')
                    # Konverze na string a čištění
                    if pd.notna(value) and str(value).strip():
                        med_data[our_field] = str(value).strip()
                    else:
                        med_data[our_field] = None
                
                # Validace minimálních požadavků
                # Pro skutečná SÚKL data stačí název a ATC kód (nejsou účinné látky přímo)
                if not med_data.get('name'):
                    logger.debug(f"Řádek {idx}: chybí název, přeskakuji")
                    continue
                
                # Pro testovací data vyžadujeme účinnou látku
                # Pro skutečná SÚKL data můžeme použít ATC kód místo účinné látky
                if not med_data.get('active_ingredient') and not med_data.get('atc_code'):
                    logger.debug(f"Řádek {idx}: chybí účinná látka i ATC kód, přeskakuji")
                    continue
                
                medication = MedicationInfo(**med_data)
                medications.append(medication)
                
            except Exception as e:
                logger.warning(f"Chyba při zpracování řádku {idx}: {e}")
                continue
        
        logger.info(f"Extraktováno {len(medications)} platných záznamů o lécích")
        return medications
    
    def create_embedding_texts(self, medications: List[MedicationInfo]) -> List[Dict[str, any]]:
        """
        Vytvoření textů pro embedding do vector database
        
        Args:
            medications: Seznam informací o lécích
            
        Returns:
            List[Dict]: Dokumenty připravené pro embedding
        """
        logger.info("Připravuji texty pro embedding")
        documents = []
        
        for med in medications:
            # Vytvoření komplexního textu pro embedding
            text_parts = []
            
            if med.name:
                text_parts.append(f"Název: {med.name}")
            if med.active_ingredient:
                text_parts.append(f"Účinná látka: {med.active_ingredient}")
            elif med.atc_code:
                text_parts.append(f"ATC kód: {med.atc_code}")
            if med.strength:
                text_parts.append(f"Síla: {med.strength}")
            if med.form:
                text_parts.append(f"Léková forma: {med.form}")
            if med.manufacturer:
                text_parts.append(f"Výrobce: {med.manufacturer}")
            if med.indication:
                text_parts.append(f"Indikace: {med.indication}")
            if med.contraindication:
                text_parts.append(f"Kontraindikace: {med.contraindication}")
            if med.side_effects:
                text_parts.append(f"Nežádoucí účinky: {med.side_effects}")
            if med.interactions:
                text_parts.append(f"Interakce: {med.interactions}")
            if med.dosage:
                text_parts.append(f"Dávkování: {med.dosage}")
                
            content = "\n".join(text_parts)
            
            # Metadata pro referenci
            metadata = {
                "name": med.name,
                "active_ingredient": med.active_ingredient,
                "registration_number": med.registration_number,
                "atc_code": med.atc_code,
                "prescription_required": med.prescription_required
            }
            
            documents.append({
                "content": content,
                "metadata": metadata
            })
        
        logger.info(f"Připraveno {len(documents)} dokumentů pro embedding")
        return documents
    
    def download_sukl_data(self, output_path: str = None) -> str:
        """
        Stáhne nejnovější SÚKL data (placeholder - implementace podle dostupného API)
        
        Args:
            output_path: Cesta kam uložit stažená data
            
        Returns:
            str: Cesta k staženému souboru
        """
        # TODO: Implementovat skutečné stahování z SÚKL API nebo scrapu
        
        logger.warning("Stahování SÚKL dat není ještě implementováno")
        logger.info("Pro testování použijte: https://opendata.sukl.cz/")
        
        if not output_path:
            output_path = self.data_dir / "sukl_data.csv"
            
        # Prozatím vytvoří dummy CSV pro testování
        dummy_data = {
            'NAZEV': ['PARALEN 500MG', 'BRUFEN 400MG', 'ASPIRIN 100MG'],
            'UCINNE_LATKY': ['Paracetamolum', 'Ibuprofenum', 'Acidum acetylsalicylicum'], 
            'SILA': ['500 mg', '400 mg', '100 mg'],
            'LEKOVA_FORMA': ['Potahované tablety', 'Potahované tablety', 'Tablety'],
            'DRZITEL_ROZHODNUTI': ['Zentiva, k.s.', 'Mylan Ireland Limited', 'Bayer AG'],
            'REGISTRACNI_CISLO': ['16/123/69-C', '83/456/92-C', '12/789/84-C']
        }
        
        dummy_df = pd.DataFrame(dummy_data)
        dummy_df.to_csv(output_path, sep=';', encoding='windows-1250', index=False)
        
        logger.info(f"Vytvořen testovací soubor: {output_path}")
        return str(output_path)