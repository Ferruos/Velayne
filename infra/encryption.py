"""Encryption utilities using Fernet for securing sensitive data."""

import base64
import os
from typing import Optional

from cryptography.fernet import Fernet

from .config import settings


class EncryptionManager:
    """Manages encryption and decryption of sensitive strings using Fernet."""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize the encryption manager.
        
        Args:
            encryption_key: Base64-encoded Fernet key. If None, uses settings.encryption_key
        """
        key = encryption_key or settings.encryption_key
        
        if not key:
            # Generate a new key if none provided (for first-time setup)
            key = Fernet.generate_key().decode()
            print(f"Generated new encryption key: {key}")
            print("Add this to your .env file as ENCRYPTION_KEY=")
        
        try:
            # Ensure key is bytes
            if isinstance(key, str):
                key = key.encode()
            self._fernet = Fernet(key)
        except Exception as e:
            raise ValueError(f"Invalid encryption key: {e}")
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string.
        
        Args:
            plaintext: The string to encrypt
            
        Returns:
            Base64-encoded encrypted string
            
        Raises:
            ValueError: If plaintext is empty or encryption fails
        """
        if not plaintext or not isinstance(plaintext, str):
            raise ValueError("Plaintext must be a non-empty string")
        
        try:
            encrypted_bytes = self._fernet.encrypt(plaintext.encode())
            return base64.b64encode(encrypted_bytes).decode()
        except Exception as e:
            raise ValueError(f"Encryption failed: {e}")
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt an encrypted string.
        
        Args:
            ciphertext: Base64-encoded encrypted string
            
        Returns:
            Decrypted plaintext string
            
        Raises:
            ValueError: If ciphertext is invalid or decryption fails
        """
        if not ciphertext or not isinstance(ciphertext, str):
            raise ValueError("Ciphertext must be a non-empty string")
        
        try:
            encrypted_bytes = base64.b64decode(ciphertext.encode())
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")
    
    def is_encrypted(self, text: str) -> bool:
        """
        Check if a string appears to be encrypted (basic heuristic).
        
        Args:
            text: String to check
            
        Returns:
            True if string appears to be encrypted, False otherwise
        """
        try:
            # Try to decode as base64 and decrypt
            self.decrypt(text)
            return True
        except:
            return False


# Global encryption manager instance
encryption_manager = EncryptionManager()


def encrypt_string(plaintext: str) -> str:
    """
    Convenience function to encrypt a string.
    
    Args:
        plaintext: String to encrypt
        
    Returns:
        Encrypted string
    """
    return encryption_manager.encrypt(plaintext)


def decrypt_string(ciphertext: str) -> str:
    """
    Convenience function to decrypt a string.
    
    Args:
        ciphertext: Encrypted string to decrypt
        
    Returns:
        Decrypted string
    """
    return encryption_manager.decrypt(ciphertext)


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key.
    
    Returns:
        Base64-encoded encryption key
    """
    return Fernet.generate_key().decode()