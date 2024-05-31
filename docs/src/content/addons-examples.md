---
title: "Examples"
menu:
    addons:
        weight: 6
---

# Script examples

This page provides example scripts to get familiar with Scalpel's Python library. They are designed for real use cases.

## Table of content

-   [GZIP-ed API](#gzip-ed-api)
-   [Cryptography using a session as a secret](#cryptography-using-a-session-as-a-secret)

## GZIP-ed API

Let's assume you encountered an API using a custom protocol that gzips multiple form-data fields.

Quick-and-dirty Scalpel script to directly edit the unzipped data and find hidden secrets:

```python
from pyscalpel import Request, Response, logger
import gzip


def unzip_bytes(data):
    try:
        # Create a GzipFile object with the input data
        with gzip.GzipFile(fileobj=data) as gz_file:
            # Read the uncompressed data
            uncompressed_data = gz_file.read()
        return uncompressed_data
    except OSError as e:
        logger.error(f"Error: Failed to unzip the data - {e}")


def req_edit_in_fs(req: Request) -> bytes | None:
    gz = req.multipart_form["fs"].content

    # Decode utf-16 and re-encoding to get rid of null bytes in the editor
    content = gzip.decompress(gz).decode("utf-16le").encode("latin-1")
    return content


def req_edit_out_fs(req: Request, text: bytes) -> Request | None:
    data = text.decode("latin-1").encode("utf-16le")
    content = gzip.compress(data, mtime=0)
    req.multipart_form["fs"].content = content
    return req


def req_edit_in_filetosend(req: Request) -> bytes | None:
    gz = req.multipart_form["filetosend"].content
    content = gzip.decompress(gz)
    return content


def req_edit_out_filetosend(req: Request, text: bytes) -> Request | None:
    data = text
    content = gzip.compress(data, mtime=0)
    req.multipart_form["filetosend"].content = content
    return req


def res_edit_in(res: Response) -> bytes | None:
    gz = res.content
    if not gz:
        return

    content = gzip.decompress(gz)
    content.decode("utf-16le").encode("utf-8")
    return content


def res_edit_out(res: Response, text: bytes) -> Response | None:
    res.content = text
    return res
```

## Cryptography using a session as a secret

In this case, the client encrypted its form data using a session token obtained upon authentication.

This script demonstrates that Scalpel can be easily used to deal with **stateful behaviors**:

> 💡 Find a mock API to test this case in Scalpel's GitHub repository: [`test/server.js`](https://github.com/ambionics/scalpel/blob/4b935cb29b496f3627a319d963a009dda79a1aa7/test/server.js#L117C1-L118C1).

```python
from pyscalpel import Request, Response, Flow
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode


session: bytes = b""


def match(flow: Flow) -> bool:
    return flow.path_is("/encrypt-session*") and bool(
        session or flow.request.method != "POST"
    )


def get_cipher(secret: bytes, iv=bytes(16)):
    hasher = SHA256.new()
    hasher.update(secret)
    derived_aes_key = hasher.digest()[:32]
    cipher = AES.new(derived_aes_key, AES.MODE_CBC, iv)
    return cipher


def decrypt(secret: bytes, data: bytes) -> bytes:
    data = b64decode(data)
    cipher = get_cipher(secret)
    decrypted = cipher.decrypt(data)
    return unpad(decrypted, AES.block_size)


def encrypt(secret: bytes, data: bytes) -> bytes:
    cipher = get_cipher(secret)
    padded_data = pad(data, AES.block_size)
    encrypted = cipher.encrypt(padded_data)
    return b64encode(encrypted)


def response(res: Response) -> Response | None:
    if res.request.method == "GET":
        global session
        session = res.content or b""
        return


def req_edit_in_encrypted(req: Request) -> bytes:
    secret = session
    encrypted = req.form[b"encrypted"]
    if not encrypted:
        return b""

    return decrypt(secret, encrypted)


def req_edit_out_encrypted(req: Request, text: bytes) -> Request:
    secret = session
    req.form[b"encrypted"] = encrypt(secret, text)
    return req


def res_edit_in_encrypted(res: Response) -> bytes:
    secret = session
    encrypted = res.content

    if not encrypted:
        return b""

    return decrypt(secret, encrypted)


def res_edit_out_encrypted(res: Response, text: bytes) -> Response:
    secret = session
    res.content = encrypt(secret, text)
    return res
```

---

> If you encountered an interesting case, feel free to contact us to add it!
