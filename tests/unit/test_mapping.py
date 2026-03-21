# -*- coding: utf-8 -*-
"""Unit tests for mapping system"""

import pytest
import json
import tempfile
from pathlib import Path
from src.core.mapping import MappingLoader, _is_valid_cell_address
from src.core.exceptions import MappingError


class TestCellAddressValidation:
    """Tests for cell address validation"""

    def test_valid_cell_addresses(self):
        """Test valid cell addresses"""
        valid_cells = ["A", "A1", "Z99", "AA1", "B10", "D4", "J4", "ZZ999"]
        for cell in valid_cells:
            assert _is_valid_cell_address(cell), f"{cell} should be valid"

    def test_invalid_cell_addresses(self):
        """Test invalid cell addresses"""
        invalid_cells = ["1A", "1", "", "0A", "A-1", "@1", "A 1"]
        for cell in invalid_cells:
            assert not _is_valid_cell_address(cell), f"{cell} should be invalid"


class TestHeaderMappingLoader:
    """Tests for header mapping loader"""

    def test_load_valid_header_mapping(self):
        """Test loading valid header mapping"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "empresa": "B1",
                "nif": "D4",
                "mes": "J4"
            }, f)
            f.flush()
            
            mapping = MappingLoader.load_header_mapping(f.name)
            assert mapping["empresa"] == "B1"
            assert mapping["nif"] == "D4"
            assert mapping["mes"] == "J4"
            
            Path(f.name).unlink()

    def test_load_header_mapping_not_found(self):
        """Test error when header mapping file not found"""
        with pytest.raises(MappingError) as exc_info:
            MappingLoader.load_header_mapping("/nonexistent/path.json")
        assert "not found" in str(exc_info.value)

    def test_load_header_mapping_invalid_json(self):
        """Test error when JSON is invalid"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json {]")
            f.flush()
            
            with pytest.raises(MappingError):
                MappingLoader.load_header_mapping(f.name)
            
            Path(f.name).unlink()

    def test_load_header_mapping_not_dict(self):
        """Test error when mapping is not a dict"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(["not", "a", "dict"], f)
            f.flush()
            
            with pytest.raises(MappingError):
                MappingLoader.load_header_mapping(f.name)
            
            Path(f.name).unlink()

    def test_load_header_mapping_invalid_cell_address(self):
        """Test error when cell address is invalid"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"empresa": "invalid"}, f)
            f.flush()
            
            with pytest.raises(MappingError) as exc_info:
                MappingLoader.load_header_mapping(f.name)
            assert "invalid cell address" in str(exc_info.value).lower()
            
            Path(f.name).unlink()


class TestFooterMappingLoader:
    """Tests for footer mapping loader"""

    def test_load_valid_footer_mapping(self):
        """Test loading valid footer mapping"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "ultimo_dia_util_mes": "N47",
                "nome_completo": "B42",
                "morada": "B43",
                "nif": "D44",
            }, f)
            f.flush()

            mapping = MappingLoader.load_footer_mapping(f.name)
            assert mapping["ultimo_dia_util_mes"] == "N47"
            assert mapping["nome_completo"] == "B42"
            assert mapping["nif"] == "D44"

            Path(f.name).unlink()

    def test_load_footer_mapping_not_found(self):
        """Test error when footer mapping file not found"""
        with pytest.raises(MappingError) as exc_info:
            MappingLoader.load_footer_mapping("/nonexistent/path.json")
        assert "not found" in str(exc_info.value)


class TestRowsMappingLoader:
    """Tests for rows mapping loader"""

    def test_load_valid_rows_mapping(self):
        """Test loading valid rows mapping"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "start_row": 8,
                "columns": {
                    "day": "A",
                    "description": "B",
                    "location": "D",
                    "start_time": "E",
                    "end_time": "J"
                }
            }, f)
            f.flush()
            
            mapping = MappingLoader.load_rows_mapping(f.name)
            assert mapping["start_row"] == 8
            assert mapping["columns"]["day"] == "A"
            assert mapping["columns"]["end_time"] == "J"
            
            Path(f.name).unlink()

    def test_load_rows_mapping_missing_start_row(self):
        """Test error when start_row is missing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"columns": {}}, f)
            f.flush()
            
            with pytest.raises(MappingError) as exc_info:
                MappingLoader.load_rows_mapping(f.name)
            assert "start_row" in str(exc_info.value)
            
            Path(f.name).unlink()

    def test_load_rows_mapping_missing_columns(self):
        """Test error when columns is missing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"start_row": 8}, f)
            f.flush()
            
            with pytest.raises(MappingError) as exc_info:
                MappingLoader.load_rows_mapping(f.name)
            assert "columns" in str(exc_info.value)
            
            Path(f.name).unlink()

    def test_load_rows_mapping_invalid_start_row_type(self):
        """Test error when start_row is not int"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "start_row": "8",
                "columns": {}
            }, f)
            f.flush()
            
            with pytest.raises(MappingError):
                MappingLoader.load_rows_mapping(f.name)
            
            Path(f.name).unlink()

    def test_load_rows_mapping_invalid_start_row_value(self):
        """Test error when start_row is < 1"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "start_row": 0,
                "columns": {}
            }, f)
            f.flush()
            
            with pytest.raises(MappingError):
                MappingLoader.load_rows_mapping(f.name)
            
            Path(f.name).unlink()
