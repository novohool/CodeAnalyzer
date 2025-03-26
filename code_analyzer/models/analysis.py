"""Analysis results data model."""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class AnalysisResults(BaseModel):
    """Container for all analysis results."""
    
    metrics: Dict[str, Any] = Field(default_factory=dict)
    dependency: Dict[str, Any] = Field(default_factory=dict)
    framework: Dict[str, Any] = Field(default_factory=dict)
    k8s: Dict[str, Any] = Field(default_factory=dict)
    route: Dict[str, Any] = Field(default_factory=dict)
    structure: Dict[str, Any] = Field(default_factory=dict)
    test: Dict[str, Any] = Field(default_factory=dict)
    
    def update_section(self, section: str, data: Dict[str, Any]) -> None:
        """Update a section of the results.
        
        Args:
            section: Section name to update
            data: Data to update with
        """
        if hasattr(self, section):
            setattr(self, section, data)
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary.
        
        Returns:
            Dictionary representation of results
        """
        return self.model_dump()
        
    def __iter__(self):
        """Make results iterable.
        
        Returns:
            Iterator over sections
        """
        return iter(self.to_dict().items()) 