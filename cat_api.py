from fastapi import HTTPException
import httpx

THE_CAT_API_URL = "https://api.thecatapi.com/v1/breeds"

async def validate_breed(breed: str):
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(THE_CAT_API_URL)
            resp.raise_for_status()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Breed service unavailable: {e}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Breed service error")

        breeds = {item["name"] for item in resp.json()}

    if breed not in breeds:
        raise HTTPException(status_code=422, detail=f"Unknown cat breed: {breed}")