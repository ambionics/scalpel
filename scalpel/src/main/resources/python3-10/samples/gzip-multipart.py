"""
    GZIP Decompression and Re-Encoding

    This script interacts with an API that gzip compresses its request and response contents.
    
    The target this script was made for encodes utf-16le documents and compress them with GZIP before transmitting it through it's HTTP API.
    
    This script decompresses the gzip encoded content, decodes the utf-16le encoded text, and 
    re-encodes it in latin-1 to get rid of additional zero bytes that would be invisible 
    in plain text and would interfere with editing the plaintext.
"""

import gzip
from pyscalpel import Request, Response


def req_edit_in_fs(req: Request) -> bytes | None:
    """
    Decompresses the gzip content and re-encodes from utf-16le to latin-1.

    Args:
        req: The incoming HTTP request.

    Returns:
        The decompressed and re-encoded content of the HTTP request.
    """
    gz = req.multipart_form["fs"].content
    content = gzip.decompress(gz).decode("utf-16le").encode("latin-1")
    return content


def req_edit_out_fs(req: Request, text: bytes) -> Request | None:
    """
    Encodes the content from latin-1 to utf-16le and compresses it with gzip.

    Args:
        req: The outgoing HTTP request.
        text: The content to be re-encoded and compressed.

    Returns:
        The HTTP request with the re-encoded and compressed content.
    """
    data = text.decode("latin-1").encode("utf-16le")
    content = gzip.compress(data, mtime=0)
    req.multipart_form["fs"].content = content
    return req


def req_edit_in_filetosend(req: Request) -> bytes | None:
    """
    Decompresses the gzip content.

    Args:
        req: The incoming HTTP request.

    Returns:
        The decompressed content of the HTTP request.
    """
    gz = req.multipart_form["filetosend"].content
    content = gzip.decompress(gz)
    return content


def req_edit_out_filetosend(req: Request, text: bytes) -> Request | None:
    """
    Compresses the content with gzip.

    Args:
        req: The outgoing HTTP request.
        text: The content to be compressed.

    Returns:
        The HTTP request with the compressed content.
    """
    data = text
    content = gzip.compress(data, mtime=0)
    req.multipart_form["filetosend"].content = content
    return req


def res_edit_in(res: Response) -> bytes | None:
    """
    Decompresses the gzip content, decodes from utf-16le to utf-8.

    Args:
        res: The incoming HTTP response.

    Returns:
        The decompressed and re-encoded content of the HTTP response.
    """
    gz = res.content
    if not gz:
        return

    content = gzip.decompress(gz)
    content.decode("utf-16le").encode("utf-8")
    return content


def res_edit_out(res: Response, text: bytes) -> Response | None:
    """
    Replaces the content of the HTTP response with the input text.

    Args:
        res: The outgoing HTTP response.
        text: The text to be set as the new content of the response.

    Returns:
        The HTTP response with the new content.
    """
    res.content = text
    return res
