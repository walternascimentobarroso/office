# -*- coding: utf-8 -*-
"""Unit tests for configuration module"""

import pytest
import tempfile
import os
from pathlib import Path
from src.core.config import Config
from src.core.exceptions import TemplateLoadError


class TestConfig:
    """Tests for Config initialization and validation"""

    def test_config_with_valid_paths(self):
        """Test Config initialization with valid paths"""
        # Create temporary files
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "template.xlsx"
            header_mapping = Path(tmpdir) / "header.json"
            rows_mapping = Path(tmpdir) / "rows.json"
            footer_mapping = Path(tmpdir) / "footer.json"
            
            template_path.touch()
            
            # Create valid JSON mapping files
            import json
            with open(header_mapping, 'w') as f:
                json.dump({"empresa": "B1"}, f)
            
            with open(rows_mapping, 'w') as f:
                json.dump({"start_row": 8, "columns": {"day": "A"}}, f)

            with open(footer_mapping, 'w') as f:
                json.dump({"ultimo_dia_util_mes": "N47"}, f)
            
            # Set environment variables
            old_template = os.environ.get("TEMPLATE_PATH")
            old_header = os.environ.get("HEADER_MAPPING_PATH")
            old_rows = os.environ.get("ROWS_MAPPING_PATH")
            old_footer = os.environ.get("FOOTER_MAPPING_PATH")
            
            try:
                os.environ["TEMPLATE_PATH"] = str(template_path)
                os.environ["HEADER_MAPPING_PATH"] = str(header_mapping)
                os.environ["ROWS_MAPPING_PATH"] = str(rows_mapping)
                os.environ["FOOTER_MAPPING_PATH"] = str(footer_mapping)
                
                config = Config()
                
                assert config.template_path == str(template_path)
                assert config.header_mapping_path == str(header_mapping)
                assert config.rows_mapping_path == str(rows_mapping)
                assert config.footer_mapping_path == str(footer_mapping)
            finally:
                if old_template:
                    os.environ["TEMPLATE_PATH"] = old_template
                else:
                    os.environ.pop("TEMPLATE_PATH", None)
                if old_header:
                    os.environ["HEADER_MAPPING_PATH"] = old_header
                else:
                    os.environ.pop("HEADER_MAPPING_PATH", None)
                if old_rows:
                    os.environ["ROWS_MAPPING_PATH"] = old_rows
                else:
                    os.environ.pop("ROWS_MAPPING_PATH", None)
                if old_footer:
                    os.environ["FOOTER_MAPPING_PATH"] = old_footer
                else:
                    os.environ.pop("FOOTER_MAPPING_PATH", None)

    def test_config_missing_template(self):
        """Test Config raises TemplateLoadError when template is missing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import json
            header_mapping = Path(tmpdir) / "header.json"
            rows_mapping = Path(tmpdir) / "rows.json"
            footer_mapping = Path(tmpdir) / "footer.json"
            template_path = Path(tmpdir) / "template.xlsx"
            
            with open(header_mapping, 'w') as f:
                json.dump({"empresa": "B1"}, f)
            with open(rows_mapping, 'w') as f:
                json.dump({"start_row": 8, "columns": {}}, f)
            with open(footer_mapping, 'w') as f:
                json.dump({"ultimo_dia_util_mes": "N47"}, f)
            # Don't create template
            
            old_template = os.environ.get("TEMPLATE_PATH")
            old_header = os.environ.get("HEADER_MAPPING_PATH")
            old_rows = os.environ.get("ROWS_MAPPING_PATH")
            old_footer = os.environ.get("FOOTER_MAPPING_PATH")
            
            try:
                os.environ["TEMPLATE_PATH"] = str(template_path)
                os.environ["HEADER_MAPPING_PATH"] = str(header_mapping)
                os.environ["ROWS_MAPPING_PATH"] = str(rows_mapping)
                os.environ["FOOTER_MAPPING_PATH"] = str(footer_mapping)
                
                with pytest.raises(TemplateLoadError) as exc_info:
                    Config()
                assert "template" in str(exc_info.value).lower()
            finally:
                if old_template:
                    os.environ["TEMPLATE_PATH"] = old_template
                else:
                    os.environ.pop("TEMPLATE_PATH", None)
                if old_header:
                    os.environ["HEADER_MAPPING_PATH"] = old_header
                else:
                    os.environ.pop("HEADER_MAPPING_PATH", None)
                if old_rows:
                    os.environ["ROWS_MAPPING_PATH"] = old_rows
                else:
                    os.environ.pop("ROWS_MAPPING_PATH", None)
                if old_footer:
                    os.environ["FOOTER_MAPPING_PATH"] = old_footer
                else:
                    os.environ.pop("FOOTER_MAPPING_PATH", None)

    def test_config_missing_header_mapping(self):
        """Test Config raises TemplateLoadError when header mapping is missing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "template.xlsx"
            header_mapping = Path(tmpdir) / "header.json"
            rows_mapping = Path(tmpdir) / "rows.json"
            footer_mapping = Path(tmpdir) / "footer.json"
            
            import json
            template_path.touch()
            with open(rows_mapping, 'w') as f:
                json.dump({"start_row": 8, "columns": {}}, f)
            with open(footer_mapping, 'w') as f:
                json.dump({"ultimo_dia_util_mes": "N47"}, f)
            # Don't create header mapping
            
            old_template = os.environ.get("TEMPLATE_PATH")
            old_header = os.environ.get("HEADER_MAPPING_PATH")
            old_rows = os.environ.get("ROWS_MAPPING_PATH")
            old_footer = os.environ.get("FOOTER_MAPPING_PATH")
            
            try:
                os.environ["TEMPLATE_PATH"] = str(template_path)
                os.environ["HEADER_MAPPING_PATH"] = str(header_mapping)
                os.environ["ROWS_MAPPING_PATH"] = str(rows_mapping)
                os.environ["FOOTER_MAPPING_PATH"] = str(footer_mapping)
                
                with pytest.raises(TemplateLoadError) as exc_info:
                    Config()
                assert "header" in str(exc_info.value).lower()
            finally:
                if old_template:
                    os.environ["TEMPLATE_PATH"] = old_template
                else:
                    os.environ.pop("TEMPLATE_PATH", None)
                if old_header:
                    os.environ["HEADER_MAPPING_PATH"] = old_header
                else:
                    os.environ.pop("HEADER_MAPPING_PATH", None)
                if old_rows:
                    os.environ["ROWS_MAPPING_PATH"] = old_rows
                else:
                    os.environ.pop("ROWS_MAPPING_PATH", None)
                if old_footer:
                    os.environ["FOOTER_MAPPING_PATH"] = old_footer
                else:
                    os.environ.pop("FOOTER_MAPPING_PATH", None)

    def test_config_missing_rows_mapping(self):
        """Test Config raises TemplateLoadError when rows mapping is missing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "template.xlsx"
            header_mapping = Path(tmpdir) / "header.json"
            rows_mapping = Path(tmpdir) / "rows.json"
            footer_mapping = Path(tmpdir) / "footer.json"
            
            import json
            template_path.touch()
            with open(header_mapping, 'w') as f:
                json.dump({"empresa": "B1"}, f)
            with open(footer_mapping, 'w') as f:
                json.dump({"ultimo_dia_util_mes": "N47"}, f)
            # Don't create rows mapping
            
            old_template = os.environ.get("TEMPLATE_PATH")
            old_header = os.environ.get("HEADER_MAPPING_PATH")
            old_rows = os.environ.get("ROWS_MAPPING_PATH")
            old_footer = os.environ.get("FOOTER_MAPPING_PATH")
            
            try:
                os.environ["TEMPLATE_PATH"] = str(template_path)
                os.environ["HEADER_MAPPING_PATH"] = str(header_mapping)
                os.environ["ROWS_MAPPING_PATH"] = str(rows_mapping)
                os.environ["FOOTER_MAPPING_PATH"] = str(footer_mapping)
                
                with pytest.raises(TemplateLoadError) as exc_info:
                    Config()
                assert "rows" in str(exc_info.value).lower()
            finally:
                if old_template:
                    os.environ["TEMPLATE_PATH"] = old_template
                else:
                    os.environ.pop("TEMPLATE_PATH", None)
                if old_header:
                    os.environ["HEADER_MAPPING_PATH"] = old_header
                else:
                    os.environ.pop("HEADER_MAPPING_PATH", None)
                if old_rows:
                    os.environ["ROWS_MAPPING_PATH"] = old_rows
                else:
                    os.environ.pop("ROWS_MAPPING_PATH", None)
                if old_footer:
                    os.environ["FOOTER_MAPPING_PATH"] = old_footer
                else:
                    os.environ.pop("FOOTER_MAPPING_PATH", None)

    def test_config_missing_footer_mapping(self):
        """Test Config raises TemplateLoadError when footer mapping is missing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "template.xlsx"
            header_mapping = Path(tmpdir) / "header.json"
            rows_mapping = Path(tmpdir) / "rows.json"
            footer_mapping = Path(tmpdir) / "footer.json"

            import json
            template_path.touch()
            with open(header_mapping, 'w') as f:
                json.dump({"empresa": "B1"}, f)
            with open(rows_mapping, 'w') as f:
                json.dump({"start_row": 8, "columns": {}}, f)
            # Don't create footer mapping

            old_template = os.environ.get("TEMPLATE_PATH")
            old_header = os.environ.get("HEADER_MAPPING_PATH")
            old_rows = os.environ.get("ROWS_MAPPING_PATH")
            old_footer = os.environ.get("FOOTER_MAPPING_PATH")

            try:
                os.environ["TEMPLATE_PATH"] = str(template_path)
                os.environ["HEADER_MAPPING_PATH"] = str(header_mapping)
                os.environ["ROWS_MAPPING_PATH"] = str(rows_mapping)
                os.environ["FOOTER_MAPPING_PATH"] = str(footer_mapping)

                with pytest.raises(TemplateLoadError) as exc_info:
                    Config()
                assert "footer" in str(exc_info.value).lower()
            finally:
                if old_template:
                    os.environ["TEMPLATE_PATH"] = old_template
                else:
                    os.environ.pop("TEMPLATE_PATH", None)
                if old_header:
                    os.environ["HEADER_MAPPING_PATH"] = old_header
                else:
                    os.environ.pop("HEADER_MAPPING_PATH", None)
                if old_rows:
                    os.environ["ROWS_MAPPING_PATH"] = old_rows
                else:
                    os.environ.pop("ROWS_MAPPING_PATH", None)
                if old_footer:
                    os.environ["FOOTER_MAPPING_PATH"] = old_footer
                else:
                    os.environ.pop("FOOTER_MAPPING_PATH", None)

    def test_config_environment_variables(self):
        """Test Config uses environment variables when set"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import json
            template_path = Path(tmpdir) / "template.xlsx"
            header_mapping = Path(tmpdir) / "header.json"
            rows_mapping = Path(tmpdir) / "rows.json"
            footer_mapping = Path(tmpdir) / "footer.json"
            
            template_path.touch()
            with open(header_mapping, 'w') as f:
                json.dump({"empresa": "B1"}, f)
            with open(rows_mapping, 'w') as f:
                json.dump({"start_row": 8, "columns": {}}, f)
            with open(footer_mapping, 'w') as f:
                json.dump({"ultimo_dia_util_mes": "N47"}, f)
            
            # Set environment variables
            old_template = os.environ.get("TEMPLATE_PATH")
            old_header = os.environ.get("HEADER_MAPPING_PATH")
            old_rows = os.environ.get("ROWS_MAPPING_PATH")
            old_footer = os.environ.get("FOOTER_MAPPING_PATH")
            
            try:
                os.environ["TEMPLATE_PATH"] = str(template_path)
                os.environ["HEADER_MAPPING_PATH"] = str(header_mapping)
                os.environ["ROWS_MAPPING_PATH"] = str(rows_mapping)
                os.environ["FOOTER_MAPPING_PATH"] = str(footer_mapping)
                
                config = Config()
                
                assert config.template_path == str(template_path)
                assert config.header_mapping_path == str(header_mapping)
                assert config.rows_mapping_path == str(rows_mapping)
                assert config.footer_mapping_path == str(footer_mapping)
            finally:
                # Restore environment variables
                if old_template:
                    os.environ["TEMPLATE_PATH"] = old_template
                else:
                    os.environ.pop("TEMPLATE_PATH", None)
                if old_header:
                    os.environ["HEADER_MAPPING_PATH"] = old_header
                else:
                    os.environ.pop("HEADER_MAPPING_PATH", None)
                if old_rows:
                    os.environ["ROWS_MAPPING_PATH"] = old_rows
                else:
                    os.environ.pop("ROWS_MAPPING_PATH", None)
                if old_footer:
                    os.environ["FOOTER_MAPPING_PATH"] = old_footer
                else:
                    os.environ.pop("FOOTER_MAPPING_PATH", None)
