# Tech Compass Admin

A Streamlit-based admin dashboard for managing Tech Compass platform content, including solutions, categories, tags, and user interactions.

## Requirements

- Python 3.12+
- pip (Package manager)
- Virtual environment (venv recommended)

## Quick Start

### 1. Clone Repository

```bash
git clone [your-repository-url]
cd compass-admin
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
# .\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory:

```bash
# API Configuration
API_BASE_URL=http://localhost:8000/api  # Replace with actual API URL
```

### 5. Launch Application

```bash
streamlit run Home.py
```

The application will be available at http://localhost:8501

## Project Structure

```
compass-admin/
├── Home.py                 # Main entry point
├── pages/                  # Page components
│   ├── 2_Solutions.py     # Solutions management
│   ├── 3_Categories.py    # Categories management
│   ├── 4_Tags.py         # Tags management
│   └── ...               # Other management pages
├── utils/                  # Utility modules
│   ├── api.py             # API client
│   ├── auth.py            # Authentication
│   └── common.py          # Shared utilities
└── requirements.txt        # Dependencies
```

## Development Guidelines

1. Follow PEP 8 style guide
2. Add type hints for new functions
3. Keep dependencies updated
4. Use feature branches for development
5. Write descriptive commit messages
