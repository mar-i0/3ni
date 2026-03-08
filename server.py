"""
Servidor sin estado para almacenamiento seguro en 3NI.
Características:
- Sin autenticación centralizada
- Sin registro de IPs
- Sin metadatos persistentes
- Datos ya encriptados (server no ve contenido)
"""

import json
import hashlib
import secrets
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
from pydantic import BaseModel
from typing import Optional
import logging
import asyncio

from storage import MultiStorageBackend
from encryption import E2EEncryption

# Desactivar logging de acceso (privacidad)
logging.getLogger("uvicorn.access").disabled = True

app = FastAPI(title="3NI Secure Server", version="1.0")

# Inicializar backend de almacenamiento distribuido
storage = MultiStorageBackend(
    ipfs_enabled=True,
    storj_enabled=False,
    bittorrent_enabled=True
)

# Cache temporal en memoria (sin persistencia a disco)
# Se limpia automáticamente después de cada sesión
temp_cache = {}


class UploadRequest(BaseModel):
    """Solicitud de carga de datos encriptados."""
    filename: str
    salt: str  # base64 encoded
    file_hash: str  # hex encoded


class RetrievalRequest(BaseModel):
    """Solicitud de recuperación de datos."""
    storage_locations: dict  # {backend: location_id}
    salt: str  # para verificación


@app.post("/api/v1/store")
async def store_encrypted_file(file: UploadFile = File(...)):
    """
    Almacena un archivo ya encriptado en backends distribuidos.

    El cliente DEBE encriptar antes de enviar.
    El servidor NO ve el contenido.

    Retorna:
    - storage_locations: donde se almacenó el archivo
    - retrieval_id: ID único anónimo para recuperación
    """
    try:
        data = await file.read()

        if not data:
            raise HTTPException(status_code=400, detail="Empty file")

        # Generar ID de recuperación anónimo (sin relación con usuario)
        retrieval_id = secrets.token_urlsafe(32)

        # Distribuir en múltiples backends
        locations = await storage.store_distributed(data, file.filename)

        # Guardar referencias en memoria (temporal)
        temp_cache[retrieval_id] = locations

        return JSONResponse({
            "status": "success",
            "retrieval_id": retrieval_id,
            "file_hash": locations['hash'],
            "size": locations['size'],
            "locations": locations['locations'],
            "message": "✓ Archivo almacenado de forma distribuida"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/retrieve")
async def retrieve_encrypted_file(request: RetrievalRequest):
    """
    Recupera archivo encriptado desde backends distribuidos.

    El cliente DEBE desencriptar después de recibir.
    El servidor NO desencripta.

    Args:
        storage_locations: diccionario con IDs de cada backend
        salt: para verificación de integridad

    Retorna:
        archivo encriptado (bytes)
    """
    try:
        data = await storage.retrieve_from_any(request.storage_locations)

        if not data:
            raise HTTPException(
                status_code=404,
                detail="Data not found in any backend"
            )

        return FileResponse(
            path=None,
            content=data,
            media_type="application/octet-stream",
            headers={"Content-Disposition": "attachment; filename=encrypted.bin"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/health")
async def health_check():
    """
    Health check (sin información sensible).
    El servidor no revela su ubicación ni identidad.
    """
    return JSONResponse({
        "status": "online",
        "backends": list(storage.backends.keys()),
        "timestamp": None  # Sin timestamps
    })


@app.get("/api/v1/clear")
async def clear_memory():
    """
    Limpia la memoria caché temporal.
    Esto cumple con 'Ni existe la información'.
    """
    global temp_cache
    count = len(temp_cache)
    temp_cache.clear()
    return JSONResponse({
        "status": "success",
        "cleared_entries": count,
        "message": "✓ Memoria caché limpiada"
    })


@app.on_event("shutdown")
async def cleanup():
    """Limpieza al apagar el servidor."""
    global temp_cache
    temp_cache.clear()
    print("\n✓ Limpieza completada. Servidor apagado.")


def run_server(
    host: str = "127.0.0.1",
    port: int = 8443,
    ssl_certfile: Optional[str] = None,
    ssl_keyfile: Optional[str] = None,
    title: str = "3NI Secure Server"
):
    """
    Inicia el servidor sin estado.

    Args:
        host: interfaz de escucha (127.0.0.1 para localhost, 0.0.0.0 para TOR/I2P)
        port: puerto
        ssl_certfile: certificado SSL (opcional)
        ssl_keyfile: clave privada SSL (opcional)
        title: título del servidor
    """
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
        log_level="warning",  # Minimal logging
        access_log=False  # Sin logs de acceso (privacidad)
    )

    server = uvicorn.Server(config)
    return server


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════╗
    ║   3NI SECURE SERVER v1.0           ║
    ║   Almacenamiento seguro distribuido║
    ╚════════════════════════════════════╝
    """)

    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8443

    run_server(host="127.0.0.1", port=port)
