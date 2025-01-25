# Test Data Generation Scripts

This directory contains scripts for generating test data for the Compass API.

## Generate Test Data

The `generate_test_data.py` script creates a complete test dataset using the API endpoints. It will create:
- Users (including an admin user)
- Solutions with categories and tags
- Comments on solutions
- Ratings for solutions

### Prerequisites

1. Make sure you have all required packages installed:
```bash
pip install -r requirements.txt
```

2. Configure your environment variables in `.env`:
```
API_BASE_URL=http://localhost:8000  # Your API base URL
```

### Usage

1. Make sure your API server is running
2. Run the script:
```bash
python scripts/generate_test_data.py
```

### What the Script Does

1. Creates a test user if not existed (test/test)
2. Creates regular users (default: 5)
3. Generates solutions (default: 10) with random categories and tags
4. Adds comments to solutions (default: 3 per solution)
5. Adds ratings to solutions (default: 5 per solution)

You can modify these numbers by editing the parameters in the `generate_test_data()` method call in the script.

### Notes

- The script includes rate limiting (0.5s delay between requests) to prevent overwhelming the API
- Will create test user if not existed
- The script uses the Faker library to generate realistic-looking data
- If any errors occur during execution, they will be logged to the console

"""
generate test data by using solution api post methods
1. clear existing data from db: user, solution, category, tag (use same .env config)
2. create admin user by post /api/users (auth server enable = false, allow any user to login)
3. post fake solutions one by one (category should be auto created, slug should be auto generated in backend)
"""