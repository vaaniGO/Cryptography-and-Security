from hashlib import sha256
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

def decrypt_message(encrypted_str: str, key: str) -> str:
    try:
        # Derive a valid 16-byte AES key from the alphanumeric key
        valid_key = sha256(key.encode()).digest()[:16]

        # Split the input into IV and ciphertext
        iv_b64_str, ct_b64_str = encrypted_str.split(':')
        iv = base64.b64decode(iv_b64_str)
        ct_bytes = base64.b64decode(ct_b64_str)

        # Set up the cipher
        cipher = Cipher(algorithms.AES(valid_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt the padded data
        decrypted_padded_data = decryptor.update(ct_bytes) + decryptor.finalize()

        # Unpad the decrypted plaintext
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

        # Decode from bytes to string
        plaintext = decrypted_data.decode('utf-8')
        return plaintext

    except Exception as e:
        return f"Decryption failed: {str(e)}"

# Example usage
encrypted_string = "ejVc4RhwkdFPXwsBQjhzLg==:RyQDLSl2CDd1zQDvl0If7fnvzTNZFXnuD6grWyvnUrI="  # <-- replace with actual string
symmetric_key = "eMVT"    # <-- replace with actual key
print(decrypt_message(encrypted_string, symmetric_key))
