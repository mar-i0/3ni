# 3NI SECURE v1.0

**Sistema de almacenamiento seguro distribuido basado en los 3NI:**

- ✓ **Ni existe la información** - Almacenamiento distribuido, efímero, sin persistencia centralizada
- ✓ **Ni nadie puede acceder a ella** - Encriptación E2E, clave derivada del usuario
- ✓ **Ni te pueden relacionar con ella** - Anonimato mediante TOR, I2P, sin metadatos

## Arquitectura

```
┌─────────────────────────┐
│   Cliente CLI (Python)  │
│   - Encripta localmente │
│   - Deriva clave del    │
│     usuario             │
└────────────┬────────────┘
             │ (Datos cifrados)
             ▼
┌─────────────────────────┐
│  Red Anónima            │
│  - TOR (.onion)         │
│  - I2P (.i2p)           │
└────────────┬────────────┘
             │
┌────────────▼──────────────────┐
│  Servidor sin estado          │
│  - No autenticación           │
│  - No metadatos               │
│  - Sin logs de acceso         │
└────────────┬──────────────────┘
             │
    ┌────────┼────────┐
    ▼        ▼        ▼
┌──────┐ ┌──────────┐ ┌──────────┐
│ IPFS │ │  Storj   │ │BitTorrent│
│      │ │ (P2P)    │ │ (DHT)    │
└──────┘ └──────────┘ └──────────┘
```

## Instalación

```bash
# Clonar repositorio
git clone https://github.com/mar-i0/3NI.git
cd 3NI

# Instalar dependencias
pip install -r requirements.txt

# Dependencias del sistema (Ubuntu/Debian)
sudo apt-get install tor i2p ipfs
```

### Requisitos

- **Python 3.10+**
- **TOR** - Para anonimato de red
- **I2P** - Alternativa/complemento a TOR
- **IPFS** - Almacenamiento distribuido
- **libtorrent-rasterbar** - Para soporte BitTorrent

## Uso Rápido

### 1. Iniciar el servidor

```bash
python main.py server start --tor --i2p
```

Salida:
```
🧅 TOR (Onion): http://abc123def456.onion
🌐 I2P: http://uvwxyz1234.i2p
📡 Servidor disponible en: http://127.0.0.1:8443
```

### 2. Encriptar y subir archivo

```bash
python main.py client upload --file secreto.txt --server http://127.0.0.1:8443
```

Solicitará contraseña (no visible en pantalla):
```
Contraseña: ••••••••••
Repetir para confirmar: ••••••••••

INFORMACIÓN DE RECUPERACIÓN
========================================
Retrieval ID: ABC123XYZ...
Hash:         abc123def456...
Tamaño:       1024 bytes

Ubicaciones:
  ipfs           QmABC123...
  bittorrent     ABC123.torrent
========================================
```

### 3. Descargar y desencriptar

```bash
python main.py client download --id ABC123XYZ --server http://127.0.0.1:8443
```

Solicitará contraseña:
```
Contraseña: ••••••••••
✓ Archivo recuperado: 1024 bytes
```

## Comandos Disponibles

### Servidor

```bash
# Iniciar con todos los backends
python main.py server start --tor --i2p

# Iniciar sin TOR
python main.py server start --no-tor

# Iniciar sin I2P
python main.py server start --no-i2p

# Con SSL/TLS
python main.py server start --ssl
```

### Cliente

```bash
# Generar contraseña segura
python main.py keygen

# Subir con contraseña directa
python main.py client upload --file archivo.txt --password micontraseña

# Generar QR con código de recuperación
python main.py client upload --file archivo.txt --qr

# Usar TOR
python main.py client upload --file archivo.txt --tor

# Usar I2P
python main.py client upload --file archivo.txt --i2p

# Descargar con especificar salida
python main.py client download --id RETRIEVAL_ID --output recuperado.txt
```

### Demo

```bash
# Ejecutar demostración completa
python main.py demo
```

## Flujo de Encriptación

### Encriptación (Cliente → Servidor)

1. **Usuario proporciona:**
   - Archivo a proteger
   - Contraseña/frase

2. **Cliente:**
   - Genera salt aleatorio (32 bytes)
   - Deriva clave: PBKDF2(password, salt) → 32 bytes
   - Encripta archivo: Fernet(key)
   - Calcula hash SHA-256 para verificación

3. **Transmisión:**
   - Datos ya encriptados
   - Servidor NUNCA ve contenido en claro
   - Salt se envía junto (necesario para desencrypción)

4. **Almacenamiento Distribuido:**
   - IPFS: almacena contenido, devuelve CID
   - Storj: contrato de almacenamiento P2P
   - BitTorrent: crea swarm distribuido

### Desencriptación (Servidor → Cliente)

1. **Usuario proporciona:**
   - Retrieval ID (anónimo, sin relación con identidad)
   - Contraseña

2. **Cliente:**
   - Recupera datos cifrados desde cualquier backend
   - Deriva clave con salt
   - Desencripta: Fernet(key).decrypt()
   - Verifica integridad: SHA-256

3. **Integridad:**
   - Hash verificable sin desencriptar
   - Detección de corrupción o tampering

## Características de Seguridad

### Ni existe la información

- **Almacenamiento distribuido:** Datos fragmentados entre múltiples nodos
- **Ephemeral Storage:** Caché en memoria, sin persistencia en disco
- **Auto-purga:** Limpieza periódica de datos temporales
- **No backup centralizado:** Cada nodo es autónomo

### Ni nadie puede acceder a ella

- **E2E Encryption:** Encriptación de punta a punta (Fernet - AES-128)
- **PBKDF2:** Derivación fuerte de clave (480,000 iteraciones)
- **No contraseña en servidor:** El servidor no recibe ni almacena contraseñas
- **Sin claves administrativas:** No hay backdoors, no hay cuentas privilegiadas
- **Metadata resistance:** Sin timestamps, IPs, user-agents en logs

### Ni te pueden relacionar con ella

- **Red anónima TOR:**
  - Múltiples capas de encriptación
  - Rotación de circuitos
  - Dirección .onion única por sesión

- **Red anónima I2P:**
  - Encriptación de punto a punto
  - Mezclado de paquetes (mixnet)
  - Garlic routing

- **Sin autenticación centralizada:**
  - Retrieval ID anónimo (sin relación con usuario)
  - Sin cuentas, sin perfiles
  - Sin sesiones persistentes

- **No recopilación de metadatos:**
  - Sin logs de acceso
  - Sin timestamps de transacciones
  - Sin correlación de IPs

## Configuración Avanzada

### Archivo de configuración (`config.json`)

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8443,
    "ssl": false
  },
  "storage": {
    "ipfs": {
      "enabled": true,
      "api_url": "/ip4/127.0.0.1/tcp/5001"
    },
    "storj": {
      "enabled": false,
      "api_key": ""
    },
    "bittorrent": {
      "enabled": true,
      "tracker_url": "udp://tracker.openbittorrent.com:80/announce"
    }
  },
  "networks": {
    "tor": {
      "enabled": true,
      "socks_port": 9050
    },
    "i2p": {
      "enabled": true,
      "port": 7654
    }
  },
  "encryption": {
    "algorithm": "fernet",
    "iterations": 480000,
    "salt_length": 32
  }
}
```

### Variables de entorno

```bash
# Configuración de TOR
export TOR_SOCKS_PORT=9050
export TOR_CONTROL_PORT=9051

# Configuración de I2P
export I2P_PORT=7654

# IPFS
export IPFS_API_URL="/ip4/127.0.0.1/tcp/5001"

# Servidor
export 3NI_SERVER_PORT=8443
export 3NI_ENABLE_TOR=true
export 3NI_ENABLE_I2P=true
```

## API del Servidor

### POST `/api/v1/store`

Almacena un archivo encriptado en backends distribuidos.

**Parámetros:**
- `file` (multipart): datos encriptados

**Respuesta:**
```json
{
  "status": "success",
  "retrieval_id": "abc123xyz...",
  "file_hash": "sha256hash...",
  "size": 1024,
  "locations": {
    "ipfs": "QmABC123...",
    "bittorrent": "ABC123.torrent"
  }
}
```

### POST `/api/v1/retrieve`

Recupera archivo encriptado desde backends.

**Parámetros:**
```json
{
  "storage_locations": {
    "ipfs": "QmABC123...",
    "bittorrent": "ABC123.torrent"
  },
  "salt": "base64encodedSalt"
}
```

**Respuesta:** Datos encriptados (bytes)

### GET `/api/v1/health`

Verifica estado del servidor.

**Respuesta:**
```json
{
  "status": "online",
  "backends": ["ipfs", "bittorrent"],
  "timestamp": null
}
```

### GET `/api/v1/clear`

Limpia caché en memoria.

**Respuesta:**
```json
{
  "status": "success",
  "cleared_entries": 42
}
```

## Casos de Uso

### 1. Whistleblowing Seguro

```bash
# Reportero anónimo
python main.py client upload \
  --file documento_secreto.pdf \
  --server http://abc123.onion \
  --tor \
  --qr
```

### 2. Comunicación Resistente a Censura

```bash
# Usuario en país con censura
python main.py client upload \
  --file mensaje.txt \
  --server http://xyz123.i2p \
  --i2p
```

### 3. Protección de Datos Sensibles

```bash
# Usuario protegiendo datos médicos/financieros
python main.py client upload --file datos_medicos.bin
```

## Limitaciones Conocidas

- **IPFS:** Requiere nodo IPFS local corriendo
- **Storj:** SDK no completamente integrado, requiere credenciales
- **BitTorrent:** Requiere seeders activos para descarga
- **TOR:** Requiere `tor` instalado y en PATH
- **I2P:** Requiere router I2P activo

## Mejoras Futuras

- [ ] Integración WebRTC para transferencias P2P directas
- [ ] Sharding de datos con Shamir Secret Sharing
- [ ] Servidor sin estado containerizado (Docker)
- [ ] Cliente con interfaz web
- [ ] Backup distribuido automático
- [ ] Sincronización con SFTP/rclone
- [ ] Integración con Blockchain para pruebas de almacenamiento

## Seguridad & Auditoría

### Consideraciones de Seguridad

⚠️ **Este software es experimental. Úsalo bajo tu propio riesgo.**

- **Criptografía:** Usa bibliotecas estándar (cryptography, libsodium)
- **Fuente abierta:** Código completamente auditable
- **Sin telemetría:** Cero recopilación de datos
- **Sin dependencias maliciosas:** Stack mínimo de dependencias

### Recomendaciones

1. **Auditoría de código:** Revisa `/usr/src/3NI/` antes de usar
2. **Actualización:** Mantén TOR, I2P, IPFS actualizados
3. **Contraseñas:** Usa frases robustas (20+ caracteres)
4. **Backups:** Guarda Retrieval IDs en lugar seguro
5. **Privacidad de red:** Usa VPN + TOR para máximo anonimato

## Contribuir

Reporta vulnerabilidades privadamente a `security@3ni-secure.local`

## Licencia

MIT License - Código abierto, uso libre

## Contacto

- Código: [GitHub](https://github.com/mar-i0/3NI)
- Issues: Reporta bugs en GitHub Issues

---

**3NI SECURE** - Almacenamiento sin identidad, sin censura, sin control.
