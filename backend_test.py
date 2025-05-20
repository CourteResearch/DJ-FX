
import requests
import time
import sys
import os
from datetime import datetime

class AutomatedDJTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                return success, response.json() if response.content else {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                return success, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test(
            "Root Endpoint",
            "GET",
            "",
            200
        )

    def test_get_genres(self):
        """Test getting available genres"""
        success, response = self.run_test(
            "Get Genres",
            "GET",
            "genres",
            200
        )
        if success:
            print(f"Available genres: {response.get('genres', [])}")
        return success, response

    def test_create_mix(self, genre):
        """Test creating a new mix"""
        success, response = self.run_test(
            "Create Mix",
            "POST",
            "mixes",
            200,
            data={"genre": genre, "title": "Test Mix", "duration_minutes": 50}
        )
        if success:
            print(f"Mix created with ID: {response.get('id')}")
            print(f"Mix status: {response.get('status')}")
        return success, response

    def test_get_mixes(self):
        """Test getting all mixes"""
        success, response = self.run_test(
            "Get Mixes",
            "GET",
            "mixes",
            200
        )
        if success:
            print(f"Found {len(response)} mixes")
        return success, response

    def test_get_mix_by_id(self, mix_id):
        """Test getting a specific mix by ID"""
        success, response = self.run_test(
            "Get Mix by ID",
            "GET",
            f"mixes/{mix_id}",
            200
        )
        if success:
            print(f"Mix title: {response.get('title')}")
            print(f"Mix status: {response.get('status')}")
        return success, response

def main():
    # Get backend URL from environment or use default
    backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'https://c29c47e8-2a0e-4e89-833c-b83ab2684b03.preview.emergentagent.com')
    api_url = f"{backend_url}/api"
    
    print(f"Testing API at: {api_url}")
    
    # Setup tester
    tester = AutomatedDJTester(api_url)
    
    # Test root endpoint
    tester.test_root_endpoint()
    
    # Test getting genres
    genres_success, genres_response = tester.test_get_genres()
    if not genres_success:
        print("❌ Failed to get genres, stopping tests")
        return 1
    
    # Test getting mixes
    mixes_success, mixes_response = tester.test_get_mixes()
    
    # Test creating a mix if genres are available
    if genres_success and 'genres' in genres_response and len(genres_response['genres']) > 0:
        test_genre = genres_response['genres'][0]
        print(f"Creating a test mix with genre: {test_genre}")
        
        mix_success, mix_response = tester.test_create_mix(test_genre)
        if mix_success and 'id' in mix_response:
            mix_id = mix_response['id']
            
            # Wait a bit and then check the mix status
            print("Waiting 10 seconds to check mix status...")
            time.sleep(10)
            
            tester.test_get_mix_by_id(mix_id)
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
      