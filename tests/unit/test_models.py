# -*- coding: utf-8 -*-
"""Unit tests for Pydantic models"""

import pytest
from src.models.request import Meta, Entry, GenerateExcelRequest
from pydantic import ValidationError


class TestMeta:
    """Tests for Meta model"""

    def test_meta_all_fields(self):
        """Test Meta with all fields provided"""
        meta = Meta(empresa="Acme Corp", nif="123456", mes="March 2026")
        assert meta.empresa == "Acme Corp"
        assert meta.nif == "123456"
        assert meta.mes == "March 2026"

    def test_meta_empty(self):
        """Test Meta with no fields"""
        meta = Meta()
        assert meta.empresa is None
        assert meta.nif is None
        assert meta.mes is None

    def test_meta_partial_fields(self):
        """Test Meta with some fields"""
        meta = Meta(empresa="Test Corp")
        assert meta.empresa == "Test Corp"
        assert meta.nif is None
        assert meta.mes is None

    def test_meta_extra_fields_ignored(self):
        """Test that extra fields are ignored"""
        meta = Meta(empresa="Corp", unknown_field="should_be_ignored", another_unknown="also_ignored")
        assert meta.empresa == "Corp"
        assert not hasattr(meta, "unknown_field")
        assert not hasattr(meta, "another_unknown")


class TestEntry:
    """Tests for Entry model"""

    def test_entry_all_fields(self):
        """Test Entry with all fields"""
        entry = Entry(
            day=1,
            description="Meeting",
            location="Office",
            start_time="09:00",
            end_time="10:00"
        )
        assert entry.day == 1
        assert entry.description == "Meeting"
        assert entry.location == "Office"
        assert entry.start_time == "09:00"
        assert entry.end_time == "10:00"

    def test_entry_empty(self):
        """Test Entry with no fields"""
        entry = Entry()
        assert entry.day is None
        assert entry.description is None
        assert entry.location is None
        assert entry.start_time is None
        assert entry.end_time is None

    def test_entry_day_as_string(self):
        """Test Entry with day as string"""
        entry = Entry(day="15")
        assert entry.day == "15"

    def test_entry_day_as_int(self):
        """Test Entry with day as int"""
        entry = Entry(day=15)
        assert entry.day == 15

    def test_entry_extra_fields_ignored(self):
        """Test that extra fields are ignored"""
        entry = Entry(description="Test", extra_field="ignored")
        assert entry.description == "Test"
        assert not hasattr(entry, "extra_field")


class TestGenerateExcelRequest:
    """Tests for GenerateExcelRequest model"""

    def test_valid_request_full_data(self):
        """Test valid request with full data"""
        request = GenerateExcelRequest(
            meta={"empresa": "Corp", "nif": "123"},
            entries=[
                {"day": 1, "description": "Task 1", "location": "Office", "start_time": "09:00", "end_time": "10:00"},
                {"day": 2, "description": "Task 2", "location": "Home", "start_time": "14:00", "end_time": "16:00"}
            ]
        )
        assert len(request.entries) == 2
        assert request.meta.empresa == "Corp"

    def test_valid_request_empty_entries(self):
        """Test valid request with empty entries"""
        request = GenerateExcelRequest(meta={"empresa": "Corp"}, entries=[])
        assert len(request.entries) == 0

    def test_valid_request_empty_meta(self):
        """Test valid request with empty meta"""
        request = GenerateExcelRequest(meta={}, entries=[])
        assert request.meta.empresa is None

    def test_missing_meta_field(self):
        """Test that missing meta field raises error"""
        with pytest.raises(ValidationError) as exc_info:
            GenerateExcelRequest(entries=[])
        assert "meta" in str(exc_info.value)

    def test_missing_entries_field(self):
        """Test that missing entries field uses default empty list"""
        request = GenerateExcelRequest(meta={})
        assert request.entries == []

    def test_invalid_meta_type(self):
        """Test that invalid meta type raises error"""
        with pytest.raises(ValidationError):
            GenerateExcelRequest(meta="invalid", entries=[])

    def test_invalid_entries_type(self):
        """Test that invalid entries type raises error"""
        with pytest.raises(ValidationError):
            GenerateExcelRequest(meta={}, entries="invalid")

    def test_meta_dict_conversion(self):
        """Test that meta dict is converted to Meta object"""
        request = GenerateExcelRequest(
            meta={"empresa": "Corp", "nif": "123", "mes": "March"},
            entries=[]
        )
        assert isinstance(request.meta, Meta)
        assert request.meta.empresa == "Corp"

    def test_entries_list_conversion(self):
        """Test that entries list items are converted to Entry objects"""
        request = GenerateExcelRequest(
            meta={},
            entries=[{"day": 1, "description": "Test"}]
        )
        assert len(request.entries) == 1
        assert isinstance(request.entries[0], Entry)
        assert request.entries[0].day == 1
