from dataclasses import dataclass
from enum import Enum
from typing import Optional

class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"

@dataclass
class Document:
    id: int | None = None
    name: str = ""
    content: str = ""
    type: DocumentType = DocumentType.PDF

@dataclass
class Employee:
    id: Optional[int] = None
    email: str = ""
    name: str = ""
    role: str = ""

@dataclass
class AdminSession:
    user_id: int = 0

@dataclass
class OnboardingChecklist:
    role: str
    documents: list[str]
    contacts: list[str]
    events: list[str]
    materials: list[str]