#!/usr/bin/env python3
"""
Test script for authentication endpoints
"""

import requests
import time

BASE_URL = "http://localhost:8002/api/v1"

def test_phone_login():
    print("Testing phone login...")

    # Step 1: Send OTP
    response = requests.post(f"{BASE_URL}/auth/phone-login", json={
        "phone_number": "9999999999"
    })

    print(f"OTP Send - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
        if data.get('detail', {}).get('code') == 'OTP_SENT':
            print("✅ OTP sent successfully")
            return True
    else:
        print(f"❌ Failed: {response.text}")
    return False

def test_facebook_login():
    print("\nTesting Facebook login...")

    response = requests.post(f"{BASE_URL}/auth/facebook-login")

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
        if 'access_token' in data:
            print("✅ Facebook login successful")
            return data['access_token']
    else:
        print(f"❌ Failed: {response.text}")
    return None

def test_demo_login():
    print("\nTesting demo login...")

    response = requests.post(f"{BASE_URL}/auth/demo-login")

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
        if 'access_token' in data:
            print("✅ Demo login successful")
            return data['access_token']
    else:
        print(f"❌ Failed: {response.text}")
    return None

if __name__ == "__main__":
    print("🚀 Testing GigShield Authentication Endpoints")
    print("=" * 50)

    # Test phone login
    test_phone_login()

    # Test Facebook login
    test_facebook_login()

    # Test demo login
    test_demo_login()

    print("\n✨ Testing complete!")