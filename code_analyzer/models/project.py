"""Project information data models."""

from typing import List, Optional
from pydantic import BaseModel, Field

class ProjectInfo(BaseModel):
    """Project basic information."""
    name: str
    description: str = ''
    version: str = ''
    author: str = ''
    license: str = ''
    repository: Optional[str] = None
    homepage: Optional[str] = None
    features: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)

class DependencyInfo(BaseModel):
    """Package dependency information."""
    name: str
    version: str
    type: str = 'runtime'  # runtime, dev, peer, optional
    source: str = 'npm'    # npm, pip, etc.

class FrameworkInfo(BaseModel):
    """Framework information."""
    name: Optional[str] = None
    version: Optional[str] = None
    major_packages: List[str] = Field(default_factory=list)
    build_tools: List[str] = Field(default_factory=list)

class DatabaseInfo(BaseModel):
    """Database information."""
    type: Optional[str] = None
    version: Optional[str] = None
    orm: Optional[str] = None
    orm_version: Optional[str] = None

class ServerFramework(FrameworkInfo):
    """Server-side framework information."""
    database: DatabaseInfo = Field(default_factory=DatabaseInfo)

class Frameworks(BaseModel):
    """Project frameworks information."""
    web: FrameworkInfo = Field(default_factory=FrameworkInfo)
    server: ServerFramework = Field(default_factory=ServerFramework)

class FileInfo(BaseModel):
    """File information."""
    path: str
    size: int
    lines: int
    type: str
    last_modified: str

class DirectoryInfo(BaseModel):
    """Directory information."""
    path: str
    files: List[FileInfo] = Field(default_factory=list)
    subdirs: List[str] = Field(default_factory=list)

class ProjectStructure(BaseModel):
    """Project structure information."""
    root: str
    directories: List[DirectoryInfo] = Field(default_factory=list)
    special_files: dict = Field(default_factory=dict)
    file_types: dict = Field(default_factory=dict)

class CodeMetrics(BaseModel):
    """Code quality metrics."""
    lines_of_code: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    functions_count: int = 0
    classes_count: int = 0
    complexity: float = 0.0
    maintainability: float = 0.0

class IssueInfo(BaseModel):
    """Issue information."""
    severity: str
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None

class SuggestionInfo(BaseModel):
    """Improvement suggestion."""
    category: str
    suggestion: str
    priority: str = 'medium'
    file: Optional[str] = None

class TestInfo(BaseModel):
    """Test information."""
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    coverage: float = 0.0
    test_files: List[str] = Field(default_factory=list)

class TestCoverage(BaseModel):
    """Test coverage details."""
    line_coverage: float = 0.0
    branch_coverage: float = 0.0
    function_coverage: float = 0.0
    uncovered_lines: List[str] = Field(default_factory=list)

class AnalysisResults(BaseModel):
    """Complete analysis results."""
    project_info: ProjectInfo
    structure: ProjectStructure
    frameworks: Frameworks
    metrics: CodeMetrics
    test_info: TestInfo = Field(default_factory=TestInfo)
    test_coverage: TestCoverage = Field(default_factory=TestCoverage)
    issues: List[IssueInfo] = Field(default_factory=list)
    suggestions: List[SuggestionInfo] = Field(default_factory=list) 