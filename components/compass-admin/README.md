# Tech Compass Admin

Admin dashboard component for Tech Compass, built with Streamlit. This application provides an interface for managing content, user ratings, comments, tags, and site configuration.

## Prerequisites

- Python 3.9+
- pip (Python package manager)

## Setup

1. Create and activate a virtual environment (recommended):
```bash
cd compass-admin
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Development

To run the application locally:

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Project Structure

- `app.py` - Main application entry point
- `Home.py` - Home page component
- `pages/` - Directory containing different sections of the admin panel
- `utils/` - Utility functions for authentication and API calls
- `requirements.txt` - Python dependencies

## Deployment

1. Ensure all dependencies are listed in `requirements.txt`
2. Deploy using your preferred hosting platform (e.g., Streamlit Cloud, Docker, or custom server)

## Features

- Authentication system
- Content management (Solutions, Categories)
- User interaction management (Comments, Ratings)
- Tag management
- Site configuration 