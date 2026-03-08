# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**3NI SECURE** is a distributed secure storage system implementing three core security principles:

1. **Ni existe la información** – Data distributed across multiple backends (IPFS, Storj, BitTorrent), stored ephemeral-first with no central persistence
2. **Ni nadie puede acceder** – End-to-end encryption using Fernet (AES-128) with PBKDF2-derived keys; server never sees plaintext
3. **Ni te pueden relacionar** – Anonymous network layer (TOR onion + I2P) with stateless architecture; no logs, metadata, or user tracking

The system consists of a Python CLI client for encryption/upload and a stateless FastAPI server that distributes encrypted data across multiple backends.

## Architecture Overview

```
CLIENT LAYER (Python CLI)
├── Encryption (Fernet + PBKDF2 key derivation)
├── Async upload/download with multiple servers
└── CLI interface (main.py → client.py)

ANONYMOUS NETWORK LAYER
├── TOR (SOCKS proxy + hidden service .onion)
└── I2P (router management + .i2p addresses)

SERVER LAYER (FastAPI Stateless)
├── /api/v1/store – Accept encrypted files
├── /api/v1/retrieve – Return encrypted files
├── /api/v1/health – Status without metadata
└── /api/v1/clear – Purge ephemeral cache

STORAGE BACKENDS (Parallel distribution)
├── IPFS (content-addressable, returns CID)
├── Storj (P2P storage contracts, not yet integrated)
└── BitTorrent (DHT-based swarms, .torrent files)
```

### Key Design Principles

- **Stateless server:** No user accounts, sessions, or persistent state; retrieval via anonymous one-time IDs
- **Zero-knowledge architecture:** Encryption happens client-side; server processes opaque bytes only
- **No metadata collection:** Server has no logs, timestamps, IP recording, or user-agent tracking; all cache is ephemeral RAM-only
- **Multi-backend redundancy:** Same encrypted file stored in IPFS + BitTorrent simultaneously for resilience

## Common Commands

### Setup & Development

```bash
# Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Or use automated installer
bash install.sh

# Generate secure password for testing
python main.py keygen
```

### Running the Server

```bash
# Start with TOR + I2P anonymity layers
python main.py server start --tor --i2p

# Start on specific port
python main.py server start --port 9000

# Start with SSL/TLS
python main.py server start --ssl

# Start without anonymity networks (development)
python main.py server start --no-tor --no-i2p
```

### Client Operations

```bash
# Upload encrypted file
python main.py client upload --file datos.txt

# Upload with custom password
python main.py client upload --file datos.txt --password "secure-pass"

# Upload via TOR
python main.py client upload --file datos.txt --tor

# Upload and generate QR code for retrieval ID
python main.py client upload --file datos.txt --qr

# Download encrypted file
python main.py client download --id <RETRIEVAL_ID>

# Download with output path
python main.py client download --id <RETRIEVAL_ID> --output recovered.txt

# Download via TOR
python main.py client download --id <RETRIEVAL_ID> --tor
```

### Testing & Demo

```bash
# Run full interactive demo (creates test file, encrypts, decrypts)
python main.py demo

# Check server health
curl http://127.0.0.1:8443/api/v1/health

# Clear server memory cache
curl http://127.0.0.1:8443/api/v1/clear
```

## File Structure & Relationships

### Core Modules

**`encryption.py`** – Cryptographic layer
- `E2EEncryption.derive_key()` – PBKDF2 key derivation (480k iterations, SHA-256)
- `E2EEncryption.encrypt_file()` – Fernet encryption with salt + hash
- `E2EEncryption.decrypt_file()` – Reverse operation with integrity verification
- Used by: `client.py` (encrypt before upload) and during download (decrypt after retrieval)

**`storage.py`** – Multi-backend distribution
- `IPFSStorage` – Content-addressed storage, returns IPFS CID
- `StorjStorage` – P2P storage contracts (skeleton implementation)
- `BitTorrentStorage` – Creates .torrent files, uses public trackers
- `MultiStorageBackend` – Distributes same encrypted data to all enabled backends simultaneously
- Used by: `server.py` (stores incoming encrypted files) and `client.py` (retrieves from any backend)

**`anonymous_network.py`** – Network anonymity
- `TORNetwork` – Manages TOR daemon, generates .onion hidden service address
- `I2PNetwork` – Manages I2P router, generates .i2p address
- `AnonymousNetworkManager` – Starts/stops both networks, returns active addresses
- Used by: `main.py server start` to initialize anonymity layers

**`server.py`** – FastAPI stateless server
- `POST /api/v1/store` – Receives encrypted file, distributes to backends, returns `retrieval_id` (random, no auth)
- `POST /api/v1/retrieve` – Fetches encrypted file from any backend, returns opaque bytes
- `GET /api/v1/health` – Status check without metadata
- `GET /api/v1/clear` – Clears ephemeral in-memory cache
- Key: No authentication, no logging, no session state, all responses are timing-safe

**`client.py`** – CLI client for encryption & uploads
- `ThreeniClient.upload()` – Encrypts file locally, uploads via aiohttp, returns retrieval info
- `ThreeniClient.download()` – Downloads encrypted file, decrypts locally, saves to disk
- Used by: `main.py client` CLI commands

**`main.py`** – CLI orchestrator
- `@cli.group("server")` – Server management commands
- `@cli.group("client")` – Client commands (upload/download)
- `@cli.command("keygen")` – Generate secure password
- `@cli.command("demo")` – Interactive demo
- Routes commands to appropriate modules

### Configuration

**`config.json`** – Central configuration (all settings documented)
- Storage backends (IPFS URL, Storj API key, BitTorrent tracker)
- Network settings (TOR ports, I2P ports)
- Encryption parameters (PBKDF2 iterations: 480000, salt length: 32)
- Privacy settings (no logging, no metadata, ephemeral cache only)

**`requirements.txt`** – Python dependencies
- FastAPI, aiohttp, cryptography, ipfshttpclient, click, qrcode

## Data Flow

### Upload (Client → Server → Storage Backends)

1. **Client:** User provides file + password
2. **Encryption:** `encryption.py` generates salt, derives key via PBKDF2, encrypts with Fernet
3. **Network:** File routed through TOR/I2P (optional)
4. **Server:** Receives encrypted bytes, distributes to backends
5. **Backends:** IPFS returns CID, BitTorrent creates .torrent, both return location ID
6. **Response:** Server returns anonymous `retrieval_id` + backend locations + file hash

### Download (Client ← Server ← Storage Backends)

1. **Client:** User provides retrieval_id + password
2. **Server:** Queries any available backend (IPFS first, fallback to BitTorrent)
3. **Network:** Encrypted bytes routed through TOR/I2P (optional)
4. **Client:** Receives encrypted bytes, derives key from password + received salt
5. **Decryption:** Fernet decrypts, SHA-256 hash verified for integrity
6. **File:** Saved locally or returned to user

## Key Development Patterns

### Adding New Storage Backend

1. Create new class in `storage.py` inheriting `BaseBackend` pattern (see IPFS/BitTorrent examples)
2. Implement `async def store(data: bytes, filename: str) -> str` returning location ID
3. Implement `async def retrieve(location_id: str) -> Optional[bytes]`
4. Register in `MultiStorageBackend.__init__()` with feature flag
5. Add config entry to `config.json`

### Modifying Encryption Parameters

1. Edit `encryption.py` constants (SALT_LENGTH, iterations in derive_key)
2. Update `config.json` with new values (for transparency)
3. Note: Changing iterations breaks backward compatibility; old files won't decrypt
4. Use versioning (e.g., `encrypt_v2`) for algorithm changes

### Adding CLI Commands

1. Edit `main.py`, add `@cli.command()` or `@cli.group()` decorator
2. Use Click parameters (`@click.option`, `@click.argument`)
3. For async operations, use `asyncio.run()` wrapper
4. Async client operations in `client.py`, import and call from main

## Testing Strategy

The codebase currently lacks automated tests. Recommended additions:

```bash
# Create test directory
mkdir -p tests

# Test modules to create:
# tests/test_encryption.py – Fernet roundtrip, key derivation, integrity checks
# tests/test_storage.py – Mock IPFS/BitTorrent store/retrieve
# tests/test_server.py – API endpoint responses, no-metadata verification
# tests/test_client.py – Upload/download workflow with mock server
# tests/test_integration.py – Full E2E: encrypt → store → retrieve → decrypt

# To run tests (once created):
pytest tests/
pytest tests/test_encryption.py::test_encrypt_decrypt_roundtrip -v
```

## Important Notes for Contributors

- **Security first:** All plaintext handling happens client-side only; server must never log or persist encrypted data
- **No authentication:** Retrieval IDs are random tokens, not linked to user identity; there are no accounts or login mechanisms
- **Stateless design:** Server restarts should have zero impact; no sessions, no databases, no persistent state
- **Network resilience:** Client should retry failed downloads from alternative backends; multiple storage backends provide redundancy
- **Privacy by default:** Any logging, error messages, or monitoring that could leak metadata must be reviewed carefully
- **Dependencies:** Keep stack minimal; avoid heavy frameworks for side features; prefer stdlib and well-audited crypto libraries

## Deployment Notes

- **TOR requirement:** `tor` binary must be in PATH; hidden service takes 2-3 seconds to initialize
- **IPFS requirement:** Requires local `ipfs daemon` running; API endpoint configurable
- **BitTorrent:** No local daemon required; creates .torrent files in `torrents/` directory
- **SSL/TLS:** Use `--ssl` flag with valid cert/key paths for HTTPS; requires `certs/server.crt` and `certs/server.key`
- **Port conflicts:** Default port 8443; use `--port` flag to change
- **Docker:** Project is containerizable but currently no Dockerfile provided

## References

- **README.md** – Full user documentation, architecture diagrams, use cases
- **EXAMPLES.md** – 50+ usage examples, troubleshooting, common workflows
- **config.json** – All configurable parameters documented inline
- **Cryptography library docs** – https://cryptography.io/
- **FastAPI docs** – https://fastapi.tiangolo.com/
