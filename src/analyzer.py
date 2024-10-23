import os
from typing import Any, List


class CodeAnalyzer:
    """
    CodeAnalyzer class analyzes the files from a GitHub repository using the EdenAI service.
    It sends the code, assignment description, and candidate level to the AI service to evaluate the
    quality of the code.

    Attributes:
        EDEN_API_KEY (str): API key for EdenAI service.
        url_ai (str): URL of the EdenAI service.
        headers (Dict[str, str]): Headers for authentication with the EdenAI service.
        file_names (List[str]): List of file names to be analyzed.
        prompt (Dict[str, Any]): Payload and headers for making requests to the AI service.
        retries (int): Number of retries for handling rate-limiting.
        backoff_factor (int): Backoff factor for retrying failed requests.

    """
    def __init__(self, files: List[Any], assignment_description: str, candidate_level: str):
        """
        Initializes the CodeAnalyzer with the given files, assignment description, and candidate
        level.

        Args:
            files (List[Any]): List of files from the GitHub repository.
            assignment_description (str): Description of the coding assignment.
            candidate_level (str): The experience level of the candidate (Junior, Middle, Senior).

        """
        self.EDEN_API_KEY = os.getenv("EDEN_API_KEY")
        self.url_ai = "https://api.edenai.run/v2/text/chat"
        self.headers = {"Authorization": f"Bearer {self.EDEN_API_KEY}"}
        self.file_names = [file.name for file in files]
        self.prompt = self.make_prompt(files, assignment_description, candidate_level)
        self.retries = 3
        self.backoff_factor = 2

    def make_prompt(self, files: List[Any], assignment_description: str,
                    candidate_level: str) -> Dict[str, Any]:
        """
        Constructs the prompt to be sent to the AI service based on the files, assignment
        description, and candidate level.

        Args:
            files (List[Any]): List of files from the GitHub repository.
            assignment_description (str): Description of the coding assignment.
            candidate_level (str): The experience level of the candidate (Junior, Middle, Senior).

        Returns:
            Dict[str, Any]: Dictionary containing the headers and payload for the AI request.

        """
        prompt = f"""
        You are analyzing code for a coding assignment. The level is {candidate_level}.
        The assignment description is: {assignment_description}

        These are the files:
        {files}

        Make sure to include the following separate sections in your response:
        - Rating: Provide a rating for the code.
        - Conclusion: Summarize your findings and provide a conclusion.
        """
        payload = {
            "providers": "openai",
            "text": f"{prompt}{assignment_description} ",
            "chatbot_global_action": "Act as an assistant",
            "previous_history": [],
            "temperature": 0.25,
            "max_tokens": 3000,
            "fallback_providers": ""
        }
        return {"headers": self.headers, "payload": payload}