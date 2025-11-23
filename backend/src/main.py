import json
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from src.database import create_db_and_tables, get_session
from src.models import ReviewRun, ReviewStatus
from src.schemas import PRReviewRequest, DiffReviewRequest, ReviewResult
from src.tasks import review_pr_task, review_diff_task


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="PR Review Agent API",
    description="Automated GitHub Pull Request Review Agent",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "service": "PR Review Agent",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "review_pr": "POST /review/pr",
            "review_diff": "POST /review/diff",
            "get_review": "GET /review/{run_id}",
        },
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/review/pr", response_model=dict)
async def review_pull_request(
    request: PRReviewRequest, session: Session = Depends(get_session)
):
    run_id = str(uuid.uuid4())

    review_run = ReviewRun(
        run_id=run_id,
        repo_owner=request.repo_owner,
        repo_name=request.repo_name,
        pr_number=request.pr_number,
        status=ReviewStatus.PENDING,
    )

    session.add(review_run)
    session.commit()
    session.refresh(review_run)

    review_pr_task.delay(run_id, request.repo_owner, request.repo_name, request.pr_number)

    return {
        "run_id": run_id,
        "status": "pending",
        "message": "Review started. Use GET /review/{run_id} to check progress.",
    }


@app.post("/review/diff", response_model=dict)
async def review_diff(request: DiffReviewRequest, session: Session = Depends(get_session)):
    run_id = str(uuid.uuid4())

    review_run = ReviewRun(
        run_id=run_id,
        repo_owner="direct",
        repo_name="diff-review",
        status=ReviewStatus.PENDING,
    )

    session.add(review_run)
    session.commit()
    session.refresh(review_run)

    review_diff_task.delay(run_id, request.diff_content)

    return {
        "run_id": run_id,
        "status": "pending",
        "message": "Review started. Use GET /review/{run_id} to check progress.",
    }


@app.get("/review/{run_id}", response_model=ReviewResult)
async def get_review_status(run_id: str, session: Session = Depends(get_session)):
    statement = select(ReviewRun).where(ReviewRun.run_id == run_id)
    review_run = session.exec(statement).first()

    if not review_run:
        raise HTTPException(status_code=404, detail="Review run not found")

    if review_run.status == ReviewStatus.COMPLETED and review_run.result_data:
        result_dict = json.loads(review_run.result_data)
        return ReviewResult(**result_dict)

    elif review_run.status == ReviewStatus.FAILED:
        raise HTTPException(
            status_code=500,
            detail=f"Review failed: {review_run.error_message or 'Unknown error'}",
        )

    elif review_run.status == ReviewStatus.PROCESSING:
        return ReviewResult(run_id=run_id, status="processing", comments=[])

    else:
        return ReviewResult(run_id=run_id, status="pending", comments=[])
