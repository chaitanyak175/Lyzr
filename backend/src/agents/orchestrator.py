import time
from typing import Any, Dict, List
from src.agents.diff_parser import DiffParserAgent
from src.agents.ast_agent import ASTAgent
from src.agents.static_analysis import StaticAnalysisAgent
from src.agents.security import SecurityAgent
from src.agents.performance import PerformanceAgent
from src.agents.readability import ReadabilityAgent
from src.agents.style import StyleAgent
from src.agents.test_coverage import TestCoverageAgent
from src.agents.summarizer import SummarizerAgent
from src.agents.comment_formatter import CommentFormatterAgent
from src.schemas import ReviewComment, ReviewResult, ReviewSummary


class ReviewOrchestrator:
    def __init__(self) -> None:
        self.agents = [
            DiffParserAgent(),
            ASTAgent(),
            StaticAnalysisAgent(),
            SecurityAgent(),
            PerformanceAgent(),
            ReadabilityAgent(),
            StyleAgent(),
            TestCoverageAgent(),
        ]
        self.summarizer = SummarizerAgent()
        self.formatter = CommentFormatterAgent()

    async def run_review(self, run_id: str, diff_content: str) -> ReviewResult:
        start_time = time.time()
        
        context: Dict[str, Any] = {
            "diff_content": diff_content,
            "run_id": run_id,
            "all_comments": [],
        }
        
        for agent in self.agents:
            agent_comments = await agent.analyze(context)
            context["all_comments"].extend(agent_comments)
        
        await self.summarizer.analyze(context)
        await self.formatter.analyze(context)
        
        summary = context.get("summary")
        formatted_comments = context.get("formatted_comments", [])
        
        processing_time = time.time() - start_time
        
        return ReviewResult(
            run_id=run_id,
            status="completed",
            summary=summary,
            comments=formatted_comments,
            processing_time_seconds=round(processing_time, 2),
        )
