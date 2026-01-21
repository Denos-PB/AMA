from abc import ABC,abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel

class WorkerResult(BaseModel):
    """Standard result format for all workers."""
    success: bool
    output: Optional[Any] = None
    error: Optional[Any] = None
    metadata: Dict[str,Any] = {}

class BaseWorker(ABC):
    """Base class for all generation workers."""

    def __init__(self, config: Dict[str,Any]):
        self.config = config

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> WorkerResult:
        """Process input and return result."""
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input before processing."""
        pass