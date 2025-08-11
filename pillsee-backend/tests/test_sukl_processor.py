"""
Testy pro SÚKL data processor
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os

from app.data.sukl_processor import SUKLDataProcessor
from app.models import MedicationInfo


class TestSUKLDataProcessor:
    
    def setup_method(self):
        """Setup před každým testem"""
        self.processor = SUKLDataProcessor()
    
    def test_create_dummy_data(self):
        """Test vytvoření dummy SÚKL dat"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_sukl.csv")
            result_path = self.processor.download_sukl_data(output_path)
            
            assert os.path.exists(result_path)
            
            # Test načtení vytvořených dat
            df = self.processor.load_sukl_csv(result_path)
            assert len(df) > 0
            assert 'NAZEV' in df.columns
            assert 'UCINNE_LATKY' in df.columns
    
    def test_load_sukl_csv_with_sample(self, sample_sukl_csv):
        """Test načtení SÚKL CSV souboru"""
        df = self.processor.load_sukl_csv(sample_sukl_csv)
        
        assert len(df) == 2
        assert 'NAZEV' in df.columns
        assert 'UCINNE_LATKY' in df.columns
        assert df.iloc[0]['NAZEV'] == 'PARALEN 500MG'
        assert df.iloc[1]['NAZEV'] == 'BRUFEN 400MG'
    
    def test_extract_medication_info(self):
        """Test extrakce informací o lécích"""
        # Vytvoření test dat
        test_data = {
            'NAZEV': ['PARALEN 500MG', 'BRUFEN 400MG'],
            'UCINNE_LATKY': ['Paracetamolum', 'Ibuprofenum'],
            'SILA': ['500 mg', '400 mg'],
            'LEKOVA_FORMA': ['Tablety', 'Tablety']
        }
        df = pd.DataFrame(test_data)
        
        medications = self.processor.extract_medication_info(df)
        
        assert len(medications) == 2
        assert all(isinstance(med, MedicationInfo) for med in medications)
        assert medications[0].name == 'PARALEN 500MG'
        assert medications[0].active_ingredient == 'Paracetamolum'
    
    def test_extract_medication_info_with_missing_data(self):
        """Test extrakce s chybějícími daty"""
        test_data = {
            'NAZEV': ['PARALEN 500MG', '', None],  # Empty and None values
            'UCINNE_LATKY': ['Paracetamolum', 'Ibuprofenum', ''],
            'SILA': ['500 mg', '400 mg', '200 mg']
        }
        df = pd.DataFrame(test_data)
        
        medications = self.processor.extract_medication_info(df)
        
        # Should only extract valid medications (with name and active ingredient)
        assert len(medications) == 1
        assert medications[0].name == 'PARALEN 500MG'
    
    def test_create_embedding_texts(self):
        """Test vytvoření textů pro embedding"""
        medications = [
            MedicationInfo(
                name="PARALEN 500MG",
                active_ingredient="Paracetamolum",
                strength="500 mg",
                form="Tablety"
            )
        ]
        
        documents = self.processor.create_embedding_texts(medications)
        
        assert len(documents) == 1
        assert 'content' in documents[0]
        assert 'metadata' in documents[0]
        assert 'Název: PARALEN 500MG' in documents[0]['content']
        assert documents[0]['metadata']['name'] == 'PARALEN 500MG'
    
    def test_create_embedding_texts_comprehensive(self):
        """Test vytvoření textů s kompletními informacemi"""
        medication = MedicationInfo(
            name="PARALEN 500MG",
            active_ingredient="Paracetamolum",
            strength="500 mg",
            form="Potahované tablety",
            manufacturer="Zentiva, k.s.",
            indication="Mírná až středně silná bolest",
            contraindication="Hypersenzitivita na paracetamol",
            side_effects="Vzácně alergické reakce",
            interactions="Opatrnost při užívání s warfarinem",
            dosage="1-2 tablety až 4x denně"
        )
        
        documents = self.processor.create_embedding_texts([medication])
        content = documents[0]['content']
        
        # Check that all information is included
        assert 'Název: PARALEN 500MG' in content
        assert 'Účinná látka: Paracetamolum' in content
        assert 'Indikace: Mírná až středně silná bolest' in content
        assert 'Kontraindikace: Hypersenzitivita' in content
        assert 'Dávkování: 1-2 tablety' in content
    
    def test_clean_czech_text(self):
        """Test čištění českého textu"""
        test_data = pd.DataFrame({
            'col1': ['  text s mezerami  ', '', 'normální text'],
            'col2': ['NaN', 'platná hodnota', '   ']
        })
        
        cleaned = self.processor._clean_czech_text(test_data)
        
        # Kontrola trim whitespace
        assert cleaned.loc[0, 'col1'] == 'text s mezerami'
        # Prázdné hodnoty by měly být NaN
        assert pd.isna(cleaned.loc[1, 'col1'])
    
    def test_encoding_detection(self):
        """Test detekce kódování souborů"""
        # Test s různými kódováními
        test_content = "NAZEV,UCINNE_LATKY\nParalen,Paracetamol"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            f.flush()
            
            try:
                df = self.processor.load_sukl_csv(f.name)
                assert len(df) == 1
                assert 'NAZEV' in df.columns
            finally:
                os.unlink(f.name)
    
    def test_invalid_file_handling(self):
        """Test zpracování neexistujícího souboru"""
        with pytest.raises(FileNotFoundError):
            self.processor.load_sukl_csv("nonexistent_file.csv")
    
    def test_empty_dataframe_handling(self):
        """Test zpracování prázdného DataFrame"""
        empty_df = pd.DataFrame()
        medications = self.processor.extract_medication_info(empty_df)
        assert len(medications) == 0
    
    def test_czech_characters_handling(self):
        """Test správného zpracování českých znaků"""
        test_data = {
            'NAZEV': ['Léčivo ě š č ř ž ý á í é ů ú'],
            'UCINNE_LATKY': ['Kyselina acetylsalicylová'],
            'SILA': ['100 mg']
        }
        df = pd.DataFrame(test_data)
        
        medications = self.processor.extract_medication_info(df)
        documents = self.processor.create_embedding_texts(medications)
        
        # Should preserve Czech characters
        content = documents[0]['content']
        assert 'Léčivo' in content
        assert 'acetylsalicylová' in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])