import re
from typing import Any, Dict, List
from src.agents.base import BaseAgent
from src.schemas import ReviewComment


class ReadabilityAgent(BaseAgent):
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
                        issues = self.check_readability_issues(code_line, file_path, line_num)
                        comments.extend(issues)
                        line_num += 1
                    elif not line.startswith("-"):
                        line_num += 1

        return comments

    def check_readability_issues(
        self, code_line: str, file_path: str, line_num: int
    ) -> List[ReviewComment]:
        comments = []

        if self._check_long_line(code_line):
            comments.append(
                self.create_comment(
                    file_path=file_path,
                    line_number=line_num,
                    severity="info",
                    category="readability",
                    message=f"Line exceeds recommended length ({len(code_line)} characters)",
                    suggestion="Consider breaking this line into multiple lines for better readability",
                )
            )

        if self._check_complex_expression(code_line):
            comments.append(
                self.create_comment(
                    file_path=file_path,
                    line_number=line_num,
                    severity="info",
                    category="readability",
                    message="Complex nested expression detected",
                    suggestion="Consider breaking into intermediate variables for clarity",
                )
            )

        if self._check_magic_numbers(code_line):
            comments.append(
                self.create_comment(
                    file_path=file_path,
                    line_number=line_num,
                    severity="info",
                    category="readability",
                    message="Magic number detected",
                    suggestion="Consider extracting to a named constant",
                )
            )

        return comments

    def _check_long_line(self, code_line: str) -> bool:
        return len(code_line) > 100

    def _check_complex_expression(self, code_line: str) -> bool:
        open_parens = code_line.count("(")
        return open_parens >= 4

    def _check_magic_numbers(self, code_line: str) -> bool:
        if re.search(r"return\s+\d+\s*$", code_line):
            return False
        return bool(re.search(r"[^0-9]\d{3,}[^0-9]", code_line))
