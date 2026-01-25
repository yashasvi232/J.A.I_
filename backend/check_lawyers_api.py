#!/usr/bin/env python3
"""
Check what lawyers are returned by the API
"""

import asyncio
import httpx

async def check_lawyers_api():
    async with httpx.AsyncClient() as client:
        response = await client.get('http://localhost:8001/api/public/lawyers')
        
        if response.status_code == 200:
            data = response.json()
            lawyers = data.get('lawyers', [])
            print(f'API returned {len(lawyers)} lawyers:')
            print()
            
            for i, lawyer in enumerate(lawyers, 1):
                print(f'{i}. ID: {lawyer.get("id", "no id")}')
                print(f'   Name: {lawyer.get("first_name", "unknown")} {lawyer.get("last_name", "unknown")}')
                print(f'   Email: {lawyer.get("email", "unknown")}')
                print(f'   Specializations: {lawyer.get("specializations", [])}')
                print()
        else:
            print(f'API call failed: {response.status_code}')
            print(response.text)

if __name__ == "__main__":
    asyncio.run(check_lawyers_api())