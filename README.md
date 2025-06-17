# NextListen

NextListen is a web application for exploring, searching, and recommending music. It integrates Spotify user data with a custom knowledge base of albums and genres to generate personalized music recommendations and dynamic queues.

## Features

- Generate queues based on your Spotify top artists and tracks  
- Create custom queues using specific artists, tracks, or genres  
- Add recommended songs to your Liked Tracks playlist on Spotify  

## Tech Stack

**Backend:**  
- Python  
- Django  
- Django REST Framework  
- drf-spectacular (OpenAPI/Swagger)  

**Frontend:**  
- React (Vite)  
- TypeScript  

**Database:**  
- MySQL  
- Qdrant
  
**Integrations:**  
- Spotify Web API  
- OpenAI API  

**Other Tools:**  
- Docker  
- Nginx (reverse proxy)  
- pre-commit, black, flake8  

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd nextlisten
```

### 2. Generate SSL Certificates and place them in the Nginx folder

- Generate `localhost.cert` and `localhost.key`  
- Place them inside the `nginx/certs` directory

### 3. Install frontend dependencies

```bash
cd frontend/webApp
npm install
```

### 4. Run ngrok

Tunnel port 443 (HTTPS):

```bash
ngrok http 443
```

### 5. Configure environment files (.env)

#### Backend (`backend/.env`)

```env
SPOTIFY_CLIENT_ID=YOUR_CLIENT_ID
SPOTIFY_CLIENT_SECRET=YOUR_CLIENT_SECRET
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/auth/spotify/callback/
OPENAI_API_KEY=YOUR_OPENAI_KEY
NGROK_URL=YOUR_NGROK_URL
```

#### Frontend (`frontend/webApp/.env`)

```env
VITE_NGROK_DEVELOPMENT_URL=SAME_AS_YOUR_BACKEND_NGROK_URL
```

### 6. Run the application with Docker

```bash
docker-compose up --build
```

### 7. Inside the backend container, apply migrations

```bash
docker exec -it nextlisten-backend-1 bash
python manage.py makemigrations
python manage.py migrate
```
### 8. All done

enter the ngrok url and enjoy

## Access

- Frontend: http://localhost:5173  
- Backend : http://localhost:8000/api/

## API Documentation

API docs are auto-generated and available after backend startup at:

http://localhost:8000/api/docs/

## Notes

- All previously committed API keys and SSL certificates have been revoked and replaced.  
- Qdrant was planned to be used as RAG with sentence transformers based on the Discogs DB, but there wasn't enough time to implement it — feel free to try adding it.  
- The recommendation algorithm improves as you like more tracks.  
- Due to the lack of RAG, only tracks from the latest AI model snapshot are available.
