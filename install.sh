#!/bin/bash

# Script de instalación para 3NI Secure
# Soporta Ubuntu, Debian, Fedora, macOS

set -e

echo "╔════════════════════════════════════════════════════╗"
echo "║    3NI SECURE - Script de Instalación v1.0        ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Detectar sistema operativo
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            echo "debian"
        elif [ -f /etc/redhat-release ]; then
            echo "fedora"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)
echo "🖥️  Sistema detectado: $OS"
echo ""

# Función para instalar paquetes
install_packages() {
    echo "📦 Instalando dependencias del sistema..."

    case $OS in
        debian)
            sudo apt-get update
            sudo apt-get install -y \
                python3 python3-pip python3-venv \
                tor i2p \
                go-ipfs \
                build-essential libssl-dev \
                git curl wget
            ;;
        fedora)
            sudo dnf install -y \
                python3 python3-pip \
                tor i2p \
                go-ipfs \
                gcc openssl-devel \
                git curl wget
            ;;
        macos)
            if ! command -v brew &> /dev/null; then
                echo "📦 Instalando Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install \
                python3 \
                tor \
                go-ipfs
            ;;
        *)
            echo "⚠️  Sistema no reconocido. Instala manualmente:"
            echo "   - Python 3.10+"
            echo "   - TOR"
            echo "   - I2P"
            echo "   - IPFS"
            ;;
    esac

    echo "✓ Dependencias del sistema instaladas"
}

# Crear entorno virtual
setup_venv() {
    echo ""
    echo "🐍 Configurando entorno virtual Python..."

    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi

    source venv/bin/activate

    # Actualizar pip
    pip install --upgrade pip setuptools wheel

    # Instalar dependencias Python
    echo "📚 Instalando dependencias Python..."
    pip install -r requirements.txt

    echo "✓ Entorno virtual configurado"
}

# Crear directorios necesarios
setup_directories() {
    echo ""
    echo "📁 Creando directorios..."

    mkdir -p torrents
    mkdir -p certs
    mkdir -p logs
    mkdir -p ~/.tor/3ni
    mkdir -p ~/.i2p/3ni
    mkdir -p ~/.cache/3ni

    echo "✓ Directorios creados"
}

# Generar certificados SSL (opcional)
setup_ssl() {
    echo ""
    echo "🔐 Configurar SSL/TLS? (opcional, para producción)"
    read -p "¿Generar certificados autofirmados? (s/n): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Ss]$ ]]; then
        if [ ! -d "certs" ]; then
            mkdir -p certs
        fi

        echo "📜 Generando certificados autofirmados..."
        openssl req -x509 -newkey rsa:4096 -keyout certs/server.key \
            -out certs/server.crt -days 365 -nodes \
            -subj "/CN=localhost/O=3NI/C=XX"

        chmod 600 certs/server.key
        echo "✓ Certificados generados en certs/"
    fi
}

# Verificar instalación
verify_installation() {
    echo ""
    echo "✓ Verificando instalación..."

    # Python
    if python3 --version > /dev/null 2>&1; then
        echo "  ✓ Python: $(python3 --version)"
    else
        echo "  ✗ Python no encontrado"
    fi

    # TOR
    if command -v tor &> /dev/null; then
        echo "  ✓ TOR: instalado"
    else
        echo "  ⚠️  TOR: no encontrado (instálalo manualmente)"
    fi

    # IPFS
    if command -v ipfs &> /dev/null; then
        echo "  ✓ IPFS: instalado"
    else
        echo "  ⚠️  IPFS: no encontrado (instálalo manualmente)"
    fi

    # Dependencias Python
    if python3 -c "import fastapi, cryptography, aiohttp" 2>/dev/null; then
        echo "  ✓ Dependencias Python: instaladas"
    else
        echo "  ⚠️  Algunas dependencias Python faltan"
    fi
}

# Mostrar instrucciones finales
show_instructions() {
    echo ""
    echo "╔════════════════════════════════════════════════════╗"
    echo "║          ¡Instalación completada! 🎉              ║"
    echo "╚════════════════════════════════════════════════════╝"
    echo ""
    echo "📖 Próximos pasos:"
    echo ""
    echo "1. Activar entorno virtual:"
    echo "   source venv/bin/activate"
    echo ""
    echo "2. Iniciar el servidor:"
    echo "   python main.py server start --tor --i2p"
    echo ""
    echo "3. En otra terminal, encriptar y subir un archivo:"
    echo "   source venv/bin/activate"
    echo "   python main.py client upload --file tu_archivo.txt"
    echo ""
    echo "4. Recuperar archivo:"
    echo "   python main.py client download --id RETRIEVAL_ID"
    echo ""
    echo "📚 Documentación: cat README.md"
    echo ""
    echo "💡 Demo rápida:"
    echo "   python main.py demo"
    echo ""
}

# Main
main() {
    install_packages
    setup_venv
    setup_directories
    setup_ssl
    verify_installation
    show_instructions
}

# Ejecutar
main
