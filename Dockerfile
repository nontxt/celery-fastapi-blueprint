# Use official Python image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy only the dependency files first to leverage Docker cache
COPY pyproject.toml poetry.lock /app/

# Install Poetry
RUN pip install poetry --no-cache-dir

# Configure Poetry to not create virtual environments (if needed)
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --without dev --no-root

# Copy the rest of the project files
COPY . /app/

# Expose FastAPI port
EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
