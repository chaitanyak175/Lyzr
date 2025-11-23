import json
from datetime import datetime
from sqlmodel import Session, select
from src.celery_app import celery_app
from src.agents.orchestrator import ReviewOrchestrator
from src.github_client import GitHubClient
from src.database import engine
from src.models import ReviewRun, ReviewStatus
import asyncio


@celery_app.task(bind=True)
def review_pr_task(self, run_id: str, owner: str, repo: str, pr_number: int) -> dict:
    return asyncio.run(_async_review_pr(run_id, owner, repo, pr_number))


async def _async_review_pr(run_id: str, owner: str, repo: str, pr_number: int) -> dict:
    with Session(engine) as session:
        statement = select(ReviewRun).where(ReviewRun.run_id == run_id)
        review_run = session.exec(statement).first()

        if not review_run:
            return {"error": "Review run not found"}

        review_run.status = ReviewStatus.PROCESSING
        session.add(review_run)
        session.commit()

        try:
            github_client = GitHubClient()
            diff_content = github_client.get_pr_diff(owner, repo, pr_number)

            orchestrator = ReviewOrchestrator()
            result = await orchestrator.run_review(run_id, diff_content)

            review_run.status = ReviewStatus.COMPLETED
            review_run.result_data = json.dumps(result.model_dump())
            review_run.completed_at = datetime.utcnow()

            session.add(review_run)
            session.commit()

            return {"status": "success", "run_id": run_id}

        except Exception as e:
            review_run.status = ReviewStatus.FAILED
            review_run.error_message = str(e)
            review_run.completed_at = datetime.utcnow()

            session.add(review_run)
            session.commit()

            return {"status": "failed", "error": str(e)}


@celery_app.task(bind=True)
def review_diff_task(self, run_id: str, diff_content: str) -> dict:
    return asyncio.run(_async_review_diff(run_id, diff_content))


async def _async_review_diff(run_id: str, diff_content: str) -> dict:
    with Session(engine) as session:
        statement = select(ReviewRun).where(ReviewRun.run_id == run_id)
        review_run = session.exec(statement).first()

        if not review_run:
            return {"error": "Review run not found"}

        review_run.status = ReviewStatus.PROCESSING
        session.add(review_run)
        session.commit()

        try:
            orchestrator = ReviewOrchestrator()
            result = await orchestrator.run_review(run_id, diff_content)

            review_run.status = ReviewStatus.COMPLETED
            review_run.result_data = json.dumps(result.model_dump())
            review_run.completed_at = datetime.utcnow()

            session.add(review_run)
            session.commit()

            return {"status": "success", "run_id": run_id}

        except Exception as e:
            review_run.status = ReviewStatus.FAILED
            review_run.error_message = str(e)
            review_run.completed_at = datetime.utcnow()

            session.add(review_run)
            session.commit()

            return {"status": "failed", "error": str(e)}