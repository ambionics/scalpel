"""
    AES Encryption and Decryption with Session

    Requires pycryptodome:
    $ pip install pycrytodome

    This script demonstrates the use of AES encryption and decryption in HTTP requests and responses, with the preservation of session state.
    The session state is maintained across calls and is not reset, demonstrating the capability of preserving global state.
    It uses the pycryptodome library to perform AES encryption and decryption, and SHA256 for key derivation.
    The script acts on paths starting with "/encrypt-session" and where the request method is not POST, or where a session is already established.
"""

from pyscalpel import Request, Response, Flow
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode


session: bytes = b""  # Global variable for session preservation


def match(flow: Flow) -> bool:
    """
    Matches if the request path starts with '/encrypt-session' and the session is set or the request method is not 'POST'.

    Args:
        flow: The flow object representing the HTTP transaction.

    Returns:
        True if the request path and request method match the conditions, otherwise False.
    """
    return flow.path_is("/encrypt-session*") and bool(
        session or flow.request.method != "POST"
    )


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


def response(res: Response) -> Response | None:
    """
    If the request method is 'GET', sets the global session variable to the response's content.

    Args:
        res: The incoming HTTP response.

    Returns:
        None.
    """
    if res.request.method == "GET":
        global session
        session = res.content or b""
        return


def req_edit_in_encrypted(req: Request) -> bytes:
    """
    Decrypts the 'encrypted' field in the incoming HTTP request's form using the session.

    Args:
        req: The incoming HTTP request.

    Returns:
        The decrypted content of the 'encrypted' field.
    """
    secret = session
    encrypted = req.form[b"encrypted"]
    if not encrypted:
        return b""

    return decrypt(secret, encrypted)


def req_edit_out_encrypted(req: Request, text: bytes) -> Request:
    """
    Encrypts the provided text using the session, and sets it as the 'encrypted' field in the outgoing HTTP request's form.

    Args:
        req: The outgoing HTTP request.
        text: The text to encrypt.

    Returns:
        The modified HTTP request with the encrypted text.
    """
    secret = session
    req.form[b"encrypted"] = encrypt(secret, text)
    return req


def res_edit_in_encrypted(res: Response) -> bytes:
    """
    Decrypts the incoming HTTP response's content using the session.

    Args:
        res: The incoming HTTP response.

    Returns:
        The decrypted content.
    """
    secret = session
    encrypted = res.content

    if not encrypted:
        return b""

    return decrypt(secret, encrypted)


def res_edit_out_encrypted(res: Response, text: bytes) -> Response:
    """
    Encrypts the provided text using the session, and sets it as the outgoing HTTP response's content.

    Args:
        res: The outgoing HTTP response.
        text: The text to encrypt.

    Returns:
        The modified HTTP response with the encrypted text.
    """
    secret = session
    res.content = encrypt(secret, text)
    return res
