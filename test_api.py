#!/usr/bin/env python3
"""
Simple test script to verify the HealthTrack API is working correctly.
Run this script after starting the Django server.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

def test_api_connection():
    """Test basic API connectivity"""
    try:
        response = requests.get(f"{BASE_URL}/auth/register/")
        print("✅ API server is running and accessible")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Make sure Django server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    print("\n🧪 Testing user registration...")
    
    test_user = {
        "username": "testuser123",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpass123",
        "password_confirm": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register/", json=test_user)
        
        if response.status_code == 201:
            print("✅ User registration successful")
            data = response.json()
            return data.get('tokens', {}).get('access', '')
        else:
            print(f"❌ User registration failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        return None

def test_activity_creation(access_token):
    """Test activity creation"""
    print("\n🧪 Testing activity creation...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    test_activity = {
        "title": "Morning Workout",
        "description": "30-minute cardio session",
        "activity_type": "workout",
        "status": "planned",
        "planned_date": "2024-12-31T10:00:00Z",
        "duration_minutes": 30,
        "calories_burned": 300
    }
    
    try:
        response = requests.post(f"{BASE_URL}/activities/", json=test_activity, headers=headers)
        
        if response.status_code == 201:
            print("✅ Activity creation successful")
            return True
        else:
            print(f"❌ Activity creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during activity creation: {e}")
        return False

def test_activity_list(access_token):
    """Test activity listing"""
    print("\n🧪 Testing activity listing...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/activities/", headers=headers)
        
        if response.status_code == 200:
            print("✅ Activity listing successful")
            data = response.json()
            print(f"Found {len(data.get('results', []))} activities")
            return True
        else:
            print(f"❌ Activity listing failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during activity listing: {e}")
        return False

def main():
    print("🚀 HealthTrack API Test Suite")
    print("=" * 40)
    
    # Test 1: API Connection
    if not test_api_connection():
        sys.exit(1)
    
    # Test 2: User Registration
    access_token = test_user_registration()
    if not access_token:
        print("\n⚠️  Skipping authenticated tests due to registration failure")
        sys.exit(1)
    
    # Test 3: Activity Creation
    if not test_activity_creation(access_token):
        print("\n⚠️  Activity creation failed")
    
    # Test 4: Activity Listing
    if not test_activity_list(access_token):
        print("\n⚠️  Activity listing failed")
    
    print("\n" + "=" * 40)
    print("🎉 API tests completed!")
    print("\nNext steps:")
    print("1. Start the React frontend: npm start (in fitness-tracker-frontend directory)")
    print("2. Open http://localhost:3000 in your browser")
    print("3. Register a new account or login with the test user (testuser123 / testpass123)")

if __name__ == "__main__":
    main()








