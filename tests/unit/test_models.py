# -*- coding: utf-8 -*-
"""Unit tests for Pydantic schemas (daily report)."""

import pytest
from pydantic import ValidationError

from src.schemas.daily_report import Company, DailyReportRequest, Employee, Entry


class TestCompany:
    """Tests for Company (CompanyModel) model."""

    def test_company_all_fields(self) -> None:
        company = Company(name="Acme Corp", tax_id="123456", address="Street X")
        assert company.name == "Acme Corp"
        assert company.tax_id == "123456"
        assert company.address == "Street X"

    def test_company_required_fields(self) -> None:
        with pytest.raises(ValidationError):
            Company(name="x")


class TestEmployee:
    """Tests for Employee (EmployeeModel) model."""

    def test_employee_all_fields(self) -> None:
        employee = Employee(name="Ana Costa", address="Street X", tax_id="999")
        assert employee.name == "Ana Costa"
        assert employee.address == "Street X"
        assert employee.tax_id == "999"


class TestEntry:
    """Tests for Entry model."""

    def test_entry_percentage_invalid(self) -> None:
        with pytest.raises(ValidationError):
            Entry(percentage=-1)
        with pytest.raises(ValidationError):
            Entry(percentage=101)


class TestDailyReportRequest:
    """Tests for DailyReportRequest model."""

    def test_valid_request_full_data(self) -> None:
        request = DailyReportRequest(
            company={"name": "Corp", "tax_id": "123", "address": "Street X"},
            employee={"name": "Ana Costa", "tax_id": "999", "address": "Street X"},
            month=3,
            entries=[
                {
                    "day": 1,
                    "description": "Task 1",
                    "location": "Office",
                    "start_time": "09:00",
                    "end_time": "10:00",
                    "percentage": 75,
                },
            ],
        )
        assert len(request.entries) == 1
        assert request.company.name == "Corp"
        assert request.entries[0].percentage == 75

    def test_holidays_normalized_drops_invalid(self) -> None:
        request = DailyReportRequest(
            company={"name": "Corp", "tax_id": "123", "address": "Street X"},
            employee={"name": "Ana Costa", "tax_id": "999", "address": "Street X"},
            month=3,
            holidays=[1, 32, 0, 5],
        )
        assert request.holidays == [1, 5]

    def test_extra_fields_ignored(self) -> None:
        request = DailyReportRequest.model_validate(
            {
                "company": {"name": "Corp", "tax_id": "123", "address": "Street X"},
                "employee": {"name": "Ana", "tax_id": "123", "address": "Address"},
                "month": 3,
                "entries": [],
                "extra_top": "ignored",
            }
        )
        assert "extra_top" not in request.model_dump()
