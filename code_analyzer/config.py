"""Configuration settings for the code analyzer."""

from typing import Dict

# Default configuration
DEFAULT_CONFIG: Dict = {
    'route_config': {
        'client': {
            'patterns': [
                'src/App.{js,jsx,ts,tsx}',
                'src/router/**/*.{js,jsx,ts,tsx}',
                'src/routes/**/*.{js,jsx,ts,tsx}',
                'src/pages/**/*.{js,jsx,ts,tsx}'
            ],
            'base_dir': 'client'
        },
        'server': {
            'patterns': [
                'app/api/**/*.py',
                'app/routers/**/*.py',
                'routes/**/*.py',
                'controllers/**/*.py'
            ],
            'base_dir': 'server'
        }
    },
    'file_patterns': {
        'backend': ['.py'],
        'frontend': ['.js', '.jsx', '.ts', '.tsx', '.vue'],
        'k8s': ['.yaml', '.yml'],
        'config': ['.env', '.conf', '.ini'],
        'test': ['test_*.py', '*_test.py', '*.test.js', '*.spec.js']
    },
    'test_config': {
        'coverage_threshold': 80.0,
        'test_dirs': ['tests', 'test', '__tests__'],
        'coverage_dirs': ['coverage', 'htmlcov'],
        'test_frameworks': {
            'python': ['pytest', 'unittest'],
            'javascript': ['jest', 'mocha']
        }
    },
    'output_dir': 'docs',
    'excluded_dirs': ['node_modules', '__pycache__', '.git', 'venv', 'dist', 'build'],
    'max_file_size': 1024 * 1024  # 1MB
} 