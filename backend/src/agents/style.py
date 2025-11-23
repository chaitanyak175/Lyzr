import re
from typing import Any, Dict, List
from src.agents.base import BaseAgent
from src.schemas import ReviewComment


class StyleAgent(BaseAgent):
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
                        issues = self.check_style_issues(code_line, file_path, line_num)
                        comments.extend(issues)
                        line_num += 1
                    elif not line.startswith("-"):
                        line_num += 1

        return comments

    def check_style_issues(
        self, code_line: str, file_path: str, line_num: int
    ) -> List[ReviewComment]:
        comments = []

        if self._check_trailing_whitespace(code_line):
            comments.append(
                self.create_comment(
                    file_path=file_path,
                    line_number=line_num,
                    severity="style",
                    category="style",
                    message="Trailing whitespace detected",
                    suggestion="Remove trailing whitespace",
                )
            )

        if self._check_inconsistent_quotes(code_line):
            comments.append(
                self.create_comment(
                    file_path=file_path,
                    line_number=line_num,
                    severity="style",
                    category="style",
                    message="Inconsistent quote usage detected",
                    suggestion="Use consistent quotes throughout the codebase (prefer single quotes)",
                )
            )

        if self._check_naming_convention(code_line):
            comments.append(
                self.create_comment(
                    file_path=file_path,
                    line_number=line_num,
                    severity="style",
                    category="style",
                    message="Variable name doesn't follow snake_case convention",
                    suggestion="Use snake_case for variable and function names",
                )
            )

        return comments

    def _check_trailing_whitespace(self, code_line: str) -> bool:
        return code_line.rstrip() != code_line

    def _check_inconsistent_quotes(self, code_line: str) -> bool:
        double_quotes = code_line.count('"')
        single_quotes = code_line.count("'")
        return double_quotes > 0 and single_quotes > 0

    def _check_naming_convention(self, code_line: str) -> bool:
        match = re.match(r"^\s*(def|class)\s+([a-zA-Z_][a-zA-Z0-9_]*)", code_line)
        if match:
            name = match.group(2)
            if match.group(1) == "def":
                return bool(re.search(r"[A-Z]", name))
            elif match.group(1) == "class":
                return not name[0].isupper()
        return False
