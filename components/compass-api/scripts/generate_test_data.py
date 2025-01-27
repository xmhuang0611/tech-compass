"""
Script to generate test data using the Compass API endpoints.
This script will:
1. Create a test user (test/test) if not exists
2. Create solutions with categories and tags
3. Add comments to solutions
4. Add ratings to solutions
"""

import os
import random
import traceback
from typing import Dict, Optional
from urllib.parse import urlencode

import faker
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
fake = faker.Faker()

def debug_request(method: str, url: str, **kwargs):
    """Print request details for debugging."""
    print(f"\n=== {method} {url} ===")
    if 'headers' in kwargs:
        print("Headers:", kwargs['headers'])
    if 'data' in kwargs:
        print("Form Data:", kwargs['data'])
    if 'json' in kwargs:
        print("JSON Data:", kwargs['json'])

class TestDataGenerator:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.solutions = []

    def create_test_user(self) -> Optional[Dict]:
        """Create test user if not exists."""
        user_data = {
            'username': 'test',
            'email': 'test@example.com',
            'password': 'test',
            'full_name': 'Test User',
            'is_active': True,
            'is_superuser': False
        }
        
        try:
            self.login_user('test', 'test')
            print("Test user already exists, skipping creation")
            return None
        except requests.exceptions.RequestException:
            # User doesn't exist, create it
            print("Creating test user...")
            url = f'{BASE_URL}/api/users'
            debug_request('POST', url, json=user_data)
            response = self.session.post(url, json=user_data)
            response.raise_for_status()
            return response.json()

    def login_user(self, username: str, password: str) -> str:
        """Login user and return authentication token."""
        # According to OpenAPI spec, login expects form data
        login_data = {
            'username': username,
            'password': password,
            'grant_type': 'password',
            'scope': ''
        }
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        url = f'{BASE_URL}/api/auth/login'
        encoded_data = urlencode(login_data)
        
        debug_request('POST', url, headers=headers, data=encoded_data)
        response = self.session.post(url, data=encoded_data, headers=headers)
        
        print("Response status:", response.status_code)
        print("Response headers:", dict(response.headers))
        print("Response body:", response.text)
        
        response.raise_for_status()
        token = response.json()['access_token']
        self.token = token
        return token

    def create_solution(self) -> Dict:
        """Create a new solution through the API."""
        radar_statuses = ['ADOPT', 'TRIAL', 'ASSESS', 'HOLD']
        stages = ['DEVELOPING', 'UAT', 'PRODUCTION', 'DEPRECATED', 'RETIRED']
        recommend_statuses = ['BUY', 'HOLD', 'SELL']
        
        solution_data = {
            'name': fake.catch_phrase(),
            'description': fake.text(max_nb_chars=200),
            'category': fake.word(),  # Primary category
            'radar_status': random.choice(radar_statuses),
            'department': fake.company_suffix(),
            'team': fake.job(),
            'team_email': fake.company_email(),
            'maintainer_name': fake.name(),
            'maintainer_email': fake.email(),
            'official_website': fake.url(),
            'documentation_url': fake.url(),
            'demo_url': fake.url(),
            'version': f"{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(0,9)}",
            'tags': [fake.word() for _ in range(random.randint(2, 5))],
            'pros': [fake.sentence() for _ in range(random.randint(2, 4))],
            'cons': [fake.sentence() for _ in range(random.randint(1, 3))],
            'stage': random.choice(stages),
            'recommend_status': random.choice(recommend_statuses)
        }
        
        headers = {'Authorization': f'Bearer {self.token}'}
        url = f'{BASE_URL}/api/solutions/'
        debug_request('POST', url, headers=headers, json=solution_data)
        response = self.session.post(url, json=solution_data, headers=headers)
        response.raise_for_status()
        return response.json()['data']

    def create_comment(self, solution_slug: str) -> Dict:
        """Create a new comment on a solution."""
        comment_data = {
            'content': fake.text(max_nb_chars=200)
        }
        
        headers = {'Authorization': f'Bearer {self.token}'}
        url = f'{BASE_URL}/api/comments/solution/{solution_slug}'
        debug_request('POST', url, headers=headers, json=comment_data)
        response = self.session.post(url, json=comment_data, headers=headers)
        response.raise_for_status()
        return response.json()

    def create_rating(self, solution_slug: str) -> Dict:
        """Create a new rating for a solution."""
        rating_data = {
            'score': random.randint(1, 5),
            'comment': fake.sentence() if random.random() > 0.5 else None
        }
        
        headers = {'Authorization': f'Bearer {self.token}'}
        url = f'{BASE_URL}/api/ratings/solution/{solution_slug}'
        debug_request('POST', url, headers=headers, json=rating_data)
        response = self.session.post(url, json=rating_data, headers=headers)
        response.raise_for_status()
        return response.json()

    def generate_test_data(
        self,
        num_solutions: int = 5,
        num_comments_per_solution: int = 4,
        num_ratings_per_solution: int = 1
    ):
        """Generate complete test dataset."""
        print("Starting test data generation...")

        # Create/login test user
        self.create_test_user()
        if not self.token:
            self.login_user('test', 'test')

        # Create solutions
        print(f"Creating {num_solutions} solutions...")
        for _ in range(num_solutions):
            solution = self.create_solution()
            self.solutions.append(solution)

        # Create comments and ratings for each solution
        for solution in self.solutions:
            print(f"Adding comments and ratings for solution: {solution['name']}")
            
            # Add comments
            for _ in range(num_comments_per_solution):
                self.create_comment(solution['slug'])

            # Add ratings
            for _ in range(num_ratings_per_solution):
                self.create_rating(solution['slug'])

        print("Test data generation completed successfully!")

def main():
    try:
        generator = TestDataGenerator()
        generator.generate_test_data()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred during API request: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    main()
