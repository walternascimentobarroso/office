#!/usr/bin/env python3
"""Manual smoke test for POST /reports/mapa-diario."""

import asyncio

import httpx


async def test_endpoint() -> None:
    data = {
        "meta": {"empresa": "Test Company", "mes": 1},
        "entries": [
            {
                "day": 1,
                "description": "Test entry",
                "location": "Office",
                "start_time": "09:00",
                "end_time": "17:00",
            }
        ],
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/reports/mapa-diario",
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
