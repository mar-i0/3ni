"""
3NI SECURE - Punto de entrada principal.

Orquesta:
- Servidor sin estado
- Redes anónimas (TOR + I2P)
- Almacenamiento distribuido (IPFS, Storj, BitTorrent)
- Encriptación E2E

Uso:
    python main.py server          # Inicia el servidor
    python main.py client upload   # Sube archivo encriptado
    python main.py client download # Descarga archivo encriptado
    python main.py demo            # Demo completa
"""

import click
import asyncio
import os
from pathlib import Path
from contextlib import asynccontextmanager

from server import run_server
from anonymous_network import AnonymousNetworkManager
from client import ThreeniClient
from encryption import E2EEncryption


class ThreeniManager:
    """Gestor central de 3NI."""

    def __init__(self):
        """Inicializa todos los componentes."""
        self.network_manager = AnonymousNetworkManager()
        self.server = None
        self.anonymous_addresses = {}

    def print_banner(self):
        """Imprime banner de bienvenida."""
        banner = """
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║             3NI SECURE v1.0                          ║
║                                                       ║
║  ✓ Ni existe la información                          ║
║  ✓ Ni nadie puede acceder a ella                     ║
║  ✓ Ni te pueden relacionar con ella                  ║
║                                                       ║
║  Almacenamiento seguro distribuido                   ║
║  Encriptación E2E | TOR + I2P | IPFS/Storj/BT       ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
        """
        click.echo(banner)

    async def start_server(
        self,
        port: int = 8443,
        enable_tor: bool = True,
        enable_i2p: bool = True,
        use_ssl: bool = False
    ):
        """
        Inicia el servidor con redes anónimas.

        Args:
            port: puerto del servidor
            enable_tor: habilitar TOR
            enable_i2p: habilitar I2P
            use_ssl: usar SSL/TLS
        """
        self.print_banner()

        click.echo("🚀 Iniciando 3NI Secure Server...\n")

        # Iniciar redes anónimas
        if enable_tor or enable_i2p:
            click.echo("🔗 Configurando redes anónimas...")
            self.anonymous_addresses = self.network_manager.start_all()

            if self.anonymous_addresses.get('tor'):
                click.echo(f"   🧅 TOR (Onion): http://{self.anonymous_addresses['tor']}")

            if self.anonymous_addresses.get('i2p'):
                click.echo(f"   🌐 I2P: http://{self.anonymous_addresses['i2p']}")

        click.echo(f"\n📡 Servidor disponible en: http://127.0.0.1:{port}")
        click.echo("\n✓ Servidor en espera de conexiones...\n")

        # Iniciar servidor
        server = run_server(
            host="127.0.0.1",
            port=port,
            ssl_certfile="certs/server.crt" if use_ssl else None,
            ssl_keyfile="certs/server.key" if use_ssl else None
        )

        try:
            await server.serve()
        except KeyboardInterrupt:
            click.echo("\n\n🛑 Apagando servidor...")
            self.network_manager.stop_all()
            click.echo("✓ Limpieza completada")


@click.group()
def cli():
    """3NI Secure - Almacenamiento seguro distribuido."""
    pass


@cli.group()
def server():
    """Comandos del servidor."""
    pass


@server.command()
@click.option('--port', '-p', default=8443, help='Puerto del servidor')
@click.option('--tor/--no-tor', default=True, help='Habilitar TOR')
@click.option('--i2p/--no-i2p', default=True, help='Habilitar I2P')
@click.option('--ssl/--no-ssl', default=False, help='Usar SSL/TLS')
def start(port, tor, i2p, ssl):
    """Inicia el servidor con redes anónimas."""
    manager = ThreeniManager()
    asyncio.run(manager.start_server(
        port=port,
        enable_tor=tor,
        enable_i2p=i2p,
        use_ssl=ssl
    ))


@cli.group()
def client():
    """Comandos del cliente."""
    pass


@client.command()
@click.option('--file', '-f', required=True, help='Archivo a encriptar')
@click.option('--password', '-p', help='Contraseña (si no se proporciona, se solicita)')
@click.option('--server', '-s', default='http://127.0.0.1:8443', help='URL del servidor')
@click.option('--tor', is_flag=True, help='Usar TOR')
@click.option('--i2p', is_flag=True, help='Usar I2P')
@click.option('--qr', is_flag=True, help='Generar código QR')
def upload(file, password, server, tor, i2p, qr):
    """Encripta y sube un archivo."""
    if not password:
        password = click.prompt('Contraseña', hide_input=True,
                               confirmation_prompt=True)

    threeni_client = ThreeniClient(server)
    result = asyncio.run(threeni_client.upload(
        file,
        password,
        use_tor=tor,
        use_i2p=i2p
    ))

    if result:
        click.echo("\n" + "="*60)
        click.echo("INFORMACIÓN DE RECUPERACIÓN")
        click.echo("="*60)
        click.echo(f"Retrieval ID: {result['retrieval_id']}")
        click.echo(f"Hash:         {result['file_hash']}")
        click.echo(f"Tamaño:       {result['size']} bytes")
        click.echo("\nUbicaciones de almacenamiento:")
        for backend, location in result['locations'].items():
            click.echo(f"  {backend:15} {location}")
        click.echo("="*60)

        if qr:
            import json
            import qrcode
            qr_data = {
                'id': result['retrieval_id'],
                'server': server,
                'hash': result['file_hash']
            }
            qr_obj = qrcode.QRCode(version=1, box_size=10)
            qr_obj.add_data(json.dumps(qr_data))
            qr_obj.make()
            img = qr_obj.make_image()
            img.save('retrieval_qr.png')
            click.echo("\n✓ QR guardado: retrieval_qr.png")


@client.command()
@click.option('--id', '-i', required=True, help='Retrieval ID')
@click.option('--password', '-p', help='Contraseña')
@click.option('--server', '-s', default='http://127.0.0.1:8443', help='URL del servidor')
@click.option('--output', '-o', help='Ruta de salida')
@click.option('--tor', is_flag=True, help='Usar TOR')
@click.option('--i2p', is_flag=True, help='Usar I2P')
def download(id, password, server, output, tor, i2p):
    """Descarga y desencripta un archivo."""
    if not password:
        password = click.prompt('Contraseña', hide_input=True)

    threeni_client = ThreeniClient(server)
    result = asyncio.run(threeni_client.download(
        id,
        password,
        output,
        use_tor=tor,
        use_i2p=i2p
    ))

    if result:
        click.echo(f"\n✓ Archivo recuperado: {len(result)} bytes")


@cli.command()
def keygen():
    """Genera contraseña segura."""
    import secrets
    pwd = secrets.token_urlsafe(32)
    click.echo(f"🔑 Contraseña generada:\n{pwd}\n")
    click.echo("⚠️  Guárdala en un lugar seguro")


@cli.command()
def demo():
    """Ejecuta una demostración completa."""
    manager = ThreeniManager()
    manager.print_banner()

    # Crear archivo de prueba
    test_file = Path("test_secret.txt")
    test_file.write_text("Este es un archivo secreto para 3NI Secure")

    click.echo("📝 Archivo de prueba creado: test_secret.txt\n")

    # Generar contraseña
    import secrets
    password = secrets.token_urlsafe(16)
    click.echo(f"🔐 Encriptando con contraseña: {password[:20]}...\n")

    # Encriptar
    ciphertext, salt, file_hash = E2EEncryption.encrypt_file(
        str(test_file),
        password
    )
    click.echo(f"✓ Encriptado: {len(ciphertext)} bytes")
    click.echo(f"✓ Hash: {file_hash.hex()[:16]}...\n")

    # Desencriptar (verificación)
    plaintext = E2EEncryption.decrypt_file(ciphertext, password, salt)
    click.echo(f"✓ Desencriptado: {plaintext.decode()}\n")

    # Limpiar
    test_file.unlink()
    click.echo("✓ Demo completada")


if __name__ == '__main__':
    cli()
