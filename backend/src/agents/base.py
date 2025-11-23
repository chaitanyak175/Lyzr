from abc import ABC, abstractmethod
from typing import Any, Dict, List
from src.schemas import ReviewComment


class BaseAgent(ABC):
    def __init__(self) -> None:
        self.name = self.__class__.__name__

    @abstractmethod
    async def analyze(self, context: Dict[str, Any]) -> List[ReviewComment]:
        pass

    def create_comment(
        self,
        file_path: str,
        line_number: int | None,
        severity: str,
        category: str,
        message: str,
        suggestion: str | None = None,
    ) -> ReviewComment:
        return ReviewComment(
            file_path=file_path,
            line_number=line_number,
            severity=severity,
            category=category,
            message=message,
            suggestion=suggestion,
        )
