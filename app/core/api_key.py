from fastapi import Header, HTTPException, status, Depends
import os


async def verify_api_key(x_api_key: str = Header(...)):
    api_key = os.getenv("API_KEY")
    if not api_key or x_api_key != api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
    return True
