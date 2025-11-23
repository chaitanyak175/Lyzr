from typing import Any, Dict, List
from src.agents.base import BaseAgent
from src.schemas import ReviewComment, ReviewSummary


class SummarizerAgent(BaseAgent):
    async def analyze(self, context: Dict[str, Any]) -> List[ReviewComment]:
        all_comments = context.get("all_comments", [])
        parsed_files = context.get("parsed_files", [])
        
        summary = self.generate_summary(all_comments, parsed_files)
        context["summary"] = summary
        
        return []

    def generate_summary(
        self, comments: List[ReviewComment], parsed_files: List[Dict[str, Any]]
    ) -> ReviewSummary:
        total_files = len([f for f in parsed_files if not f.get("is_binary")])
        
        critical_count = sum(1 for c in comments if c.severity == "critical")
        warning_count = sum(1 for c in comments if c.severity == "warning")
        info_count = sum(1 for c in comments if c.severity == "info")
        style_count = sum(1 for c in comments if c.severity == "style")
        
        total_issues = len(comments)
        
        assessment = self._determine_overall_assessment(
            critical_count, warning_count, info_count, style_count
        )
        
        return ReviewSummary(
            total_files_reviewed=total_files,
            total_issues_found=total_issues,
            critical_issues=critical_count,
            warnings=warning_count,
            info_items=info_count,
            style_issues=style_count,
            overall_assessment=assessment,
        )

    def _determine_overall_assessment(
        self, critical: int, warnings: int, info: int, style: int
    ) -> str:
        if critical > 0:
            return f"CRITICAL: {critical} critical security or code quality issues must be addressed immediately"
        elif warnings >= 5:
            return f"NEEDS WORK: {warnings} warnings found that should be reviewed and addressed"
        elif warnings > 0:
            return f"GOOD: Only {warnings} minor warnings found, consider addressing them"
        elif info > 0 or style > 0:
            return f"EXCELLENT: No critical issues, only {info + style} suggestions for improvement"
        else:
            return "PERFECT: No issues found, code looks great!"
