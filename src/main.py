from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl, constr, field_validator

from src.analyzer import CodeAnalyzer
from src.logger import log_error, log_info
from src.repo_fetcher import GitHubRepositoryFetcher

app = FastAPI()


class ReviewRequest(BaseModel):
    """
    Request model for code review.

    Attributes:
        assignment_description (str): Description of the assignment.
                                      Must be between 1 and 1000 characters.
        github_repo_url (HttpUrl): GitHub repository URL.
        candidate_level (Literal['Junior', 'Middle', 'Senior']): The candidate's experience level.

    """
    assignment_description: constr(min_length=1, max_length=1000)
    github_repo_url: HttpUrl
    candidate_level: Literal['Junior', 'Middle', 'Senior']

    @field_validator('assignment_description')
    def validate_assignment_description(cls, value: str) -> str:
        """
        Validates that the assignment description is not empty or just whitespace.

        Args:
            value (str): The assignment description to validate.

        Returns:
            str: The validated assignment description.

        """
        if not str(value).strip():
            raise ValueError('Assignment description cannot be empty or whitespace.')
        return value

    @field_validator('github_repo_url')
    def validate_github_repo_url(cls, value: HttpUrl) -> HttpUrl:
        """
        Validates that the GitHub repository URL starts with 'https://github.com/'.

        Args:
            value (HttpUrl): The GitHub repository URL to validate.

        Returns:
            HttpUrl: The validated GitHub URL.

        """
        if not str(value).startswith("https://github.com/"):
            raise ValueError('GitHub repository URL must start with "https://github.com/".')
        return value


@app.post("/review")
async def review_code(request: ReviewRequest):
    """
    Endpoint to review the code in a GitHub repository.

    Args:
        request (ReviewRequest): The request containing the assignment description, GitHub URL,
                                 and candidate level.

    Returns:
        dict: A dictionary with the code review results.

    """
    try:
        log_info(f"Received review request for repository: {request.github_repo_url}")
        git_hub_fetcher = GitHubRepositoryFetcher()
        repo_files = await git_hub_fetcher.fetch_repo_contents(request.github_repo_url)
        codeAnalyzer = CodeAnalyzer(repo_files, request.assignment_description,
                                    request.candidate_level)
        review = await codeAnalyzer.start()
        log_info("Review completed successfully.")
        return {"review": review}
    except HTTPException as http_exc:
        log_error(f"HTTPException: {http_exc.detail}")
        raise http_exc
    except ValueError as val_exc:
        log_error(f"ValueError: {str(val_exc)}")
        raise HTTPException(status_code=400,
                            detail=f"Invalid input: {str(val_exc)}.")
    except Exception as e:
        log_error(f"Internal server error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
