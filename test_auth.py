import asyncio
import httpx

async def test_login():
    url = "http://127.0.0.1:8000/auth/token"
    data = {
        "username": "admin@example.com",
        "password": "admin123"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, data=data, headers=headers)
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_login())