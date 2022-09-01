from fastapi import APIRouter

from .. import models

router = APIRouter(tags=["Informational"])

@router.get("/status", response_model=models.StatusOut)
async def status():
    return {
        "status" : "OK", 
        "message": "All Korrekt", 
        "version": 1
        }
