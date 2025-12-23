import httpx
import os
import asyncio

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://facel-soporte-ia.fastmcp.app/mcp")

async def get_mcp_token():
    url = f"https://facel-soporte-ia.fastmcp.app/mcp/oauth/token"  # revisa tu endpoint real de token
    data = {
        "grant_type": "password",
        "username": str("octavio.gastelum@tectijuana.edu.mx"),
        "password": str("1234!Pass")
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data=data)
        resp.raise_for_status()  # lanza error si no es 200
        token_info = resp.json()
        print(token_info["access_token"])  # usualmente viene en "access_token"

if __name__ == "__main__":
    asyncio.run(get_mcp_token())