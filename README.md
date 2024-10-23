# CodeReviewAI

CodeReviewAI is a FastAPI-based application that reviews code in GitHub repositories. It fetches the repository contents, analyzes the code, and provides a review based on the assignment description and candidate level.

## Getting Started

### Prerequisites

- Docker
- Docker Compose
- Python 3.10+
- Poetry (for dependency management)

### Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/CodeReviewAI.git
    cd CodeReviewAI
    ```

2. Create a `.env` file in the root directory and add your environment variables:

    ```env
    EDEN_API_KEY=your_eden_api_key
    GITHUB_API_TOKEN=your_github_api_token
    ```

### Running the Application

1. Build and start the Docker containers:

    ```sh
    docker-compose up -d --build
    ```

2. Access the running container:

    ```sh
    docker exec -it {container_id} /bin/bash
    ```

### Running Tests

1. Run the unit tests using `pytest`:

    ```sh
    pytest
    ```

2. Run the functional tests:

    ```sh
    python /tests/func_test.py
    ```

## Project Structure

```plaintext
.env
.gitignore
.pytest_cache/
[docker-compose.yml](http://_vscodecontentref_/#%7B%22uri%22%3A%7B%22%24mid%22%3A1%2C%22fsPath%22%3A%22d%3A%5C%5Cprojects%5C%5CAiReviewer%5C%5Cdocker-compose.yml%22%2C%22_sep%22%3A1%2C%22path%22%3A%22%2Fd%3A%2Fprojects%2FAiReviewer%2Fdocker-compose.yml%22%2C%22scheme%22%3A%22file%22%7D%7D)
Dockerfile
logs/
[poetry.lock](http://_vscodecontentref_/#%7B%22uri%22%3A%7B%22%24mid%22%3A1%2C%22fsPath%22%3A%22d%3A%5C%5Cprojects%5C%5CAiReviewer%5C%5Cpoetry.lock%22%2C%22_sep%22%3A1%2C%22path%22%3A%22%2Fd%3A%2Fprojects%2FAiReviewer%2Fpoetry.lock%22%2C%22scheme%22%3A%22file%22%7D%7D)
[pyproject.toml](http://_vscodecontentref_/#%7B%22uri%22%3A%7B%22%24mid%22%3A1%2C%22fsPath%22%3A%22d%3A%5C%5Cprojects%5C%5CAiReviewer%5C%5Cpyproject.toml%22%2C%22_sep%22%3A1%2C%22path%22%3A%22%2Fd%3A%2Fprojects%2FAiReviewer%2Fpyproject.toml%22%2C%22scheme%22%3A%22file%22%7D%7D)
[pytest.ini](http://_vscodecontentref_/#%7B%22uri%22%3A%7B%22%24mid%22%3A1%2C%22fsPath%22%3A%22d%3A%5C%5Cprojects%5C%5CAiReviewer%5C%5Cpytest.ini%22%2C%22_sep%22%3A1%2C%22path%22%3A%22%2Fd%3A%2Fprojects%2FAiReviewer%2Fpytest.ini%22%2C%22scheme%22%3A%22file%22%7D%7D)
[run_fastapi.sh](http://_vscodecontentref_/#%7B%22uri%22%3A%7B%22%24mid%22%3A1%2C%22fsPath%22%3A%22d%3A%5C%5Cprojects%5C%5CAiReviewer%5C%5Crun_fastapi.sh%22%2C%22_sep%22%3A1%2C%22path%22%3A%22%2Fd%3A%2Fprojects%2FAiReviewer%2Frun_fastapi.sh%22%2C%22scheme%22%3A%22file%22%7D%7D)
src/
tests/
