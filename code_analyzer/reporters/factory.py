"""Reporter factory module."""

from typing import Dict, Type

from .base import BaseReporter
from .html_reporter import HTMLReporter
from .text_reporter import TextReporter

class ReporterFactory:
    """Factory class for creating reporters."""
    
    _reporters: Dict[str, Type[BaseReporter]] = {
        'html': HTMLReporter,
        'text': TextReporter
    }
    
    @classmethod
    def create(cls, reporter_type: str, output_dir: str, **kwargs) -> BaseReporter:
        """Create a reporter instance.
        
        Args:
            reporter_type: Type of reporter to create ('html' or 'text')
            output_dir: Directory to save reports
            **kwargs: Additional arguments to pass to reporter constructor
            
        Returns:
            Reporter instance
            
        Raises:
            ValueError: If reporter_type is not supported
        """
        reporter_class = cls._reporters.get(reporter_type.lower())
        if reporter_class is None:
            supported = ', '.join(cls._reporters.keys())
            raise ValueError(
                f"Unsupported reporter type: {reporter_type}. "
                f"Supported types are: {supported}"
            )
        
        return reporter_class(output_dir=output_dir, **kwargs)
    
    @classmethod
    def register(cls, name: str, reporter_class: Type[BaseReporter]) -> None:
        """Register a new reporter type.
        
        Args:
            name: Name of the reporter type
            reporter_class: Reporter class to register
            
        Raises:
            ValueError: If name is already registered
            TypeError: If reporter_class is not a subclass of BaseReporter
        """
        if name in cls._reporters:
            raise ValueError(f"Reporter type '{name}' is already registered")
        
        if not issubclass(reporter_class, BaseReporter):
            raise TypeError(
                f"Reporter class must be a subclass of BaseReporter, "
                f"got {reporter_class.__name__}"
            )
        
        cls._reporters[name] = reporter_class
    
    @classmethod
    def get_supported_types(cls) -> list[str]:
        """Get list of supported reporter types.
        
        Returns:
            List of supported reporter type names
        """
        return list(cls._reporters.keys()) 