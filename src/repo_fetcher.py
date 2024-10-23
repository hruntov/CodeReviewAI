from github import Auth, Github


GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN")


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