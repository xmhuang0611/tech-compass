# Tech Solutions (TSL)

A platform for showcasing and managing technical solutions within organizations. Tech Solutions helps development teams discover, compare, and evaluate various tools, processes, and practices used in software development.

## Components

The project is organized into the following components:

- `components/tsl-ui`: Frontend application built with Angular + PrimeNG
- `components/tsl-api`: Backend API service built with Python FastAPI
- `components/tsl-admin`: Admin panel built with Python Streamlit
- `components/tsl-radar`: Technology radar visualization

## Features

- 📊 Browse and search technical solutions
- ⭐ Rate and review solutions
- 🏷️ Tag-based categorization
- 📝 Detailed solution comparisons
- 📈 Technology radar visualization
- 🔍 Advanced filtering and search capabilities

## Tech Stack

- **Frontend**: Angular + PrimeNG
- **Backend**: Python FastAPI
- **Database**: MongoDB
- **Admin Panel**: Python Streamlit
- **Tech Radar**: Custom implementation

## Getting Started

### Prerequisites

- Node.js and npm
- Python 3.x
- MongoDB

### Installation

1. Clone the repository

```bash
git clone https://github.com/tobyqin/tech-solutions.git
cd tech-solutions
```

2. Set up and run the backend

```bash
cd components/tsl-api
pip install -r requirements.txt
python main.py
```

3. Set up and run the frontend

```bash
cd components/tsl-ui
npm install
ng serve
```

4. Set up and run the admin panel (optional)

```bash
cd components/tsl-admin
pip install -r requirements.txt
streamlit run app.py
```

5. Set up and run the tech radar (optional)

```bash
cd components/tsl-radar
npm install
npm start
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
