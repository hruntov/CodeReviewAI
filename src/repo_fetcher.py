import os
from collections import namedtuple

from fastapi import HTTPException
from github import Auth, Github, GithubException, RateLimitExceededException
from pydantic import HttpUrl

from src.logger import log_error, log_info, log_warning

MAX_CONTENT_SIZE = 1024 * 1024
GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN")
FileInfo = namedtuple("FileInfo", ["name", "path", "content"])


class GitHubRepositoryFetcher:
    """
    Class responsible for fetching the contents of a GitHub repository.
    Uses the GitHub API to retrieve file contents from a repository.

    Attributes:
        github (Github): Instance of the GitHub API client.

    """
    def __init__(self, token: str = GITHUB_API_TOKEN):
        """
        Initializes the GitHubRepositoryFetcher with the provided GitHub token.

        Args:
            token (str): GitHub API token for authentication.

        """
        self.github = Github(auth=Auth.Token(token))

    async def fetch_repo_contents(self, repo_url: HttpUrl) -> list:
        """
        Fetches all file contents from a GitHub repository URL.

        Args:
            repo_url (HttpUrl): The GitHub repository URL.

        Returns:
            list[FileInfo]: A list of named tuples containing file information.

        """
        repo_name = self._extract_repo_name(repo_url)
        repo = self._get_repository(repo_name)
        files = self._get_repo_files(repo)

        all_files = self._process_files(repo, files)
        log_info(f"Fetched {len(all_files)} files from repository {repo_name}")
        return all_files

    def _extract_repo_name(self, repo_url: HttpUrl) -> str:
        """
        Extracts the repository name from the GitHub URL.

        Args:
            repo_url (HttpUrl): The GitHub repository URL.

        Returns:
            str: The repository name.

        """
        repo_url_str = str(repo_url)
        return repo_url_str.split("github.com/")[1]

    def _get_repository(self, repo_name: str):
        """
        Gets the repository from GitHub.

        Args:
            repo_name (str): The name of the repository.

        Returns:
            Repository: The GitHub repository object.

        """
        try:
            return self.github.get_repo(repo_name)
        except RateLimitExceededException:
            log_warning("GitHub API rate limit exceeded.")
            raise HTTPException(status_code=429, detail="GitHub API rate limit exceeded.")
        except GithubException as e:
            if e.status == 404:
                log_error(f"Repository not found: {str(e)}")
                raise HTTPException(status_code=404, detail=f"Repository not found: {str(e)}")
            log_error(f"Error fetching repository: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching repository: {str(e)}")
        except Exception as e:
            log_error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    def _get_repo_files(self, repo) -> list:
        """
        Retrieves the contents (files) of the repository.

        Args:
            repo (Repository): The GitHub repository object.

        Returns:
            list: A list of file objects in the repository.

        """
        try:
            return repo.get_contents("")
        except GithubException as e:
            log_error(f"Error fetching repository contents: {str(e)}")
            raise HTTPException(status_code=500,
                                detail=f"Error fetching repository contents: {str(e)}")
        except Exception as e:
            log_error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    def _process_files(self, repo, files: list) -> list[FileInfo]:
        all_files = []
        while files:
            file_content = files.pop(0)
            if file_content.type == "dir":
                files.extend(repo.get_contents(file_content.path))
            else:
                content = self._get_file_content(file_content)
                file_info = FileInfo(
                    name=file_content.name,
                    path=file_content.path,
                    content=content
                )
                all_files.append(file_info)
        return all_files

    def _get_file_content(self, file_content) -> str:
        """
        Retrieves the content of a file. If the file is large, it saves it to disk.

        Args:
            file_content (ContentFile): The file object from GitHub.

        Returns:
            str: The content of the file, either in raw format or a message indicating the file was
                 saved.

        """
        if file_content.size > MAX_CONTENT_SIZE:
            return self._save_large_file(file_content)
        else:
            return file_content.decoded_content.decode("utf-8")

    def _save_large_file(self, file_content) -> str:
        """
        Saves a large file to disk if its size exceeds MAX_CONTENT_SIZE.

        Args:
            file_content (ContentFile): The file object from GitHub.

        Returns:
            str: A message indicating the file has been saved.

        """
        try:
            file_path = os.path.join("/tmp", file_content.path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(file_content.decoded_content)
            return f"File content saved to {file_path}"
        except Exception as e:
            log_error(f"Error saving file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error saving large file: {str(e)}")
