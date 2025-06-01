docs:
    uv run mkdocs serve

lint:
    @echo "Running Ruff linter"
    uv run ruff check .


format:
    @echo "Formatting code with Ruff"
    uv run ruff format