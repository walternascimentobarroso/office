#!/usr/bin/env python3
"""Manual smoke test for POST /reports/daily-report."""

import asyncio

import httpx


async def test_endpoint() -> None:
    data = {
        "company": {
            "name": "Test Company",
            "tax_id": "123456789",
            "address": "1 Test St",
        },
        "employee": {
            "name": "Test Employee",
            "tax_id": "987654321",
            "address": "2 Test St",
        },
        "month": 1,
        "entries": [
            {
                "day": 1,
                "description": "Test entry",
                "location": "Office",
                "start_time": "09:00",
                "end_time": "17:00",
            }
        ],
        "holidays": [],
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/reports/daily-report",
                json=data,
            )
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Content-Length: {len(response.content)} bytes")
            if response.status_code == 200:
                print("Success: Excel file generated.")
                with open("test.xlsx", "wb") as f:
                    f.write(response.content)
                print("File saved as test.xlsx")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Connection error: {e}")


if __name__ == "__main__":
    asyncio.run(test_endpoint())
