# Tech Solutions (TSL)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

A platform for showcasing and managing technical solutions within organizations. Tech Solutions helps development teams discover, compare, and evaluate various tools, processes, and practices used in software development.

## 🌟 Features

- 📊 **Solution Discovery**
  - Browse and search technical solutions
  - Advanced filtering and search capabilities
  - Detailed solution comparisons
- ⭐ **Evaluation System**
  - Rate and review solutions
  - Comment and discuss implementations
  - Track usage statistics
- 🏷️ **Organization**
  - Tag-based categorization
  - Custom taxonomies
  - Team-based organization
- 📈 **Visualization**
  - Technology radar visualization
  - Adoption trends
  - Impact analysis
- 🔐 **Access Control**
  - Role-based permissions
  - Team management
  - Audit logging

## 🏗️ Architecture

The project follows a microservices architecture with the following components:

- `components/tsl-ui`: Frontend application built with Angular + PrimeNG
- `components/tsl-api`: Backend API service built with Python FastAPI
- `components/tsl-admin`: Admin panel built with Python Streamlit
- `components/tsl-radar`: Technology radar visualization

## 🛠️ Tech Stack

- **Frontend**: 
  - Angular 15+
  - PrimeNG
  - TypeScript
- **Backend**: 
  - Python FastAPI
  - MongoDB
  - Redis (caching)
- **Admin Panel**: 
  - Python Streamlit
- **DevOps**:
  - Docker
  - GitHub Actions
  - Kubernetes (optional)

## 🚀 Getting Started

### Prerequisites

- Node.js 16+ and npm
- Python 3.9+
- MongoDB 5.0+
- Docker (optional)

### Environment Setup

1. **Clone the repository**

```bash
git clone https://github.com/tobyqin/tech-solutions.git
cd tech-solutions
```

2. **Backend Setup**

```bash
cd components/tsl-api
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

python main.py
```

3. **Frontend Setup**

```bash
cd components/tsl-ui
npm install

# Configure environment
cp environment.example.ts environment.ts
# Edit environment.ts with your configuration

ng serve
```

4. **Admin Panel Setup**

```bash
cd components/tsl-admin
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .streamlit/config.example.toml .streamlit/config.toml
# Edit config.toml with your configuration

streamlit run app.py
```

5. **Tech Radar Setup**

```bash
cd components/tsl-radar
npm install
npm start
```

### 🐳 Docker Setup (Alternative)

```bash
docker-compose up -d
```

## 👩‍💻 Development

### Branch Strategy

- `main`: Production-ready code
- `develop`: Development branch
- Feature branches: `feature/*`
- Bug fixes: `fix/*`

### Code Style

- Frontend: ESLint + Prettier
- Backend: Black + isort
- Pre-commit hooks are configured

### Testing

```bash
# Backend tests
cd components/tsl-api
pytest

# Frontend tests
cd components/tsl-ui
ng test
```

## 🤝 Contributing

We welcome contributions! Please search existing issues before creating new ones. For code contributions, fork the repo, make your changes with tests, and submit a PR.

## 📫 Contact

- **Project Lead**: Toby Qin
- **Issue Tracker**: [GitHub Issues](https://github.com/tobyqin/tech-solutions/issues)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
Last updated: 2025-01-17
