import re
from typing import Any, Dict, List
from src.agents.base import BaseAgent
from src.schemas import ReviewComment


class PerformanceAgent(BaseAgent):
    async def analyze(self, context: Dict[str, Any]) -> List[ReviewComment]:
        comments = []
        parsed_files = context.get("parsed_files", [])

        for file_data in parsed_files:
            if file_data.get("is_binary"):
                continue

            file_path = file_data["path"]

            for hunk in file_data.get("hunks", []):
                line_num = hunk["new_start"]
                for line in hunk["lines"]:
                    if line.startswith("+") and not line.startswith("+++"):
                        code_line = line[1:]
                        issues = self.check_performance_issues(code_line, file_path, line_num)
                        comments.extend(issues)
                        line_num += 1
                    elif not line.startswith("-"):
                        line_num += 1

        return comments

    def check_performance_issues(
        self, code_line: str, file_path: str, line_num: int
    ) -> List[ReviewComment]:
        comments = []

        if self._check_nested_loop(code_line):
            comments.append(
                self.create_comment(
                    file_path=file_path,
                    line_number=line_num,
                    severity="warning",
                    category="performance",
                    message="Nested loop detected - potential O(n²) complexity",
                    suggestion="Consider using list comprehensions, map/filter, or more efficient algorithms",
                )
            )

        if self._check_repeated_computation(code_line):
            comments.append(
                self.create_comment(
                    file_path=file_path,
                    line_number=line_num,
                    severity="warning",
                    category="performance",
                    message="Repeated function call in loop condition detected",
                    suggestion="Cache the result in a variable before the loop",
                )
            )

        if self._check_string_concatenation_in_loop(code_line):
            comments.append(
                self.create_comment(
                    file_path=file_path,
                    line_number=line_num,
                    severity="info",
                    category="performance",
                    message="String concatenation in loop may be inefficient",
                    suggestion="Use str.join() or list accumulation for better performance",
                )
            )

        return comments

    def _check_nested_loop(self, code_line: str) -> bool:
        return bool(re.match(r"^\s+for\s+.+\s+in\s+", code_line))

    def _check_repeated_computation(self, code_line: str) -> bool:
        return bool(re.search(r"while.*len\(", code_line))

    def _check_string_concatenation_in_loop(self, code_line: str) -> bool:
        return bool(re.search(r"\+=\s*['\"]", code_line))
