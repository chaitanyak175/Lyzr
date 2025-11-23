from typing import Any, Dict, List
from src.agents.base import BaseAgent
from src.schemas import ReviewComment


class CommentFormatterAgent(BaseAgent):
    async def analyze(self, context: Dict[str, Any]) -> List[ReviewComment]:
        all_comments = context.get("all_comments", [])
        formatted_comments = self.format_comments(all_comments)
        context["formatted_comments"] = formatted_comments
        return []

    def format_comments(self, comments: List[ReviewComment]) -> List[ReviewComment]:
        sorted_comments = sorted(
            comments,
            key=lambda c: (
                self._severity_priority(c.severity),
                c.file_path,
                c.line_number or 0,
            ),
        )
        
        deduped_comments = self._deduplicate_comments(sorted_comments)
        
        return deduped_comments

    def _severity_priority(self, severity: str) -> int:
        priority_map = {"critical": 0, "warning": 1, "info": 2, "style": 3}
        return priority_map.get(severity, 4)

    def _deduplicate_comments(
        self, comments: List[ReviewComment]
    ) -> List[ReviewComment]:
        seen = set()
        unique_comments = []
        
        for comment in comments:
            key = (
                comment.file_path,
                comment.line_number,
                comment.category,
                comment.message,
            )
            if key not in seen:
                seen.add(key)
                unique_comments.append(comment)
        
        return unique_comments
