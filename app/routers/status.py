from fastapi import APIRouter, Depends, HTTPException, status

from .. import models

router = APIRouter(tags=["Informational"])

@router.get("/status", response_model=models.StatusOut)
def status():
    return {
        "status" : "OK", 
        "message": "All Korrekt", 
        "version": 1
        }
