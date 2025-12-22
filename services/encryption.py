"""
Encryption Service for Secure Token Storage

Provides symmetric encryption for sensitive user-scoped tokens using Fernet.

ENCRYPTION SCOPE (User-Scoped Tokens ONLY):
    - linkedin_access_token
    - linkedin_refresh_token  
    - github_access_token (optional)

NOT ENCRYPTED (App-Level Secrets - ENV-ONLY):
    - GROQ_API_KEY
    - LINKEDIN_CLIENT_SECRET
    - UNSPLASH_ACCESS_KEY
    - GITHUB_TOKEN
    These must NEVER be stored in the database.

ENCRYPTION KEY:
    - Loaded from ENCRYPTION_KEY environment variable
    - Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    - Must be 32 bytes, URL-safe base64-encoded

SECURITY NOTES:
    - Fernet provides AES-128-CBC encryption with HMAC authentication
    - Each encrypted value includes a timestamp for key rotation support
    - Graceful fallback for development (warns if key not set)
    - Auto-migration: plaintext tokens encrypted on first access
"""

import os
import base64
import logging

logger = logging.getLogger(__name__)

# Load encryption key from environment
# SECURITY: This key must be kept secret and never committed to version control
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', '')

# Lazy-loaded Fernet instance
_fernet = None


def _get_fernet():
    """
    Get or create the Fernet encryption instance.
    
    Returns:
        Fernet instance or None if key not configured
        
    SECURITY: Logs a warning (not error) if key is missing to allow
    development without encryption, but production MUST have this set.
    """
    global _fernet
    
    if _fernet is not None:
        return _fernet
    
    if not ENCRYPTION_KEY:
        logger.warning(
            "ENCRYPTION_KEY not set. Tokens will be stored in plaintext. "
            "Set ENCRYPTION_KEY environment variable for production."
        )
        return None
    
    try:
        from cryptography.fernet import Fernet
        _fernet = Fernet(ENCRYPTION_KEY.encode())
        return _fernet
    except Exception as e:
        logger.error(f"Failed to initialize encryption: {e}")
        return None


def encrypt_value(plaintext: str) -> str:
    """
    Encrypt a plaintext string value.
    
    Args:
        plaintext: The sensitive value to encrypt
        
    Returns:
        Base64-encoded encrypted string, or original if encryption unavailable
        
    SECURITY:
        - Returns prefixed value (ENC:) to identify encrypted data
        - If encryption fails, returns plaintext with warning
        - Empty/None values return empty string
    """
    if not plaintext:
        return ''
    
    fernet = _get_fernet()
    if not fernet:
        # Development fallback - store plaintext but log warning
        return plaintext
    
    try:
        encrypted = fernet.encrypt(plaintext.encode())
        # Prefix with ENC: to identify encrypted values
        return f"ENC:{encrypted.decode()}"
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        return plaintext


def decrypt_value(encrypted: str) -> str:
    """
    Decrypt an encrypted string value.
    
    Args:
        encrypted: The encrypted value (with ENC: prefix) or plaintext
        
    Returns:
        Decrypted plaintext string
        
    SECURITY:
        - Handles both encrypted (ENC: prefix) and legacy plaintext values
        - Auto-migration: plaintext values are returned as-is for re-encryption
        - Decryption failures return empty string (fail secure)
    """
    if not encrypted:
        return ''
    
    # Check if value is encrypted (has ENC: prefix)
    if not encrypted.startswith('ENC:'):
        # Legacy plaintext value - return as-is for auto-migration
        return encrypted
    
    fernet = _get_fernet()
    if not fernet:
        logger.error("Cannot decrypt: ENCRYPTION_KEY not set")
        return ''
    
    try:
        # Remove ENC: prefix and decrypt
        encrypted_data = encrypted[4:]  # Remove "ENC:" prefix
        decrypted = fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        return ''


def is_encrypted(value: str) -> bool:
    """
    Check if a value is encrypted (has ENC: prefix).
    
    Args:
        value: The value to check
        
    Returns:
        True if encrypted, False if plaintext or empty
    """
    return bool(value and value.startswith('ENC:'))


def mask_token(token: str, visible_chars: int = 8) -> str:
    """
    Create a masked version of a token for display.
    
    Args:
        token: The token to mask (can be encrypted or plaintext)
        visible_chars: Number of characters to show at start and end
        
    Returns:
        Masked string like "AQXr...Xw" or "••••••••" if too short
        
    SECURITY: 
        - NEVER returns the actual token
        - Used for frontend display only
        - Decrypts internally if needed, but only returns masked version
    """
    if not token:
        return ''
    
    # If encrypted, show that it's set but masked
    if is_encrypted(token):
        return '••••••••'
    
    # For plaintext (legacy), mask it
    if len(token) <= visible_chars * 2:
        return '••••••••'
    
    return f"{token[:visible_chars]}...{token[-4:]}"


# =============================================================================
# KEY GENERATION UTILITY
# =============================================================================

def generate_key() -> str:
    """
    Generate a new Fernet encryption key.
    
    Returns:
        URL-safe base64-encoded 32-byte key
        
    Usage:
        Add to .env: ENCRYPTION_KEY=<generated_key>
    """
    from cryptography.fernet import Fernet
    return Fernet.generate_key().decode()


if __name__ == '__main__':
    # CLI utility to generate a new encryption key
    print("Generated ENCRYPTION_KEY:")
    print(generate_key())
    print("\nAdd this to your .env file:")
    print("ENCRYPTION_KEY=<key_above>")
