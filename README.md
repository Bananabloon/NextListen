# NextListen

NextListen is a web application for exploring, searching, and recommending music. It integrates Spotify user data with a custom knowledge base of albums and genres to generate personalized music recommendations and dynamic queues.

## Features

-   Generate queues based on your Spotify top artists and tracks
-   Create custom queues using specific artists, tracks, or genres
-   Add recommended songs to your Liked Tracks playlist on Spotify
-

## Tech Stack

**Backend**

-   Python
-   Django
-   Django REST Framework
-   drf-spectacular (OpenAPI/Swagger)

**Frontend**

-   React (Vite)
-   TypeScript

**Database**

-   MySQL

**Integrations**

-   Spotify Web API
-   OpenAI API

**Other Tools**

-   Docker
-   Nginx (reverse proxy)
-   pre-commit, black, flake8

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd nextlisten
```

### 2. Generate SSL keys and put them in ngnix

-   Generate localhost.cert, and localhost.key
-   Put them in nginx/certs

### 2. Setup frontend

```bash
cd frontend/webApp
npm install
```

### 3. Setup ngrok

run

```bash
ngrok http 443
```

### 4. Setup the .env

Backend Environment (`backend/.env`)

```env
SPOTIFY_CLIENT_ID=YOUR_CLIENT_ID
SPOTIFY_CLIENT_SECRET=YOUR_CLIENT_SECRET
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/auth/spotify/callback/
OPENAI_API_KEY=YOUR_OPENAI_KEY
NGROK_URL=YOUR_NGROK_URL
```

Frontend Environment (`frontend/webApp/.env`)

```env
VITE_NGROK_DEVELOPMENT_URL=SAME_AS_YOUR_BACKEND_NGROK_URL
```

### 2. Run the Application with Docker

```bash
docker-compose up --build
```

### 3. Inside the Backend Container

```bash
docker exec -it nextlisten-backend-1 bash
python manage.py makemigrations
python manage.py migrate
```

## Access

-   Frontend: http://localhost:5173
-   Backend API (Swagger Docs): http://localhost:8000/api/docs/

## Configuration

## API Documentation

API documentation is auto-generated and available after starting the backend:

http://localhost:8000/api/docs/

## Notes

-   All API keys previously committed have been revoked and replaced.
-   Qdrant was supposed to be used as RAG with sentence transformers using discogs DB, but there wasn't enought time. You can try implementing it
-   The algorythm gets better as you like more and more
-   Because of the lack of RAG, there are only tracks from the latest ai model snapshot
