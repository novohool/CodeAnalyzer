"""Test analyzer module."""

from pathlib import Path
from typing import Dict, Any, List
import re

from .base import BaseAnalyzer

class TestAnalyzer(BaseAnalyzer):
    """Analyzes test files and coverage."""

    def analyze(self) -> Dict[str, Any]:
        """Analyze test files and coverage.
        
        Returns:
            Dict containing test analysis results
        """
        test_info = {
            'test_files': self._analyze_test_files(),
            'coverage': self._analyze_coverage(),
            'test_patterns': self._analyze_test_patterns()
        }
        return {'test_info': test_info}
    
    def _analyze_test_files(self) -> List[Dict[str, Any]]:
        """Analyze test files."""
        test_files = []
        for file in self.repo_path.rglob('*'):
            if file.is_file() and self._is_test_file(file):
                content = file.read_text(encoding='utf-8')
                test_files.append({
                    'path': str(file.relative_to(self.repo_path)),
                    'test_count': self._count_test_cases(content),
                    'test_types': self._get_test_types(content)
                })
        return test_files
    
    def _analyze_coverage(self) -> Dict[str, Any]:
        """Analyze test coverage."""
        coverage = {
            'total': 0,
            'covered': 0,
            'missing': 0,
            'branch_coverage': 0
        }
        
        # Look for coverage report files
        coverage_file = self.repo_path / '.coverage'
        if coverage_file.exists():
            # Parse coverage data
            # This is a simplified version - you might want to use coverage.py library
            try:
                with open(coverage_file, 'r') as f:
                    content = f.read()
                    # Extract coverage numbers using regex
                    total_match = re.search(r'total\s+(\d+)', content)
                    covered_match = re.search(r'covered\s+(\d+)', content)
                    if total_match and covered_match:
                        coverage['total'] = int(total_match.group(1))
                        coverage['covered'] = int(covered_match.group(1))
                        coverage['missing'] = coverage['total'] - coverage['covered']
                        coverage['branch_coverage'] = coverage['covered'] / coverage['total'] * 100
            except Exception:
                pass
        
        return coverage
    
    def _analyze_test_patterns(self) -> Dict[str, List[str]]:
        """Analyze test patterns used."""
        patterns = {
            'unittest': [],
            'pytest': [],
            'doctest': []
        }
        
        for file in self.repo_path.rglob('*'):
            if file.is_file() and self._is_test_file(file):
                content = file.read_text(encoding='utf-8')
                if 'import unittest' in content:
                    patterns['unittest'].append(str(file.relative_to(self.repo_path)))
                if 'import pytest' in content:
                    patterns['pytest'].append(str(file.relative_to(self.repo_path)))
                if '>>>' in content:
                    patterns['doctest'].append(str(file.relative_to(self.repo_path)))
        
        return patterns
    
    def _is_test_file(self, file: Path) -> bool:
        """Check if file is a test file."""
        name = file.name.lower()
        return (name.startswith('test_') or 
                name.endswith('_test.py') or 
                name.endswith('_tests.py') or
                'test' in name)
    
    def _count_test_cases(self, content: str) -> int:
        """Count number of test cases in file."""
        # Count unittest test cases
        unittest_count = len(re.findall(r'def\s+test_', content))
        
        # Count pytest test functions
        pytest_count = len(re.findall(r'def\s+test_', content))
        
        # Count doctest examples
        doctest_count = len(re.findall(r'>>>', content))
        
        return max(unittest_count, pytest_count, doctest_count)
    
    def _get_test_types(self, content: str) -> List[str]:
        """Get types of tests used in file."""
        types = []
        if 'import unittest' in content:
            types.append('unittest')
        if 'import pytest' in content:
            types.append('pytest')
        if '>>>' in content:
            types.append('doctest')
        return types 