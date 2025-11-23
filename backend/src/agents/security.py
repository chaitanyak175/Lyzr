import re
from typing import Any, Dict, List
from src.agents.base import BaseAgent
from src.schemas import ReviewComment


class SecurityAgent(BaseAgent):
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
                        issues = self.check_security_issues(code_line, file_path, line_num)
                        comments.extend(issues)
                        line_num += 1
                    elif not line.startswith("-"):
                        line_num += 1

        return comments

    def check_security_issues(
        self, code_line: str, file_path: str, line_num: int
    ) -> List[ReviewComment]:
        comments = []

        if self._check_sql_injection(code_line):
            comments.append(
                self.create_comment(
                    file_path=file_path,
                    line_number=line_num,
                    severity="critical",
                    category="security",
                    message="Potential SQL injection vulnerability detected",
                    suggestion="Use parameterized queries or ORM methods instead of string formatting",
                )
            )

        if self._check_hardcoded_secrets(code_line):
            comments.append(
                self.create_comment(
                    file_path=file_path,
                    line_number=line_num,
                    severity="critical",
                    category="security",
                    message="Possible hardcoded secret or API key detected",
                    suggestion="Store secrets in environment variables or a secure vault",
                )
            )

        if self._check_eval_usage(code_line):
            comments.append(
                self.create_comment(
                    file_path=file_path,
                    line_number=line_num,
                    severity="critical",
                    category="security",
                    message="Use of eval() or exec() detected - potential code injection risk",
                    suggestion="Avoid eval/exec or carefully validate and sanitize input",
                )
            )

        return comments

    def _check_sql_injection(self, code_line: str) -> bool:
        sql_patterns = [
            r"execute\s*\([^)]*['\"].*%s.*['\"].*%",
            r"execute\s*\([^)]*['\"].*\+.*['\"]",
            r"execute\s*\([^)]*f['\"].*\{.*\}",
            r"cursor\.execute\([^)]*\.format\(",
        ]
        return any(re.search(pattern, code_line, re.IGNORECASE) for pattern in sql_patterns)

    def _check_hardcoded_secrets(self, code_line: str) -> bool:
        secret_patterns = [
            r"(api[_-]?key|apikey|secret|password|token|auth)\s*=\s*['\"][a-zA-Z0-9]{16,}['\"]",
            r"(aws|github|slack)[_-]?(token|key|secret)\s*=\s*['\"]",
        ]
        return any(
            re.search(pattern, code_line, re.IGNORECASE) for pattern in secret_patterns
        )

    def _check_eval_usage(self, code_line: str) -> bool:
        return bool(re.search(r"\b(eval|exec)\s*\(", code_line))
