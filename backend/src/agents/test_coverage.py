import re
from typing import Any, Dict, List
from src.agents.base import BaseAgent
from src.schemas import ReviewComment


class TestCoverageAgent(BaseAgent):
    async def analyze(self, context: Dict[str, Any]) -> List[ReviewComment]:
        comments = []
        parsed_files = context.get("parsed_files", [])

        production_files = []
        test_files = []

        for file_data in parsed_files:
            if file_data.get("is_binary"):
                continue

            file_path = file_data["path"]
            if self._is_test_file(file_path):
                test_files.append(file_data)
            else:
                production_files.append(file_data)

        for file_data in production_files:
            file_path = file_data["path"]
            if not file_path.endswith(".py"):
                continue

            functions_added = self._extract_functions_from_diff(file_data)
            if functions_added:
                corresponding_test = self._find_test_file(file_path, test_files)
                if not corresponding_test:
                    comments.append(
                        self.create_comment(
                            file_path=file_path,
                            line_number=None,
                            severity="warning",
                            category="testing",
                            message=f"New functions added but no corresponding test file found",
                            suggestion=f"Consider adding tests in test_{file_path.split('/')[-1]}",
                        )
                    )

        return comments

    def _is_test_file(self, file_path: str) -> bool:
        return "test_" in file_path or "_test.py" in file_path or "/tests/" in file_path

    def _extract_functions_from_diff(self, file_data: Dict[str, Any]) -> List[str]:
        functions = []
        for hunk in file_data.get("hunks", []):
            for line in hunk["lines"]:
                if line.startswith("+") and not line.startswith("+++"):
                    code_line = line[1:]
                    match = re.match(r"^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", code_line)
                    if match:
                        functions.append(match.group(1))
        return functions

    def _find_test_file(
        self, production_file: str, test_files: List[Dict[str, Any]]
    ) -> Dict[str, Any] | None:
        base_name = production_file.split("/")[-1].replace(".py", "")
        test_name = f"test_{base_name}"

        for test_file in test_files:
            if test_name in test_file["path"]:
                return test_file
        return None
