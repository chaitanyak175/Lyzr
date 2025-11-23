import ast
from typing import Any, Dict, List
from src.agents.base import BaseAgent
from src.schemas import ReviewComment


class ASTAgent(BaseAgent):
    async def analyze(self, context: Dict[str, Any]) -> List[ReviewComment]:
        comments = []
        parsed_files = context.get("parsed_files", [])

        for file_data in parsed_files:
            if file_data.get("is_binary"):
                continue

            file_path = file_data["path"]
            if not file_path.endswith(".py"):
                continue

            for hunk in file_data.get("hunks", []):
                line_num = hunk["new_start"]
                for line in hunk["lines"]:
                    if line.startswith("+") and not line.startswith("+++"):
                        code_line = line[1:]
                        issues = self.check_line_ast(code_line, file_path, line_num)
                        comments.extend(issues)
                        line_num += 1
                    elif not line.startswith("-"):
                        line_num += 1

        return comments

    def check_line_ast(
        self, code_line: str, file_path: str, line_num: int
    ) -> List[ReviewComment]:
        comments = []

        if re_import := self._check_shadowing(code_line):
            comments.append(
                self.create_comment(
                    file_path=file_path,
                    line_number=line_num,
                    severity="warning",
                    category="naming",
                    message=f"Variable name '{re_import}' shadows a built-in or common library name",
                    suggestion=f"Consider renaming '{re_import}' to avoid shadowing",
                )
            )

        return comments

    def _check_shadowing(self, code_line: str) -> str | None:
        builtins_and_common = {
            "id",
            "type",
            "list",
            "dict",
            "set",
            "str",
            "int",
            "float",
            "input",
            "open",
            "file",
            "object",
            "bytes",
            "filter",
            "map",
        }

        try:
            tree = ast.parse(code_line)
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    if node.id in builtins_and_common:
                        return node.id
        except SyntaxError:
            pass

        return None
