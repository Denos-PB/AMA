from __future__ import annotations
from typing import Literal

MemoryErrorKind = Literal["config","embed","store","search","empty"]

class MemoryError(Exception):
    def __init__(self, message:str,*,kind: MemoryErrorKind = "store") -> None:
        self.message = message
        self.kind = kind
        super().__init__(message)

    @classmethod
    def config(cls,message:str) -> MemoryError:
        return cls(message,kind="config")
    
    @classmethod
    def embed(cls, message:str) -> MemoryError:
        return cls(message,kind="embed")

    @classmethod
    def store(cls, message: str) -> MemoryError:
        return cls(message, kind="store")
    
    @classmethod
    def search(cls, message: str) -> MemoryError:
        return cls(message, kind="search")