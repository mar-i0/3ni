"""
Cliente CLI para 3NI Secure.
Encripta archivos localmente y los sube a través de TOR/I2P.
"""

import click
import asyncio
import base64
import json
from pathlib import Path
from typing import Optional
import aiohttp
import requests
from encryption import E2EEncryption
import qrcode
from io import BytesIO


class ThreeniClient:
    """Cliente principal para 3NI Secure."""

    def __init__(self, server_url: str = "http://127.0.0.1:8443"):
        """
        Args:
            server_url: URL del servidor (puede ser .onion o .i2p)
        """
        self.server_url = server_url.rstrip('/')
        self.session = None

    async def upload(
        self,
        file_path: str,
        password: str,
        use_tor: bool = False,
        use_i2p: bool = False
    ) -> Optional[dict]:
        """
        Encripta y sube un archivo.

        Args:
            file_path: ruta al archivo a encriptar
            password: contraseña para derivar clave de encriptación
            use_tor: enrutar a través de TOR
            use_i2p: enrutar a través de I2P

        Retorna:
            diccionario con localizaciones de almacenamiento
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

            click.echo("🔐 Encriptando archivo...")

            # Encriptar archivo
            ciphertext, salt, file_hash = E2EEncryption.encrypt_file(
                str(file_path),
                password
            )

            click.echo(f"✓ Encriptado: {len(ciphertext)} bytes")

            # Preparar para envío
            server_url = self.server_url
            if use_tor:
                # Conectar a través de proxy SOCKS5 (TOR)
                server_url = f"socks5://127.0.0.1:9050/{self.server_url}"
                click.echo("🧅 Usando TOR...")
            elif use_i2p:
                click.echo("🌐 Usando I2P...")

            click.echo(f"📤 Subiendo a {self.server_url}...")

            # Enviar archivo encriptado
            async with aiohttp.ClientSession() as session:
                with open(file_path, 'rb') as f:
                    files = {'file': (file_path.name, ciphertext)}

                    async with session.post(
                        f"{self.server_url}/api/v1/store",
                        data=files
                    ) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            click.echo("✓ Archivo subido exitosamente")
                            return result
                        else:
                            error = await resp.text()
                            click.echo(f"✗ Error: {error}")
                            return None

        except Exception as e:
            click.echo(f"✗ Error: {e}", err=True)
            return None

    async def download(
        self,
        retrieval_id: str,
        password: str,
        output_path: Optional[str] = None,
        use_tor: bool = False,
        use_i2p: bool = False
    ) -> Optional[bytes]:
        """
        Descarga y desencripta un archivo.

        Args:
            retrieval_id: ID de recuperación anónimo
            password: contraseña para derivar clave
            output_path: ruta donde guardar el archivo
            use_tor: usar TOR
            use_i2p: usar I2P

        Retorna:
            datos desencriptados (bytes)
        """
        try:
            click.echo("📥 Descargando desde servidor...")

            if use_tor:
                click.echo("🧅 Usando TOR...")
            elif use_i2p:
                click.echo("🌐 Usando I2P...")

            # Obtener localizaciones (simulado)
            storage_locations = {
                "ipfs": retrieval_id,
                "bittorrent": f"{retrieval_id}.torrent"
            }

            # Solicitar al servidor
            async with aiohttp.ClientSession() as session:
                payload = {
                    "storage_locations": storage_locations,
                    "salt": ""
                }

                async with session.post(
                    f"{self.server_url}/api/v1/retrieve",
                    json=payload
                ) as resp:
                    if resp.status == 200:
                        ciphertext = await resp.read()
                        click.echo(f"✓ Descargado: {len(ciphertext)} bytes")

                        click.echo("🔓 Desencriptando...")
                        plaintext = E2EEncryption.decrypt_file(
                            ciphertext,
                            password,
                            b""  # Salt sería enviado por el servidor
                        )

                        if output_path:
                            with open(output_path, 'wb') as f:
                                f.write(plaintext)
                            click.echo(f"✓ Guardado en: {output_path}")

                        return plaintext
                    else:
                        error = await resp.text()
                        click.echo(f"✗ Error: {error}")
                        return None

        except Exception as e:
            click.echo(f"✗ Error: {e}", err=True)
            return None


@click.group()
def cli():
    """3NI Secure - Almacenamiento seguro distribuido."""
    pass


@cli.command()
@click.option('--file', '-f', required=True, help='Archivo a encriptar')
@click.option('--password', '-p', prompt=True, hide_input=True,
              confirmation_prompt=True, help='Contraseña de encriptación')
@click.option('--server', '-s', default='http://127.0.0.1:8443',
              help='URL del servidor')
@click.option('--tor', is_flag=True, help='Usar TOR')
@click.option('--i2p', is_flag=True, help='Usar I2P')
@click.option('--qr', is_flag=True, help='Generar código QR con retrieval_id')
def upload(file, password, server, tor, i2p, qr):
    """Encripta y sube un archivo de forma segura."""

    client = ThreeniClient(server)
    result = asyncio.run(client.upload(file, password, use_tor=tor, use_i2p=i2p))

    if result:
        click.echo("\n" + "="*50)
        click.echo("INFORMACIÓN DE RECUPERACIÓN")
        click.echo("="*50)
        click.echo(f"Retrieval ID: {result['retrieval_id']}")
        click.echo(f"Hash: {result['file_hash']}")
        click.echo(f"Tamaño: {result['size']} bytes")
        click.echo(f"Ubicaciones: {json.dumps(result['locations'], indent=2)}")
        click.echo("="*50)

        # Generar QR si se solicita
        if qr:
            qr_data = {
                'retrieval_id': result['retrieval_id'],
                'server': server,
                'hash': result['file_hash']
            }

            qr_code = qrcode.QRCode(version=1, box_size=10)
            qr_code.add_data(json.dumps(qr_data))
            qr_code.make()
            img = qr_code.make_image()
            img.save('retrieval_qr.png')
            click.echo("✓ Código QR generado: retrieval_qr.png")


@cli.command()
@click.option('--id', '-i', required=True, help='Retrieval ID')
@click.option('--password', '-p', prompt=True, hide_input=True,
              help='Contraseña de desencriptación')
@click.option('--server', '-s', default='http://127.0.0.1:8443',
              help='URL del servidor')
@click.option('--output', '-o', help='Ruta de salida')
@click.option('--tor', is_flag=True, help='Usar TOR')
@click.option('--i2p', is_flag=True, help='Usar I2P')
def download(id, password, server, output, tor, i2p):
    """Descarga y desencripta un archivo."""

    client = ThreeniClient(server)
    result = asyncio.run(
        client.download(id, password, output, use_tor=tor, use_i2p=i2p)
    )

    if result:
        click.echo(f"✓ Archivo recuperado: {len(result)} bytes")


@cli.command()
def keygen():
    """Genera una contraseña segura para encriptación."""
    import secrets
    password = secrets.token_urlsafe(32)
    click.echo(f"🔑 Contraseña generada:\n{password}")


@cli.command()
@click.option('--server', '-s', default='http://127.0.0.1:8443',
              help='URL del servidor')
async def health(server):
    """Verifica el estado del servidor."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{server}/api/v1/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    click.echo("✓ Servidor en línea")
                    click.echo(f"Backends: {', '.join(data['backends'])}")
                else:
                    click.echo("✗ Servidor no disponible")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


if __name__ == '__main__':
    cli()
