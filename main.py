from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
import json
import asyncpg 

from database import get_pool, close_pool
from models import FasilitasCreate, FasilitasUpdate, UserCreate
from auth_utils import create_access_token, get_current_user, pwd_context

@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_pool()
    print("Database Terhubung!")
    yield
    await close_pool()

app = FastAPI(title="WebGIS Fullstack - Piela Nugraha", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register")
async def register(user: UserCreate):
    pool = await get_pool()
    hashed_password = pwd_context.hash(user.password)
    
    async with pool.acquire() as conn:
        try:
            await conn.execute(
                "INSERT INTO users (email, password_hash) VALUES ($1, $2)",
                user.email, hashed_password
            )
            return {"message": "Akun berhasil dibuat! Silakan login."}
        except asyncpg.exceptions.UniqueViolationError:
            raise HTTPException(status_code=400, detail="Email sudah terdaftar")

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    pool = await get_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE email = $1", form_data.username)
        
        if not user or not pwd_context.verify(form_data.password, user['password_hash']):
            raise HTTPException(status_code=401, detail="Email atau password salah")
        
        access_token = create_access_token(data={"sub": user['email']})
        return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/fasilitas/geojson")
async def get_geojson():
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT *, ST_AsGeoJSON(ST_Transform(geom, 4326)) as geojson_geom 
            FROM transportasi.halte
        """)
        
        features = []
        for row in rows:
            row_dict = dict(row)
            
            if 'geom' in row_dict:
                del row_dict['geom']
            if 'geojson_geom' in row_dict:
                del row_dict['geojson_geom']

            features.append({
                "type": "Feature",
                "geometry": json.loads(row['geojson_geom']),
                "properties": row_dict
            })
            
        return {"type": "FeatureCollection", "features": features}

@app.post("/api/fasilitas", status_code=201)
async def create_fasilitas(data: FasilitasCreate, user: str = Depends(get_current_user)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO fasilitas (nama, jenis, alamat, geom)
            VALUES ($1, $2, $3, ST_SetSRID(ST_Point($4, $5), 4326))
            RETURNING id, nama
        """, data.nama, data.jenis, data.alamat, data.longitude, data.latitude)
        return {"message": "Data berhasil ditambah", "data": dict(row)}

@app.delete("/api/fasilitas/{id}", status_code=204)
async def delete_fasilitas(id: int, user: str = Depends(get_current_user)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM fasilitas WHERE id = $1", id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Data tidak ditemukan")
        return None