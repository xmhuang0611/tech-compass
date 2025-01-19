# TSL API

Backend service for Tech Solutions (TSL) platform built with FastAPI.

## Features

- RESTful API endpoints for managing technical solutions
- MongoDB integration for data storage
- JWT-based authentication
- Rate limiting
- Input validation and error handling
- Documentation with OpenAPI/Swagger

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with required environment variables:
```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=tsl
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

4. Run the development server:
```bash
uvicorn app.main:app --reload --port 8000
```

## API Documentation

Once the server is running, access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
tsl-api/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   ├── solutions.py
│   │   │   │   ├── tags.py
│   │   │   │   └── users.py
│   │   │   └── api.py
│   │   └── deps.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── mongodb.py
│   │   └── models.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── solution.py
│   │   ├── tag.py
│   │   └── user.py
│   └── main.py
├── requirements.txt
└── README.md
```
