from pydantic import BaseModel, HttpUrl, constr, field_validator


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
