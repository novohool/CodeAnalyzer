"""File utility functions."""

from pathlib import Path
from typing import Union, List

def get_file_content(file_path: Union[str, Path]) -> str:
    """Read and return file content.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File content as string
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def is_excluded_path(path: Union[str, Path], exclude_patterns: List[str] = None) -> bool:
    """Check if a path should be excluded from analysis.
    
    Args:
        path: Path to check
        exclude_patterns: List of glob patterns to exclude
        
    Returns:
        True if path should be excluded, False otherwise
    """
    if exclude_patterns is None:
        exclude_patterns = [
            '**/__pycache__/**',
            '**/.git/**',
            '**/.venv/**',
            '**/node_modules/**',
            '**/.pytest_cache/**',
            '**/.coverage',
            '**/*.pyc',
            '**/*.pyo',
            '**/*.pyd'
        ]
        
    path_str = str(path)
    return any(Path(path_str).match(pattern) for pattern in exclude_patterns) 