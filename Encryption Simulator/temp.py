from flask import Flask, render_template, url_for, abort, jsonify, request
import math
from sympy import isprime
import random
import random
from hashlib import sha256
from cryptography.fernet import Fernet
import base64
import os
# For the AES cipher, algorithm, and mode of operation
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# For the padding schemes (e.g., PKCS7)
from cryptography.hazmat.primitives import padding

# To get the default backend for cryptographic operations
from cryptography.hazmat.backends import default_backend

def test_encryption_decryption():
    """Test function to verify encryption/decryption works correctly"""
    test_message = "Hello, World!"
    test_key = "my_secret_key"
    
    # Encrypt
    valid_key = sha256(test_key.encode()).digest()[:16]
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(valid_key), modes.CBC(iv), backend=default_backend())
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(test_message.encode('utf-8')) + padder.finalize()
    encryptor = cipher.encryptor()
    ct_bytes = encryptor.update(padded_data) + encryptor.finalize()
    
    # Create encrypted string
    iv_b64_str = base64.b64encode(iv).decode('utf-8')
    ct_b64_str = base64.b64encode(ct_bytes).decode('utf-8')
    encrypted_str = f"{iv_b64_str}:{ct_b64_str}"
    
    # Decrypt
    iv_b64_str, ct_b64_str = encrypted_str.split(':')
    iv = base64.b64decode(iv_b64_str)
    ct_bytes = base64.b64decode(ct_b64_str)
    cipher = Cipher(algorithms.AES(valid_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(ct_bytes) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data)
    plaintext = decrypted_data.decode('utf-8')
    
    print(f"Test - Original: {test_message}")
    print(f"Test - Decrypted: {plaintext}")
    print(f"Test - Match: {test_message == plaintext}")
    
    return test_message == plaintext

