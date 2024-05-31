"""
    AES Encryption and Decryption

    Requires pycryptodome:
    $ pip install pycrytodome

    This script demonstrates the use of AES encryption and decryption in HTTP requests and responses.
    It uses the pycryptodome library to perform AES encryption and decryption, and SHA256 for key derivation.
    The script acts on paths matching "/encrypt" and where the request form has a "secret" field.
    
"""

from pyscalpel import Request, Response, Flow
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode


def match(flow: Flow) -> bool:
    """
    Matches if the request path is '/encrypt' and if 'secret' is in the form of the request.

    Args:
        flow: The flow object representing the HTTP transaction.

    Returns:
        True if the request path matches and 'secret' is present, otherwise False.
    """
    return flow.path_is("/encrypt") and flow.request.form.get(b"secret") is not None


def get_cipher(secret: bytes, iv=bytes(16)):
    """
    Constructs an AES cipher object using a derived AES key from the provided secret and an initialization vector.

    Args:
        secret: The secret to derive the AES key from.
        iv: The initialization vector.

    Returns:
        The AES cipher object.
    """
    hasher = SHA256.new()
    hasher.update(secret)
    derived_aes_key = hasher.digest()[:32]
    cipher = AES.new(derived_aes_key, AES.MODE_CBC, iv)
    return cipher


def decrypt(secret: bytes, data: bytes) -> bytes:
    """
    Decrypts the base64-encoded, AES-encrypted data using the provided secret.

    Args:
        secret: The secret to use for decryption.
        data: The base64-encoded, AES-encrypted data.

    Returns:
        The decrypted data.
    """
    data = b64decode(data)
    cipher = get_cipher(secret)
    decrypted = cipher.decrypt(data)
    return unpad(decrypted, AES.block_size)


def encrypt(secret: bytes, data: bytes) -> bytes:
    """
    Encrypts the data using the provided secret and AES encryption, and then base64-encodes it.

    Args:
        secret: The secret to use for encryption.
        data: The data to encrypt.

    Returns:
        The base64-encoded, AES-encrypted data.
    """
    cipher = get_cipher(secret)
    padded_data = pad(data, AES.block_size)
    encrypted = cipher.encrypt(padded_data)
    return b64encode(encrypted)


def req_edit_in_encrypted(req: Request) -> bytes | None:
    """
    Decrypts the 'encrypted' field in the incoming HTTP request's form using the 'secret' field.

    Args:
        req: The incoming HTTP request.

    Returns:
        The decrypted content of the 'encrypted' field.
    """
    secret = req.form[b"secret"]
    encrypted = req.form[b"encrypted"]
    if not encrypted:
        return b""

    return decrypt(secret, encrypted)


def req_edit_out_encrypted(req: Request, text: bytes) -> Request:
    """
    Encrypts the provided text using the 'secret' field in the outgoing HTTP request's form, and sets it as the 'encrypted' field.

    Args:
        req: The outgoing HTTP request.
        text: The text to encrypt.

    Returns:
        The modified HTTP request with the encrypted text.
    """
    secret = req.form[b"secret"]
    req.form[b"encrypted"] = encrypt(secret, text)
    return req


def res_edit_in_encrypted(res: Response) -> bytes | None:
    """
    Decrypts the incoming HTTP response's content using the 'secret' field in the associated request's form.

    Args:
        res: The incoming HTTP response.

    Returns:
        The decrypted content.
    """
    secret = res.request.form[b"secret"]
    encrypted = res.content

    if not encrypted:
        return b""

    return decrypt(secret, encrypted)


def res_edit_out_encrypted(res: Response, text: bytes) -> Response:
    """
    Encrypts the provided text using the 'secret' field in the associated request's form, and sets it as the outgoing HTTP response's content.

    Args:
        res: The outgoing HTTP response.
        text: The text to encrypt.

    Returns:
        The modified HTTP response with the encrypted text.
    """
    secret = res.request.form[b"secret"]
    res.content = encrypt(secret, text)
    return res
