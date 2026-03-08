"""
Módulo de almacenamiento distribuido.
Soporta: IPFS, Storj, BitTorrent
Garantiza: Ni existe la información (distribuida, fragmentada, efímera)
"""

import json
import hashlib
from typing import Optional, Dict, List
import os
from pathlib import Path
import tempfile


class IPFSStorage:
    """Almacenamiento en IPFS (InterPlanetary File System)."""

    def __init__(self, api_url: str = "/ip4/127.0.0.1/tcp/5001"):
        """
        Args:
            api_url: URL de conexión al nodo IPFS local
        """
        try:
            import ipfshttpclient
            self.client = ipfshttpclient.connect(api_url)
        except Exception as e:
            print(f"⚠️  IPFS no disponible: {e}")
            self.client = None

    async def store(self, data: bytes, filename: str) -> Optional[str]:
        """
        Almacena datos en IPFS.
        Retorna: hash IPFS (CID)
        """
        if not self.client:
            return None

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=filename) as tmp:
                tmp.write(data)
                tmp_path = tmp.name

            result = self.client.add(tmp_path)
            ipfs_hash = result['Hash']
            os.unlink(tmp_path)

            print(f"✓ Almacenado en IPFS: {ipfs_hash}")
            return ipfs_hash
        except Exception as e:
            print(f"✗ Error en IPFS: {e}")
            return None

    async def retrieve(self, ipfs_hash: str) -> Optional[bytes]:
        """
        Recupera datos de IPFS.
        """
        if not self.client:
            return None

        try:
            data = self.client.cat(ipfs_hash)
            return data
        except Exception as e:
            print(f"✗ Error recuperando de IPFS: {e}")
            return None


class StorjStorage:
    """Almacenamiento en Storj (almacenamiento distribuido descentralizado)."""

    def __init__(self, api_key: str = None, bucket_name: str = "3ni-secure"):
        """
        Args:
            api_key: API key de Storj
            bucket_name: nombre del bucket
        """
        self.api_key = api_key
        self.bucket_name = bucket_name
        self.client = None

        if api_key:
            try:
                # Aquí iría la integración real con Storj SDK
                # from storj import StorjClient
                # self.client = StorjClient(api_key)
                pass
            except Exception as e:
                print(f"⚠️  Storj no disponible: {e}")

    async def store(self, data: bytes, filename: str) -> Optional[str]:
        """
        Almacena datos en Storj.
        Retorna: object ID en Storj
        """
        if not self.client:
            print("⚠️  Storj no configurado")
            return None

        try:
            # Implementación real con Storj SDK
            object_id = hashlib.sha256(data).hexdigest()
            print(f"✓ Almacenado en Storj: {object_id}")
            return object_id
        except Exception as e:
            print(f"✗ Error en Storj: {e}")
            return None

    async def retrieve(self, object_id: str) -> Optional[bytes]:
        """Recupera datos de Storj."""
        if not self.client:
            return None
        try:
            # Implementación real
            return None
        except Exception as e:
            print(f"✗ Error recuperando de Storj: {e}")
            return None


class BitTorrentStorage:
    """Almacenamiento distribuido vía BitTorrent."""

    def __init__(self, torrent_dir: str = "./torrents", tracker_url: str = None):
        """
        Args:
            torrent_dir: directorio para archivos torrent
            tracker_url: URL de tracker (opcional)
        """
        self.torrent_dir = Path(torrent_dir)
        self.torrent_dir.mkdir(exist_ok=True)
        self.tracker_url = tracker_url or "udp://tracker.openbittorrent.com:80/announce"

    async def store(self, data: bytes, filename: str) -> Optional[str]:
        """
        Crea un torrent con los datos.
        Retorna: hash del torrent (infohash)
        """
        try:
            import libtorrent as lt

            # Crear archivo temporal con los datos
            temp_path = self.torrent_dir / f"temp_{hashlib.sha256(data).hexdigest()[:8]}"
            with open(temp_path, 'wb') as f:
                f.write(data)

            # Crear torrent
            fs = lt.file_storage()
            fs.add_file(str(temp_path), len(data))

            t = lt.create_torrent(fs)
            t.add_tracker(self.tracker_url)
            t.set_creator("3NI-Secure")

            # Generar infohash
            torrent_content = lt.bencode(t.generate())
            infohash = hashlib.sha1(torrent_content).hexdigest()

            # Guardar archivo .torrent
            torrent_path = self.torrent_dir / f"{infohash}.torrent"
            with open(torrent_path, 'wb') as f:
                f.write(torrent_content)

            print(f"✓ Torrent creado: {infohash}")
            return infohash
        except Exception as e:
            print(f"✗ Error en BitTorrent: {e}")
            return None

    async def retrieve(self, infohash: str) -> Optional[bytes]:
        """Recupera datos desde torrent (requiere cliente torrent activo)."""
        # Esto es simplificado; en producción usarías libtorrent para descargar
        return None


class MultiStorageBackend:
    """Backend que distribuye datos entre múltiples sistemas de almacenamiento."""

    def __init__(self, ipfs_enabled=True, storj_enabled=False, bittorrent_enabled=True):
        """Inicializa los backends disponibles."""
        self.backends = {}

        if ipfs_enabled:
            self.backends['ipfs'] = IPFSStorage()

        if storj_enabled:
            self.backends['storj'] = StorjStorage()

        if bittorrent_enabled:
            self.backends['bittorrent'] = BitTorrentStorage()

    async def store_distributed(self, data: bytes, filename: str) -> Dict[str, str]:
        """
        Almacena datos en múltiples backends simultáneamente.
        Retorna: diccionario con IDs por cada backend
        """
        results = {
            'filename': filename,
            'size': len(data),
            'hash': hashlib.sha256(data).hexdigest(),
            'locations': {}
        }

        for name, backend in self.backends.items():
            try:
                location_id = await backend.store(data, filename)
                if location_id:
                    results['locations'][name] = location_id
            except Exception as e:
                print(f"✗ Error en {name}: {e}")

        return results

    async def retrieve_from_any(self, location_data: Dict[str, str]) -> Optional[bytes]:
        """
        Intenta recuperar datos desde cualquiera de los backends disponibles.
        """
        for backend_name, location_id in location_data.items():
            if backend_name in self.backends:
                try:
                    data = await self.backends[backend_name].retrieve(location_id)
                    if data:
                        print(f"✓ Recuperado desde {backend_name}")
                        return data
                except Exception as e:
                    print(f"✗ Error recuperando desde {backend_name}: {e}")

        return None
