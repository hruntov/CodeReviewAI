import asyncio

import httpx


async def test_review_code():
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                "http://127.0.0.1:8000/review",
                json={
                    "assignment_description": "Check security of code",
                    "github_repo_url": "https://github.com/hruntov/test_repo_for_ai_analyzer",
                    "candidate_level": "Junior"
                }
            )
            if response.status_code == 200:
                response_json = response.json()
                print("Response JSON:", response_json)
            else:
                print("Error:", response.status_code, response.text)
        except httpx.ReadTimeout:
            print("The request timed out")

asyncio.run(test_review_code())
