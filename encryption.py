"""
Módulo de encriptación E2E con clave derivada del usuario.
Garantiza: Ni nadie puede acceder a ella
"""

import os
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64


class E2EEncryption:
    """Encriptación de punto a punto, derivada de clave del usuario."""

    SALT_LENGTH = 32

    @staticmethod
    def derive_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
        """
        Deriva una clave a partir de contraseña usando PBKDF2.
        Retorna: (clave_derivada, salt_usado)
        """
        if salt is None:
            salt = os.urandom(E2EEncryption.SALT_LENGTH)

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt

    @staticmethod
    def encrypt_file(file_path: str, password: str) -> tuple[bytes, bytes, bytes]:
        """
        Encripta un archivo.
        Retorna: (datos_cifrados, salt, file_hash)
        """
        with open(file_path, 'rb') as f:
            plaintext = f.read()

        # Calcular hash del archivo original (para verificación)
        file_hash = hashlib.sha256(plaintext).digest()

        # Derivar clave
        key, salt = E2EEncryption.derive_key(password)

        # Encriptar
        cipher = Fernet(key)
        ciphertext = cipher.encrypt(plaintext)

        return ciphertext, salt, file_hash

    @staticmethod
    def decrypt_file(ciphertext: bytes, password: str, salt: bytes) -> bytes:
        """
        Desencripta datos cifrados.
        """
        key, _ = E2EEncryption.derive_key(password, salt)
        cipher = Fernet(key)
        plaintext = cipher.decrypt(ciphertext)
        return plaintext

    @staticmethod
    def verify_integrity(plaintext: bytes, file_hash: bytes) -> bool:
        """Verifica la integridad del archivo desencriptado."""
        return hashlib.sha256(plaintext).digest() == file_hash
