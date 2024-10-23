from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.repo_fetcher import GitHubRepositoryFetcher


@pytest.fixture
def mock_github_repo(mocker):
    """
    Fixture to mock the GitHub repository fetcher for various test cases.
    """
    mock_repo = Mock()
    mock_file = Mock()
    mock_file.name = "test.py"
    mock_file.path = "test.py"
    mock_file.size = 50
    mock_file.decoded_content = b"print('Hello')"
    mock_repo.get_contents = Mock(return_value=[mock_file])

    mocker.patch.object(GitHubRepositoryFetcher, '_get_repository', return_value=mock_repo)
    return mock_repo


@pytest.fixture
def mock_invalid_github_repo(mocker):
    """
    Fixture to mock the GitHub repository fetcher for non-existent repository case.
    """
    mocker.patch.object(GitHubRepositoryFetcher, '_get_repository', side_effect=HTTPException(status_code=404, detail="Repository not found"))


@pytest.mark.asyncio
async def test_review_code_valid_input(mock_github_repo):
    """
    Test with valid input, where the GitHub repository exists and returns files.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/review", json={
            "assignment_description": "Check security of code",
            "github_repo_url": "https://github.com/example/repo",
            "candidate_level": "Junior"
        })

    assert response.status_code == 200
    assert "review" in response.json()


@pytest.mark.asyncio
async def test_review_code_empty_url():
    """
    Test with invalid input: Empty GitHub URL.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/review", json={
            "assignment_description": "Check security of code",
            "github_repo_url": "",
            "candidate_level": "Junior"
        })

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_review_code_with_empty_assignment():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/review", json={
            "assignment_description": "",
            "github_repo_url": "https://invalid-url",
            "candidate_level": "Junior"
        })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_review_code_repo_not_found(mock_invalid_github_repo):
    """
    Test with a non-existent GitHub repository URL.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/review", json={
            "assignment_description": "Check security of code",
            "github_repo_url": "https://github.com/nonexistent/repo",
            "candidate_level": "Junior"
        })

    assert response.status_code == 404
    assert response.json()["detail"] == "Repository not found"


@pytest.mark.asyncio
async def test_review_code_repo_not_found(mocker):
    # Mock the _get_repository method to raise a 404 error
    mocker.patch.object(GitHubRepositoryFetcher, '_get_repository', side_effect=HTTPException(status_code=404, detail="Repository not found"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/review", json={
            "assignment_description": "Check security of code",
            "github_repo_url": "https://github.com/nonexistent/repo",
            "candidate_level": "Junior"
        })

    assert response.status_code == 404
    assert response.json()["detail"] == "Repository not found"


@pytest.mark.asyncio
async def test_review_code_value_error(mocker):
    """
    Test when a ValueError is raised for invalid input.
    """
    # Mock GitHubRepositoryFetcher to raise ValueError
    mocker.patch.object(GitHubRepositoryFetcher, 'fetch_repo_contents', side_effect=ValueError("Invalid input"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/review", json={
            "assignment_description": "Check security of code",
            "github_repo_url": "https://github.com/example/repo",
            "candidate_level": "Junior"
        })

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid input: Invalid input."


@pytest.mark.asyncio
async def test_review_code_internal_server_error(mocker):
    """
    Test for an internal server error during the process.
    """
    # Mock GitHubRepositoryFetcher to raise a generic Exception (simulating internal server error)
    mocker.patch.object(GitHubRepositoryFetcher, 'fetch_repo_contents', side_effect=Exception("Some unexpected error"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/review", json={
            "assignment_description": "Check security of code",
            "github_repo_url": "https://github.com/example/repo",
            "candidate_level": "Junior"
        })

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error: Some unexpected error"
