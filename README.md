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
    LOG_FILE=path/to/your/logfile
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
[docker-compose.yml]
Dockerfile
logs/
[poetry.lock]
[pyproject.toml]
[pytest.ini]
[run_fastapi.sh]
src/
tests/
