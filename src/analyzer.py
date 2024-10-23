import asyncio
import json
import os
import re
import time
from typing import Any, Dict, List

import httpx
import requests
from fastapi import HTTPException

from src.logger import log_error, log_warning


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


    def parse_result(self, result: Dict[str, Any], file_names: List[str]) -> Dict[str, Any]:
        """
        Parses the AI service response and extracts key sections such as rating and conclusion.

        Args:
            result (Dict[str, Any]): The raw result from the AI service.
            file_names (List[str]): List of file names to include in the final report.

        Returns:
            Dict[str, Any]: A dictionary containing the parsed results including downsides/comments,
                            rating, and conclusion.

        """
        openai_data = result.get('openai', {})
        generated_text = openai_data.get('generated_text', 'No suggestion available')

        rating = self.extract_section(generated_text, "Rating")
        conclusion = self.extract_section(generated_text, "Conclusion")

        parsed_result = {
            "Found files": file_names,
            "Downsides/Comments": generated_text,
            "Rating": rating,
            "Conclusion": conclusion
        }

        return parsed_result

    def extract_section(self, text: str, section_name: str) -> str:
        """
        Extracts a specific section (like Rating or Conclusion) from the AI response text using
        regular expressions.

        Args:
            text (str): The AI-generated text to parse.
            section_name (str): The section name to extract (e.g., "Rating", "Conclusion").

        Returns:
            str: The extracted section or a default message if not found.

        """
        # TODO: Optimize the regular expesion
        pattern = re.compile(rf"(?:###?\s*|\*\*|-\s*){section_name}[:*]?\s*(.*?)(?=\n(?:###?|\*\*|-\s*)|\Z)", re.DOTALL)

        match = pattern.search(text)
        if match:
            print("match - ", match)
            return match.group(1).strip()
        return f"No {section_name.lower()} available"


    async def start(self) -> Dict[str, Any]:
        """
        Starts the code analysis by sending requests to the AI service. Retries in case of
        rate-limiting.

        Returns:
            Dict[str, Any]: Parsed result of the AI's response.

        """
        result = None
        for attempt in range(self.retries):
            try:
                result = await self._send_request()
                if result:
                    break
            except HTTPException as e:
                if e.status_code == 429 and attempt < self.retries - 1:
                    log_warning("AI service rate limit exceeded. Retrying...")
                    await asyncio.sleep(self.backoff_factor ** attempt)
                else:
                    raise e
        return result

    async def _send_request(self) -> Dict[str, Any]:
        """
        Sends a request to the AI service and handles its response, including rate-limiting and
        errors.

        Returns:
            Dict[str, Any]: Parsed result of the AI's response.

        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.url_ai, json=self.prompt["payload"],
                                             headers=self.prompt["headers"])
                if response.status_code == 200:
                    print(response.text)
                    result = json.loads(response.text)
                    return self.parse_result(result, self.file_names)
                elif response.status_code == 429:
                    log_warning("AI service rate limit exceeded. Retrying...")
                    time.sleep(self.backoff_factor ** 2)
                    raise HTTPException(status_code=429, detail="AI service rate limit exceeded.")
                else:
                    log_error(f"AI service returned an error: {response.status_code} - "
                              f"{response.text}")
                    raise HTTPException(status_code=response.status_code, detail=response.text)
            except requests.RequestException as e:
                log_error(f"Failed to communicate with the AI service: {str(e)}")
                time.sleep(self.backoff_factor ** 2)
                raise HTTPException(status_code=502,
                                    detail=f"Failed to communicate with the AI service: {str(e)}")
            except json.JSONDecodeError as e:
                log_error(f"Invalid response format from AI service: {str(e)}")
                raise HTTPException(status_code=500,
                                    detail=f"Invalid response format from AI service: {str(e)}")
            except Exception as e:
                log_error(f"Error analyzing code: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error analyzing code: {str(e)}")
