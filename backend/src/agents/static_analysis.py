import re
from typing import Any, Dict, List
from src.agents.base import BaseAgent
from src.schemas import ReviewComment


class StaticAnalysisAgent(BaseAgent):
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
                        issues = self.check_static_issues(code_line, file_path, line_num)
                        comments.extend(issues)
                        line_num += 1
                    elif not line.startswith("-"):
                        line_num += 1

        return comments

    def check_static_issues(
        self, code_line: str, file_path: str, line_num: int
    ) -> List[ReviewComment]:
        comments = []

        if self._check_unused_variable(code_line):
            var_name = self._extract_variable_name(code_line)
            if var_name:
                comments.append(
                    self.create_comment(
                        file_path=file_path,
                        line_number=line_num,
                        severity="info",
                        category="code-quality",
                        message=f"Variable '{var_name}' is assigned but may not be used",
                        suggestion="Consider removing unused variables or prefixing with '_' if intentional",
                    )
                )

        return comments

    def _check_unused_variable(self, code_line: str) -> bool:
        pattern = r"^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*.+$"
        return bool(re.match(pattern, code_line))

    def _extract_variable_name(self, code_line: str) -> str | None:
        match = re.match(r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=", code_line)
        return match.group(1) if match else None
