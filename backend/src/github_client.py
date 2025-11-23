from github import Github, Auth
from src.config import settings


class GitHubClient:
    def __init__(self) -> None:
        auth = Auth.Token(settings.github_token)
        self.client = Github(auth=auth)

    def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        repository = self.client.get_repo(f"{owner}/{repo}")
        pull_request = repository.get_pull(pr_number)
        
        files = pull_request.get_files()
        diff_parts = []
        
        for file in files:
            if file.patch:
                diff_parts.append(f"diff --git a/{file.filename} b/{file.filename}")
                diff_parts.append(f"--- a/{file.filename}")
                diff_parts.append(f"+++ b/{file.filename}")
                diff_parts.append(file.patch)
            elif file.status == "removed":
                diff_parts.append(f"diff --git a/{file.filename} b/{file.filename}")
                diff_parts.append(f"deleted file")
            elif file.status == "added":
                diff_parts.append(f"diff --git a/{file.filename} b/{file.filename}")
                diff_parts.append(f"new file")
        
        return "\n".join(diff_parts)

    def post_review_comment(
        self, owner: str, repo: str, pr_number: int, comments: list
    ) -> None:
        repository = self.client.get_repo(f"{owner}/{repo}")
        pull_request = repository.get_pull(pr_number)
        
        review_body = self._format_review_body(comments)
        pull_request.create_issue_comment(review_body)

    def _format_review_body(self, comments: list) -> str:
        body_parts = ["## 🤖 Automated Code Review\n"]
        
        if not comments:
            body_parts.append("✅ No issues found!")
            return "\n".join(body_parts)
        
        severity_groups = {"critical": [], "warning": [], "info": [], "style": []}
        
        for comment in comments:
            severity_groups[comment.get("severity", "info")].append(comment)
        
        if severity_groups["critical"]:
            body_parts.append("### 🚨 Critical Issues\n")
            for comment in severity_groups["critical"]:
                body_parts.append(self._format_comment(comment))
        
        if severity_groups["warning"]:
            body_parts.append("### ⚠️ Warnings\n")
            for comment in severity_groups["warning"]:
                body_parts.append(self._format_comment(comment))
        
        if severity_groups["info"]:
            body_parts.append("### 💡 Suggestions\n")
            for comment in severity_groups["info"]:
                body_parts.append(self._format_comment(comment))
        
        if severity_groups["style"]:
            body_parts.append("### 🎨 Style\n")
            for comment in severity_groups["style"]:
                body_parts.append(self._format_comment(comment))
        
        return "\n".join(body_parts)

    def _format_comment(self, comment: dict) -> str:
        parts = [f"**{comment['file_path']}"]
        if comment.get("line_number"):
            parts[0] += f":{comment['line_number']}"
        parts[0] += "**"
        
        parts.append(f"- {comment['message']}")
        
        if comment.get("suggestion"):
            parts.append(f"  - 💡 Suggestion: {comment['suggestion']}")
        
        parts.append("")
        return "\n".join(parts)
