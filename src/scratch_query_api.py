import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        # Get astrologers
        r = await client.get('http://localhost:8001/api/v1/astrologers/')
        astros = r.json()
        print("Astrologers:", astros)
        if astros:
            astro_id = astros[0]['user_id']
            r = await client.get(f'http://localhost:8001/api/v1/astrologers/{astro_id}/availability')
            print("Availability:", r.json())

if __name__ == '__main__':
    asyncio.run(main())
