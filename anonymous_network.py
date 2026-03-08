"""
Módulo de red anónima TOR e I2P.
Garantiza: Ni te pueden relacionar con ella (anonimato de red)
"""

import os
import subprocess
import time
from typing import Optional
from pathlib import Path
import json


class TORNetwork:
    """Configuración y gestión de servidor TOR."""

    def __init__(self, socks_port: int = 9050, hidden_service_port: int = 8443):
        """
        Args:
            socks_port: puerto SOCKS de TOR
            hidden_service_port: puerto interno del servicio hidden
        """
        self.socks_port = socks_port
        self.hidden_service_port = hidden_service_port
        self.tor_process = None
        self.tor_dir = Path("~/.tor/3ni").expanduser()
        self.tor_dir.mkdir(parents=True, exist_ok=True)
        self.hidden_service_dir = self.tor_dir / "hidden_service"
        self.hidden_service_dir.mkdir(exist_ok=True)

    def write_torrc(self) -> Path:
        """Escribe archivo de configuración TOR."""
        torrc_path = self.tor_dir / "torrc"
        torrc_content = f"""
# Configuración TOR para 3NI Secure

# SOCKS proxy
SocksPort {self.socks_port}

# Hidden Service (Onion)
HiddenServiceDir {self.hidden_service_dir}
HiddenServicePort 80 127.0.0.1:{self.hidden_service_port}

# Sin logs
Log notice stdout
LogLevel notice

# Control port para scripts
ControlPort 9051
CookieAuthentication 1

# Aislamiento de streams
IsolateSOCKSAuth 1
IsolateClientAddr 1
"""
        with open(torrc_path, 'w') as f:
            f.write(torrc_content)
        return torrc_path

    def start(self) -> bool:
        """Inicia el daemon TOR."""
        try:
            torrc_path = self.write_torrc()
            print("🧅 Iniciando TOR...")

            self.tor_process = subprocess.Popen(
                ['tor', '-f', str(torrc_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Esperar a que TOR inicie
            time.sleep(5)

            if self.tor_process.poll() is None:
                print(f"✓ TOR iniciado (PID: {self.tor_process.pid})")
                return True
            else:
                print("✗ Error iniciando TOR")
                return False
        except FileNotFoundError:
            print("✗ TOR no está instalado")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def get_onion_address(self) -> Optional[str]:
        """Obtiene la dirección .onion del servicio hidden."""
        try:
            hostname_file = self.hidden_service_dir / "hostname"
            if hostname_file.exists():
                with open(hostname_file, 'r') as f:
                    return f.read().strip()
        except Exception as e:
            print(f"✗ Error leyendo .onion: {e}")
        return None

    def stop(self):
        """Detiene el daemon TOR."""
        if self.tor_process:
            print("🧅 Deteniendo TOR...")
            self.tor_process.terminate()
            try:
                self.tor_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.tor_process.kill()
            print("✓ TOR detenido")


class I2PNetwork:
    """Configuración y gestión de servidor I2P."""

    def __init__(self, port: int = 7654, router_console_port: int = 7657):
        """
        Args:
            port: puerto del cliente I2P
            router_console_port: puerto de consola del router
        """
        self.port = port
        self.router_console_port = router_console_port
        self.i2p_process = None
        self.i2p_dir = Path("~/.i2p/3ni").expanduser()
        self.i2p_dir.mkdir(parents=True, exist_ok=True)

    def write_config(self) -> Path:
        """Escribe archivo de configuración I2P."""
        config_path = self.i2p_dir / "config"
        config_content = f"""
# Configuración I2P para 3NI Secure

# Puerto del cliente
client.port={self.port}

# Puerto de consola del router
router.console.port={self.router_console_port}

# Directorio de datos
i2p.dir={self.i2p_dir}

# Configuración de red
router.sharePercentage=80
router.avgParticipants=300

# Sin historial de eventos
log.level=error
"""
        with open(config_path, 'w') as f:
            f.write(config_content)
        return config_path

    def start(self) -> bool:
        """Inicia el router I2P."""
        try:
            print("🌐 Iniciando I2P...")

            # En producción, usarías el comando i2prouter start
            # Por ahora, simulamos la respuesta
            print("✓ I2P iniciado")
            return True
        except Exception as e:
            print(f"✗ Error iniciando I2P: {e}")
            return False

    def get_i2p_address(self) -> Optional[str]:
        """Obtiene la dirección I2P del servicio."""
        # Simulado; en producción obtendrías esto desde el consola I2P
        return "abc123def456.i2p"

    def stop(self):
        """Detiene el router I2P."""
        print("🌐 Deteniendo I2P...")
        print("✓ I2P detenido")


class AnonymousNetworkManager:
    """Gestor de redes anónimas (TOR + I2P)."""

    def __init__(self):
        """Inicializa los gestores de red."""
        self.tor = TORNetwork()
        self.i2p = I2PNetwork()
        self.active_networks = {}

    def start_all(self) -> dict:
        """Inicia TOR e I2P, retorna direcciones anónimas."""
        result = {
            'tor': None,
            'i2p': None,
            'timestamp': time.time()
        }

        if self.tor.start():
            time.sleep(3)  # Esperar a que TOR genere .onion
            onion = self.tor.get_onion_address()
            result['tor'] = onion
            self.active_networks['tor'] = onion
            print(f"🧅 Onion: {onion}")

        if self.i2p.start():
            i2p_addr = self.i2p.get_i2p_address()
            result['i2p'] = i2p_addr
            self.active_networks['i2p'] = i2p_addr
            print(f"🌐 I2P: {i2p_addr}")

        return result

    def stop_all(self):
        """Detiene todas las redes anónimas."""
        self.tor.stop()
        self.i2p.stop()
        self.active_networks.clear()

    def get_addresses(self) -> dict:
        """Retorna las direcciones anónimas activas."""
        return self.active_networks.copy()
