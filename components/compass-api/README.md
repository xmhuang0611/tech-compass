# TC API

Backend service for Tech Compass (TC) platform built with FastAPI.

## Features

- RESTful API endpoints for managing technical solutions
- MongoDB integration for data storage
- JWT-based authentication
- Rate limiting
- Input validation and error handling
- Documentation with OpenAPI/Swagger

## Development Setup

1. Create and activate Python virtual environment:
```bash
python -m venv venv311
source venv311/bin/activate
# On Windows: venv311\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file in the project root:
```bash
cp .env.example .env
```

4. Update the `.env` file with your settings:
```env
MONGODB_URL=your_mongodb_connection_string
DATABASE_NAME=tc
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
AUTH_SERVER_URL=http://localhost:8000/auth
AUTH_SERVER_ENABLED=false
```

5. Start the development server:
```bash
# From the project root
python main.py
```

The server will start with hot reload enabled at http://localhost:8000

## API Documentation

Once the server is running, you can access:
- Interactive API docs (Swagger UI): http://localhost:8000/docs
- Alternative API docs (ReDoc): http://localhost:8000/redoc

## Development Workflow

1. The server will automatically reload when you make changes to any Python files in the `app` directory
2. Use the Swagger UI to test API endpoints interactively
3. For development, the authentication is set to accept any username/password combination
4. MongoDB connection is verified on startup

## VSCode Settings

Install the following extensions:
- Python
- Ruff
- Prettier - Code formatter
- Material Icon Theme

```json
{
  "git.enableSmartCommit": true,
  "git.confirmSync": false,
  "git.autofetch": true,
  "git.openRepositoryInParentFolders": "always",
  "workbench.iconTheme": "material-icon-theme",
  "files.autoSave": "afterDelay",
  "cursor.cpp.enablePartialAccepts": true,
  "cursor.composer.collapsePaneInputBoxPills": true,
  "cursor.composer.renderPillsInsteadOfBlocks": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/.idea": true
  },
  "explorer.confirmDelete": false,
  "search.useParentIgnoreFiles": true,
  "editor.formatOnSave": true,
  "editor.formatOnPaste": true,
  "ruff.lineLength": 120,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit",
      "source.fixAll": "explicit"
    }
  },
  "ruff.importStrategy": "useBundled",
  "[scss]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "explorer.confirmDragAndDrop": false,
  "editor.codeActionsOnSave": {
    "source.organizeImports": "explicit",
    "source.unusedImports": "always",
    "source.fixAll.ruff": "explicit"
  }
}
```