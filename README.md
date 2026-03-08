```
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║                          ███╗   ██╗██╗███╗   ███╗                        ║
║                          ████╗  ██║██║████╗ ████║                        ║
║                          ██╔██╗ ██║██║██╔████╔██║                        ║
║                          ██║╚██╗██║██║██║╚██╔╝██║                        ║
║                          ██║ ╚████║██║██║ ╚═╝ ██║                        ║
║                          ╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝                        ║
║                                                                           ║
║                    D I S T R I B U T E D   S E C U R E                   ║
║                            S T O R A G E                                 ║
║                                                                           ║
║                   Almacenamiento sin identidad, censura                  ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

## 🔐 Tres Principios. Cero Compromisos.

```
  ◆ Ni existe la información
    └─ Distribuida, fragmentada, efímera

  ◆ Ni nadie puede acceder a ella
    └─ Encriptación E2E, clave derivada del usuario

  ◆ Ni te pueden relacionar con ella
    └─ Red anónima (TOR + I2P), sin metadatos
```

---

## ⚡ Inicio Rápido

### 1️⃣ Instalación (30 segundos)

```bash
git clone https://github.com/mar-i0/3ni.git
cd 3ni
bash install.sh
```

### 2️⃣ Servidor (en una terminal)

```bash
source venv/bin/activate
python main.py server start --tor --i2p
```

**Salida esperada:**
```
🧅 TOR (Onion): http://abc123def456.onion
🌐 I2P: http://uvwxyz1234.i2p
📡 Servidor disponible en: http://127.0.0.1:8443
```

### 3️⃣ Encriptar & Subir (en otra terminal)

```bash
source venv/bin/activate
python main.py client upload --file secreto.txt

# ↓ Solicitará contraseña (oculta en pantalla)
# Contraseña: ••••••••••
# Repetir: ••••••••••
```

**Resultado:**
```
============================================================
INFORMACIÓN DE RECUPERACIÓN
============================================================
Retrieval ID: abc123xyz_defghijk_mnopqrstu_vwxyz123...
Hash:         1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d...
Tamaño:       1024 bytes

Ubicaciones:
  ipfs           QmABC123DEF456GHI789JKL...
  bittorrent     abc123xyz.torrent
============================================================
```

### 4️⃣ Descargar & Desencriptar

```bash
python main.py client download --id abc123xyz_defghijk_ --output recuperado.txt

# ↓ Solicitará contraseña
# Contraseña: ••••••••••

# ✓ Archivo recuperado: 1024 bytes
```

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                      CLIENTE CLI                         │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ Encrypt  │────│  Upload  │────│   QR Gen │          │
│  └──────────┘    └──────────┘    └──────────┘          │
│  ┌──────────┐    ┌──────────┐                          │
│  │ Decrypt  │────│ Download │                          │
│  └──────────┘    └──────────┘                          │
└──────────────────────┬──────────────────────────────────┘
                       │
                  (E2E Encrypted)
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │   TOR    │  │   I2P    │  │  Direct  │
    │ .onion   │  │  .i2p    │  │ localhost│
    └────┬─────┘  └────┬─────┘  └────┬─────┘
         │             │             │
         └─────────────┼─────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌──────────────────────┐      ┌──────────────────────┐
│ SERVER (Stateless)   │      │  NO AUTH             │
│ - Sin logs           │      │  NO METADATA         │
│ - Sin persistencia   │      │  NO TRACKING         │
│ - Caché ephemeral    │      │  CERO DATOS          │
└──────────────────────┘      └──────────────────────┘
        │
        ├─────────────────┬──────────────────┐
        │                 │                  │
        ▼                 ▼                  ▼
    ┌────────┐        ┌────────┐        ┌────────┐
    │  IPFS  │        │ Storj  │        │   BT   │
    │  P2P   │        │  P2P   │        │  DHT   │
    │ CID:Q… │        │Contract│        │.torrent│
    └────────┘        └────────┘        └────────┘
```

---

## 🛠️ Comandos Principales

### Servidor

```bash
# Inicio básico (con TOR + I2P)
python main.py server start --tor --i2p

# Sin anonimato (desarrollo local)
python main.py server start --no-tor --no-i2p

# Puerto personalizado
python main.py server start --port 9000

# Con SSL/TLS
python main.py server start --ssl
```

### Cliente - Upload

```bash
# Interactivo (solicita contraseña)
python main.py client upload --file datos.txt

# Con contraseña directa
python main.py client upload --file datos.txt --password "clave-segura"

# Vía TOR
python main.py client upload --file datos.txt --tor

# Vía I2P
python main.py client upload --file datos.txt --i2p

# Generar QR con código de recuperación
python main.py client upload --file datos.txt --qr
```

### Cliente - Download

```bash
# Descarga básica
python main.py client download --id RETRIEVAL_ID

# Con contraseña y salida especificada
python main.py client download --id RETRIEVAL_ID --password "clave" --output archivo.txt

# Vía TOR
python main.py client download --id RETRIEVAL_ID --tor
```

### Utilidades

```bash
# Generar contraseña segura
python main.py keygen

# Demo interactiva
python main.py demo

# Ver estado del servidor
curl http://127.0.0.1:8443/api/v1/health

# Limpiar caché en memoria
curl http://127.0.0.1:8443/api/v1/clear
```

---

## 🔒 Especificaciones Técnicas

```
┌─ ENCRIPTACIÓN ──────────────────────────────────┐
│ Algoritmo:        Fernet (AES-128-CBC + HMAC)  │
│ Derivación:       PBKDF2 (480,000 iteraciones)  │
│ Hash:             SHA-256                       │
│ Salt:             32 bytes (aleatorio)          │
│ Verificación:     SHA-256 (integridad)          │
└──────────────────────────────────────────────────┘

┌─ ALMACENAMIENTO ────────────────────────────────┐
│ IPFS:             Content-addressable (CID)     │
│ Storj:            Contrato de almacenamiento    │
│ BitTorrent:       DHT descentralizado           │
│ Redundancia:      Replicación multi-backend     │
└──────────────────────────────────────────────────┘

┌─ ANONIMATO ─────────────────────────────────────┐
│ TOR:              Circuitos de 3 relés          │
│ I2P:              Garlic routing                │
│ Servidor:         Sin logs, sin tracking        │
│ Metadatos:        CERO recopilación             │
└──────────────────────────────────────────────────┘
```

---

## 📊 Casos de Uso

### 🎯 Whistleblowing Seguro

```bash
# Reportero anónimo comparte documento confidencial
python main.py client upload \
  --file documento_clasificado.pdf \
  --server http://abc123.onion \
  --tor \
  --qr
```

### 🌍 Resistencia a Censura

```bash
# Usuario en país con represión comparte información
python main.py client upload \
  --file mensaje_politico.txt \
  --server http://xyz789.i2p \
  --i2p
```

### 🏥 Protección de Datos Sensibles

```bash
# Médico almacena registros de pacientes de forma segura
python main.py client upload --file historia_clinica.zip
```

### 💼 Sincronización Distribuida

```bash
# Dos dispositivos sincronizan datos sin intermediarios
# Dispositivo A:
python main.py client upload --file datos.zip --qr

# Dispositivo B (escanea QR):
python main.py client download --id RETRIEVAL_ID
```

---

## 🚀 Características Avanzadas

### Código QR para Compartir

```bash
python main.py client upload --file datos.txt --qr
# Genera: retrieval_qr.png
```

### Multi-Backend Automático

Tus datos se almacenan simultáneamente en:
- ✓ IPFS (descentralizado, resistente)
- ✓ BitTorrent (DHT distribuido)
- ✓ Storj (contrato de almacenamiento)

### API REST

```bash
# Subir archivo cifrado
curl -F "file=@datos.encrypted" http://127.0.0.1:8443/api/v1/store

# Descargar archivo cifrado
curl -X POST http://127.0.0.1:8443/api/v1/retrieve \
  -H "Content-Type: application/json" \
  -d '{"storage_locations":{"ipfs":"QmABC..."}}'
```

---

## 📚 Documentación

- **[README.md](README.md)** – Documentación técnica completa
- **[EXAMPLES.md](EXAMPLES.md)** – 50+ ejemplos de uso
- **[CLAUDE.md](CLAUDE.md)** – Guía de arquitectura para desarrolladores
- **[config.json](config.json)** – Parámetros configurables

---

## ⚙️ Requisitos

### Sistema

- **Python 3.10+**
- **TOR** (para anonimato de red)
- **I2P** (opcional, alternativo a TOR)
- **IPFS** (para almacenamiento distribuido)

### Instalación de dependencias del sistema

```bash
# Ubuntu/Debian
sudo apt-get install tor i2p go-ipfs python3-pip

# macOS
brew install tor go-ipfs

# Fedora
sudo dnf install tor i2p go-ipfs python3
```

### Python

```bash
pip install -r requirements.txt
```

---

## 🔧 Configuración

Edita `config.json` para personalizar:

```json
{
  "storage": {
    "ipfs": { "api_url": "/ip4/127.0.0.1/tcp/5001" },
    "bittorrent": { "tracker_url": "udp://tracker.openbittorrent.com:80" }
  },
  "networks": {
    "tor": { "socks_port": 9050 },
    "i2p": { "port": 7654 }
  },
  "encryption": {
    "iterations": 480000
  }
}
```

---

## 🐛 Solución de Problemas

### "TOR no está instalado"

```bash
# Ubuntu/Debian
sudo apt-get install tor

# macOS
brew install tor
```

### "IPFS API no disponible"

```bash
# Inicia el daemon IPFS
ipfs daemon
```

### "Puerto 8443 en uso"

```bash
python main.py server start --port 9000
```

### "Conexión rechazada"

```bash
# Verifica que el servidor está corriendo
curl http://127.0.0.1:8443/api/v1/health
```

---

## 🛡️ Seguridad

⚠️ **Este proyecto es experimental. Úsalo bajo tu propio riesgo.**

**Auditoría:**
- Código completamente abierto para revisión
- Sin dependencias ocultas
- Sin telemetría o phoning home
- Sin actualizaciones automáticas maliciosas

**Recomendaciones:**
1. Audita el código antes de usar en datos críticos
2. Mantén TOR, I2P, IPFS actualizados
3. Usa contraseñas fuertes (20+ caracteres)
4. Guarda Retrieval IDs en lugar seguro
5. Considera VPN + TOR para máximo anonimato

---

## 📖 Licencia

MIT License – Código completamente abierto y libre

```
Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation...
```

---

## 🤝 Contribuciones

Reporta vulnerabilidades de seguridad a:
- 📧 GitHub Issues (público para bugs generales)
- 🔐 Responsable Disclosure para vulnerabilidades críticas

---

## 🔗 Enlaces

- **GitHub:** https://github.com/mar-i0/3ni
- **Issues:** https://github.com/mar-i0/3ni/issues
- **Documentación:** Ver [README.md](README.md)

---

## 📡 Estado del Proyecto

```
✓ Core encryption (Fernet + PBKDF2)
✓ IPFS integration
✓ BitTorrent support
✓ TOR hidden service
✓ I2P support
✓ CLI client
✓ Stateless server
✓ Full documentation

⏳ Storj integration (SDK in progress)
⏳ WebRTC direct transfers
⏳ Shamir Secret Sharing
⏳ Docker containerization
⏳ Web UI client
```

---

## 💬 Disclaimer

```
┌──────────────────────────────────────────────────┐
│  3NI SECURE está diseñado para privacidad y      │
│  seguridad legítimas. Los operadores de sistemas │
│  son responsables del cumplimiento legal en su   │
│  jurisdicción.                                   │
│                                                  │
│  NO SE PROPORCIONA PARA ACTIVIDADES ILEGALES.   │
└──────────────────────────────────────────────────┘
```

---

<div align="center">

### 🔐 Almacenamiento sin identidad. Censura imposible. Control absoluto.

**Made with ❤️ for privacy, security, and freedom**

```
██████╗ ██╗   ██╗ █████╗  █████╗ █████╗ ██╗     ███████╗
██╔═══╝ ██║   ██║██╔══██╗██╔══██╗██╔══██╗██║     ██╔════╝
╚█████╗ ██║   ██║███████║███████║███████║██║     █████╗
 ╚═══██╗██║   ██║██╔══██║██╔══██║██╔══██║██║     ██╔══╝
██████╔╝╚██████╔╝██║  ██║██║  ██║██║  ██║███████╗███████╗
╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝

            Distributed. Encrypted. Anonymous.
```

</div>

---

## 🙏 Agradecimientos

Gracias a **d4c4s4** por las conversaciones e ideas en el coche.
