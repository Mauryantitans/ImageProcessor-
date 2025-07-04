from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np

class ImageOperation(ABC):
    """Base class for all image processing operations."""
    
    def __init__(self, name: str, description: str, icon: str):
        self.name = name
        self.description = description
        self.icon = icon
        self._params = self.default_params()

    @abstractmethod
    def process(self, image: np.ndarray) -> np.ndarray:
        """Process the image using current parameters."""
        pass

    @abstractmethod
    def default_params(self) -> Dict[str, Any]:
        """Return default parameters for the operation."""
        pass

    def get_params(self) -> Dict[str, Any]:
        """Get current parameters."""
        return self._params

    def set_params(self, params: Dict[str, Any]) -> None:
        """Set operation parameters."""
        for key, value in params.items():
            if key in self._params:
                self._params[key] = value

    @abstractmethod
    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        """Return parameter schema for UI generation."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert operation to dictionary representation."""
        return {
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'params': self.get_params(),
            'schema': self.param_schema()
        } 