# 3NI SECURE - Ejemplos de Uso

## 1. Setup Inicial

### Instalación automática

```bash
bash install.sh
```

### Instalación manual

```bash
# Clonar repositorio
git clone https://github.com/mar-i0/3NI.git
cd 3NI

# Instalar dependencias del sistema (Ubuntu/Debian)
sudo apt-get install python3 python3-pip tor i2p go-ipfs

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias Python
pip install -r requirements.txt

# Crear directorios necesarios
mkdir -p torrents certs logs ~/.tor/3ni ~/.i2p/3ni
```

---

## 2. Ejecutar Servidor

### Inicio básico (localhost solamente)

```bash
python main.py server start
```

Salida:
```
🚀 Iniciando 3NI Secure Server...

🔗 Configurando redes anónimas...
   🧅 TOR (Onion): http://abc123def456.onion
   🌐 I2P: http://uvwxyz1234.i2p

📡 Servidor disponible en: http://127.0.0.1:8443

✓ Servidor en espera de conexiones...
```

### Inicio con opciones

```bash
# Sin TOR
python main.py server start --no-tor

# Sin I2P
python main.py server start --no-i2p

# Con SSL/TLS
python main.py server start --ssl

# Puerto personalizado
python main.py server start --port 9000

# Combinado
python main.py server start --port 9000 --tor --no-i2p --ssl
```

---

## 3. Encriptar y Subir Archivos

### Ejemplo 1: Archivo simple

```bash
# Crear archivo de prueba
echo "Este es mi secreto" > secreto.txt

# Encriptar y subir (contraseña interactiva)
python main.py client upload --file secreto.txt

# Solicitará:
# Contraseña: ••••••••
# Repetir para confirmar: ••••••••

# Salida:
# ============================================================
# INFORMACIÓN DE RECUPERACIÓN
# ============================================================
# Retrieval ID: abc123xyz_defghijk_...
# Hash:         1a2b3c4d5e6f7a8b9c...
# Tamaño:       18 bytes
#
# Ubicaciones:
#   ipfs           QmABC123DEF456...
#   bittorrent     abc123xyz.torrent
# ============================================================
```

### Ejemplo 2: Archivo grande

```bash
# Crear archivo de 100 MB
dd if=/dev/urandom of=datos_grandes.bin bs=1M count=100

# Encriptar (lentitud esperada: ~10-30 segundos)
python main.py client upload --file datos_grandes.bin
```

### Ejemplo 3: Con contraseña en línea

```bash
python main.py client upload \
  --file documento.pdf \
  --password "Mi-Contraseña-Super-Segura-12345"
```

### Ejemplo 4: Generar código QR

```bash
python main.py client upload \
  --file presentacion.pptx \
  --qr

# Genera: retrieval_qr.png
# Contiene: Retrieval ID, Hash y ubicaciones
```

### Ejemplo 5: Especificar servidor

```bash
# Subir a servidor local
python main.py client upload \
  --file datos.txt \
  --server http://127.0.0.1:8443

# Subir a servidor remoto en TOR
python main.py client upload \
  --file datos.txt \
  --server http://abc123def456.onion
```

### Ejemplo 6: Usar TOR para conexión

```bash
# Asume TOR en puerto 9050 (por defecto)
python main.py client upload \
  --file secreto_politico.txt \
  --tor

# Salida:
# 🧅 Usando TOR...
# 📤 Subiendo a http://127.0.0.1:8443...
# ✓ Archivo subido exitosamente
```

### Ejemplo 7: Usar I2P

```bash
python main.py client upload \
  --file archivos_censurados.zip \
  --i2p
```

---

## 4. Descargar y Desencriptar

### Ejemplo 1: Descarga básica

```bash
python main.py client download \
  --id abc123xyz_defghijk_...

# Solicitará contraseña:
# Contraseña: ••••••••••

# Salida:
# 📥 Descargando desde servidor...
# ✓ Descargado: 18 bytes
# 🔓 Desencriptando...
# ✓ Archivo recuperado: 18 bytes
```

### Ejemplo 2: Guardar en ubicación específica

```bash
python main.py client download \
  --id abc123xyz_defghijk_ \
  --output recuperado.txt \
  --password "Mi-Contraseña-Super-Segura-12345"

# Salida:
# ✓ Archivo recuperado: 18 bytes
# ✓ Guardado en: recuperado.txt
```

### Ejemplo 3: A través de TOR

```bash
python main.py client download \
  --id abc123xyz_defghijk_ \
  --tor
```

---

## 5. Flujos Completos de Ejemplo

### Caso de Uso: Whistleblower

```bash
#!/bin/bash
# whistleblower.sh - Subir documento confidencial de forma segura

# 1. Generar contraseña segura
PASS=$(python main.py keygen | grep "Contraseña" | awk '{print $NF}')
echo "Contraseña generada: $PASS"

# 2. Crear documento
cat > documento_secreto.txt << EOF
Información confidencial:
- Nombre: Anónimo
- Fecha: 2025-03-08
- Detalles del abuso...
EOF

# 3. Encriptar y subir vía TOR
python main.py client upload \
  --file documento_secreto.txt \
  --password "$PASS" \
  --server http://abc123.onion \
  --tor

# 4. Guardar información de recuperación
# (Compartir con periodista vía canal seguro)

# 5. Limpiar datos locales
shred -vfz documento_secreto.txt
unset PASS
```

### Caso de Uso: Backup Distribuido

```bash
#!/bin/bash
# backup_distribuido.sh

# Archivos a respaldar
FILES=(
  "~/documentos_importantes/"
  "~/datos_medicos.pdf"
  "~/configuracion_privada.zip"
)

for file in "${FILES[@]}"; do
  echo "Respaldando: $file"

  # Comprimir
  tar -czf "${file##*/}.tar.gz" "$file"

  # Encriptar y distribuir
  python main.py client upload \
    --file "${file##*/}.tar.gz" \
    --server http://127.0.0.1:8443

  # Limpiar archivo comprimido
  rm "${file##*/}.tar.gz"
done

echo "✓ Backup distribuido completado"
```

### Caso de Uso: Sincronización Segura Entre Máquinas

**Máquina A (Origen):**
```bash
# Encriptar datos a compartir
python main.py client upload \
  --file datos_sincronizar.zip \
  --password "clave-compartida-segura" \
  --qr

# Escanear QR con Máquina B
```

**Máquina B (Destino):**
```bash
# Leer información del QR
python main.py client download \
  --id RETRIEVAL_ID_DEL_QR \
  --password "clave-compartida-segura" \
  --output datos_sincronizar.zip
```

---

## 6. Utilidades y Herramientas

### Generar contraseña segura

```bash
python main.py keygen

# Salida:
# 🔑 Contraseña generada:
# eB7x_qK9mN2pL5oR8sT1uV4wX6yZ9aB3cD5eF7gH9j-KlMnOpQr
#
# ⚠️  Guárdala en un lugar seguro
```

### Ver estado del servidor

```bash
curl -s http://127.0.0.1:8443/api/v1/health | python -m json.tool

# Salida:
# {
#   "status": "online",
#   "backends": [
#     "ipfs",
#     "bittorrent"
#   ],
#   "timestamp": null
# }
```

### Limpiar caché del servidor

```bash
curl -X GET http://127.0.0.1:8443/api/v1/clear | python -m json.tool

# Salida:
# {
#   "status": "success",
#   "cleared_entries": 5
# }
```

---

## 7. Demostración Interactiva

### Demo automática

```bash
python main.py demo

# Salida:
# 📝 Archivo de prueba creado: test_secret.txt
# 🔐 Encriptando con contraseña: abc123def456xyz789...
# ✓ Encriptado: 40 bytes
# ✓ Hash: a1b2c3d4e5f6g7h8...
# ✓ Desencriptado: Este es un archivo secreto para 3NI Secure
# ✓ Demo completada
```

---

## 8. Problemas Comunes

### Error: "TOR no está instalado"

```bash
# Ubuntu/Debian
sudo apt-get install tor

# macOS
brew install tor

# Fedora
sudo dnf install tor
```

### Error: "IPFS API no disponible"

```bash
# Iniciar daemon IPFS
ipfs daemon

# En otra terminal, ejecutar comandos
python main.py client upload --file datos.txt
```

### Error: "Puerto 8443 en uso"

```bash
# Usar puerto diferente
python main.py server start --port 9000

# Cliente debe apuntar al nuevo puerto
python main.py client upload \
  --file datos.txt \
  --server http://127.0.0.1:9000
```

### Error: "Conexión rechazada"

```bash
# Verificar que el servidor está corriendo
curl -v http://127.0.0.1:8443/api/v1/health

# Si no funciona, iniciar servidor:
python main.py server start &

# Esperar 2 segundos para que inicie
sleep 2

# Intentar de nuevo
python main.py client upload --file datos.txt
```

---

## 9. Depuración

### Modo verbose (mostrar logs)

```bash
# Requiere modificar logging en código
# Editar server.py y cambiar log_level="warning" a log_level="debug"
```

### Inspeccionar metadatos de archivo

```bash
# Ver hash del archivo original
sha256sum datos.txt

# Ver información de almacenamiento
python -c "
import json
result = {
    'retrieval_id': 'abc123...',
    'hash': 'def456...',
    'locations': {'ipfs': 'Qm...', 'bt': '...'}
}
print(json.dumps(result, indent=2))
"
```

---

## 10. Cheat Sheet

```bash
# Instalación
bash install.sh

# Servidor
python main.py server start --tor --i2p

# Subir
python main.py client upload --file archivo.txt

# Descargar
python main.py client download --id RETRIEVAL_ID

# Generar contraseña
python main.py keygen

# Demo
python main.py demo

# Health check
curl http://127.0.0.1:8443/api/v1/health

# Limpiar
curl http://127.0.0.1:8443/api/v1/clear
```

---

¡Disfruta usando 3NI SECURE! 🔐
