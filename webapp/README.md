# Web App

## Docker Compose

1. Copy `.env` with the required API keys into this directory if you have not already.
2. Build and start the stack: `docker compose up --build`.
3. Backend is served on `http://localhost:8000`, frontend on `http://localhost:3000`.
4. To stop the services, press `Ctrl+C` or run `docker compose down`.

During local development both services mount the project directories so code changes on the host are reflected in the containers.
