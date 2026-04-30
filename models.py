from pydantic import BaseModel, Field
from typing import Optional

class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class FasilitasCreate(BaseModel):
    nama: str = Field(..., min_length=3)
    jenis: str
    alamat: Optional[str] = None
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)

class FasilitasUpdate(BaseModel):
    nama: Optional[str] = None
    jenis: Optional[str] = None
    alamat: Optional[str] = None
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    latitude: Optional[float] = Field(None, ge=-90, le=90)

class FasilitasResponse(BaseModel):
    id: int
    nama: str
    jenis: str
    alamat: Optional[str]
    longitude: float
    latitude: float