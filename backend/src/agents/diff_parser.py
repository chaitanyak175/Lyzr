import re
from typing import Any, Dict, List
from src.agents.base import BaseAgent
from src.schemas import ReviewComment


class DiffParserAgent(BaseAgent):
    async def analyze(self, context: Dict[str, Any]) -> List[ReviewComment]:
        diff_content = context.get("diff_content", "")
        parsed_files = self.parse_diff(diff_content)
        context["parsed_files"] = parsed_files
        return []

    def parse_diff(self, diff_content: str) -> List[Dict[str, Any]]:
        files = []
        current_file = None
        current_hunk = None

        lines = diff_content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]

            if line.startswith("diff --git"):
                if current_file:
                    files.append(current_file)
                
                match = re.search(r"b/(.+)$", line)
                file_path = match.group(1) if match else "unknown"
                
                current_file = {
                    "path": file_path,
                    "hunks": [],
                    "is_binary": False,
                    "old_path": None,
                    "new_path": file_path,
                }
                current_hunk = None

            elif line.startswith("Binary files"):
                if current_file:
                    current_file["is_binary"] = True

            elif line.startswith("--- "):
                if current_file:
                    match = re.search(r"a/(.+)$", line)
                    current_file["old_path"] = match.group(1) if match else None

            elif line.startswith("+++ "):
                if current_file:
                    match = re.search(r"b/(.+)$", line)
                    current_file["new_path"] = match.group(1) if match else None

            elif line.startswith("@@"):
                match = re.search(r"@@ -(\d+),?\d* \+(\d+),?\d* @@", line)
                if match and current_file:
                    current_hunk = {
                        "old_start": int(match.group(1)),
                        "new_start": int(match.group(2)),
                        "lines": [],
                    }
                    current_file["hunks"].append(current_hunk)

            elif current_hunk is not None and (
                line.startswith("+") or line.startswith("-") or line.startswith(" ")
            ):
                current_hunk["lines"].append(line)

            i += 1

        if current_file:
            files.append(current_file)

        return files
