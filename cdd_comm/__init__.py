"""
Casio Digital Diaries serial communication protocol.
"""

try:
    from .decoder import Decoder
except ModuleNotFoundError:
    pass
else:
    __all__ = ["Decoder"]
