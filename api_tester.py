#!/usr/bin/env python3
"""
Fixed Automated API Testing Framework for Steady Hands API
Server: http://10.10.20.62:5000
Based on actual Postman collection endpoints
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
import unittest

class APITester:
    def __init__(self, base_url: str = "http://10.10.20.62:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        self.tokens = {}  # Store tokens for different user types
        
    def log_result(self, endpoint: str, method: str, status_code: int, 
                  response_data: Any, success: bool, message: str = ""):
        """Log test results"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "success": success,
            "message": message,
            "response": response_data
        }
        self.results.append(result)
        
        # Print result with better formatting
        status = "PASS" if success else "FAIL"
        print(f"{status} | {method} {endpoint} | Status: {status_code} | {message}")
        
    def test_health(self) -> bool:
        """Test server health check"""
        endpoint = "/"
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, timeout=10)
            success = response.status_code == 200
            message = "Server is healthy" if success else "Server health check failed"
            
            self.log_result(endpoint, "GET", response.status_code, 
                          response.text[:100], success, message)
            
            return success
            
        except requests.exceptions.RequestException as e:
            self.log_result(endpoint, "GET", 0, {}, False, f"Request failed: {str(e)}")
            return False
        
    def test_signup(self, user_data: Dict[str, str]) -> Optional[Dict]:
        """Test POST /api/v1/auth/signup"""
        endpoint = "/api/v1/auth/signup"
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.post(url, json=user_data, timeout=10)
            response_data = response.json() if response.content else {}
            
            # Check if signup was successful (200 or 201)
            success = response.status_code in [200, 201]
            message = response_data.get('message', 'Signup completed')
            
            # Handle different response structures
            if success and 'data' in response_data:
                # Store any token if provided
                token = response_data['data'].get('accessToken')
                if token:
                    self.tokens['signup'] = token
                    
            self.log_result(endpoint, "POST", response.status_code, 
                          response_data, success, message)
            
            return response_data if success else None
            
        except requests.exceptions.RequestException as e:
            self.log_result(endpoint, "POST", 0, {}, False, f"Request failed: {str(e)}")
            return None
            
    def test_signin(self, credentials: Dict[str, str]) -> Optional[str]:
        """Test POST /api/v1/auth/signin"""
        endpoint = "/api/v1/auth/signin"
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.post(url, json=credentials, timeout=10)
            response_data = response.json() if response.content else {}
            
            success = response.status_code == 200
            message = response_data.get('message', 'Authentication result')
            
            # Extract token from the correct response structure
            token = None
            if success and 'data' in response_data:
                token = response_data['data'].get('accessToken')
                if token:
                    self.tokens['signin'] = token
                    # Set Authorization header for subsequent requests
                    self.session.headers.update({'Authorization': f'Bearer {token}'})
            
            self.log_result(endpoint, "POST", response.status_code, 
                          response_data, success, message)
            
            return token
            
        except requests.exceptions.RequestException as e:
            self.log_result(endpoint, "POST", 0, {}, False, f"Request failed: {str(e)}")
            return None
            
    def test_signup_verify_otp(self, otp_data: Dict[str, str], token: str = None) -> bool:
        """Test POST /api/v1/auth/verify-signup-otp"""
        endpoint = "/api/v1/auth/verify-signup-otp"
        url = f"{self.base_url}{endpoint}"
        
        # Set token if provided
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            response = self.session.post(url, json=otp_data, headers=headers, timeout=10)
            response_data = response.json() if response.content else {}
            
            success = response.status_code == 200
            message = response_data.get('message', 'OTP verification result')
            
            self.log_result(endpoint, "POST", response.status_code, 
                          response_data, success, message)
            
            return success
            
        except requests.exceptions.RequestException as e:
            self.log_result(endpoint, "POST", 0, {}, False, f"Request failed: {str(e)}")
            return False
            
    def test_change_password(self, password_data: Dict[str, str]) -> bool:
        """Test PATCH /api/v1/auth/change-password"""
        endpoint = "/api/v1/auth/change-password"
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.patch(url, json=password_data, timeout=10)
            response_data = response.json() if response.content else {}
            
            success = response.status_code == 200
            message = response_data.get('message', 'Password change result')
            
            self.log_result(endpoint, "PATCH", response.status_code, 
                          response_data, success, message)
            
            return success
            
        except requests.exceptions.RequestException as e:
            self.log_result(endpoint, "PATCH", 0, {}, False, f"Request failed: {str(e)}")
            return False
            
    def test_forget_password(self, email_data: Dict[str, str]) -> Optional[Dict]:
        """Test POST /api/v1/auth/forget-password"""
        endpoint = "/api/v1/auth/forget-password"
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.post(url, json=email_data, timeout=10)
            response_data = response.json() if response.content else {}
            
            success = response.status_code == 200
            message = response_data.get('message', 'Forget password request result')
            
            self.log_result(endpoint, "POST", response.status_code, 
                          response_data, success, message)
            
            return response_data if success else None
            
        except requests.exceptions.RequestException as e:
            self.log_result(endpoint, "POST", 0, {}, False, f"Request failed: {str(e)}")
            return None
            
    def test_forget_password_verify(self, verify_data: Dict[str, str]) -> bool:
        """Test POST /api/v1/auth/forget-password-verify"""
        endpoint = "/api/v1/auth/forget-password-verify"
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.post(url, json=verify_data, timeout=10)
            response_data = response.json() if response.content else {}
            
            success = response.status_code == 200
            message = response_data.get('message', 'Password reset verification result')
            
            self.log_result(endpoint, "POST", response.status_code, 
                          response_data, success, message)
            
            return success
            
        except requests.exceptions.RequestException as e:
            self.log_result(endpoint, "POST", 0, {}, False, f"Request failed: {str(e)}")
            return False
            
    def test_reset_password(self, reset_data: Dict[str, str], token: str = None) -> bool:
        """Test POST /api/v1/auth/reset-password"""
        endpoint = "/api/v1/auth/reset-password"
        url = f"{self.base_url}{endpoint}"
        
        # Set token if provided
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            response = self.session.post(url, json=reset_data, headers=headers, timeout=10)
            response_data = response.json() if response.content else {}
            
            success = response.status_code == 200
            message = response_data.get('message', 'Password reset result')
            
            self.log_result(endpoint, "POST", response.status_code, 
                          response_data, success, message)
            
            return success
            
        except requests.exceptions.RequestException as e:
            self.log_result(endpoint, "POST", 0, {}, False, f"Request failed: {str(e)}")
            return False
            
    def test_social_signin(self, social_data: Dict[str, str]) -> Optional[str]:
        """Test POST /api/v1/auth/social-signin"""
        endpoint = "/api/v1/auth/social-signin"
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.post(url, json=social_data, timeout=10)
            response_data = response.json() if response.content else {}
            
            success = response.status_code == 200
            message = response_data.get('message', 'Social signin result')
            
            # Extract token
            token = None
            if success and 'data' in response_data:
                token = response_data['data'].get('accessToken')
                if token:
                    self.tokens['social'] = token
            
            self.log_result(endpoint, "POST", response.status_code, 
                          response_data, success, message)
            
            return token
            
        except requests.exceptions.RequestException as e:
            self.log_result(endpoint, "POST", 0, {}, False, f"Request failed: {str(e)}")
            return None
            
    def test_fetch_profile_data(self) -> bool:
        """Test GET /api/v1/auth/profile"""
        endpoint = "/api/v1/auth/profile"
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, timeout=10)
            response_data = response.json() if response.content else {}
            
            success = response.status_code == 200
            message = response_data.get('message', 'Profile data fetch result')
            
            self.log_result(endpoint, "GET", response.status_code, 
                          response_data, success, message)
            
            return success
            
        except requests.exceptions.RequestException as e:
            self.log_result(endpoint, "GET", 0, {}, False, f"Request failed: {str(e)}")
            return False
            
    def test_profile_image_upload(self, image_path: str = None) -> bool:
        """Test PUT /api/v1/auth/profile-image"""
        endpoint = "/api/v1/auth/profile-image"
        url = f"{self.base_url}{endpoint}"
        
        try:
            # Simulate file upload with dummy data if no actual file provided
            files = {}
            if image_path:
                files = {'file': open(image_path, 'rb')}
            else:
                # Create a dummy text file for testing
                files = {'file': ('test.txt', 'dummy image data', 'text/plain')}
            
            response = self.session.put(url, files=files, timeout=10)
            response_data = response.json() if response.content else {}
            
            success = response.status_code == 200
            message = response_data.get('message', 'Profile image upload result')
            
            self.log_result(endpoint, "PUT", response.status_code, 
                          response_data, success, message)
            
            return success
            
        except requests.exceptions.RequestException as e:
            self.log_result(endpoint, "PUT", 0, {}, False, f"Request failed: {str(e)}")
            return False
        except Exception as e:
            self.log_result(endpoint, "PUT", 0, {}, False, f"File error: {str(e)}")
            return False

    def test_signup_verify_otp_again(self, token: str = None) -> bool:
        """Test POST /api/v1/auth/verify-signup-otp-again"""
        endpoint = "/api/v1/auth/verify-signup-otp-again"
        url = f"{self.base_url}{endpoint}"
        
        # Set token if provided
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            response = self.session.post(url, json={}, headers=headers, timeout=10)
            response_data = response.json() if response.content else {}
            
            success = response.status_code == 200
            message = response_data.get('message', 'OTP resend result')
            
            self.log_result(endpoint, "POST", response.status_code, 
                          response_data, success, message)
            
            return success
            
        except requests.exceptions.RequestException as e:
            self.log_result(endpoint, "POST", 0, {}, False, f"Request failed: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run comprehensive test suite with proper error handling"""
        print("Starting Comprehensive API Testing")
        print("=" * 70)
        print(f"Testing server: {self.base_url}")
        print("=" * 70)
        
        # Test server health first
        print("\nTesting Server Health...")
        if not self.test_health():
            print("Server is not responding. Aborting tests.")
            return
        
        # Generate unique test data
        timestamp = int(time.time())
        test_user = {
            "fullName": "Test User Auto",
            "email": f"testuser{timestamp}@example.com",
            "phoneNumber": "+8801234567890",
            "password": "TestPassword123@!"
        }
        
        credentials = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        print(f"\nTesting with user: {test_user['email']}")
        
        # 1. Test Signup
        print("\nTesting User Registration...")
        signup_result = self.test_signup(test_user)
        signup_token = self.tokens.get('signup')
        
        # 2. Test OTP verification (if signup was successful)
        if signup_result and signup_token:
            print("\nTesting OTP Verification...")
            otp_data = {"otp": "123456"}  # Dummy OTP
            self.test_signup_verify_otp(otp_data, signup_token)
            
            # Test OTP resend
            print("\nTesting OTP Resend...")
            self.test_signup_verify_otp_again(signup_token)
        
        # 3. Test Signin
        print("\nTesting User Authentication...")
        token = self.test_signin(credentials)
        
        # 4. Test authenticated endpoints (if signin was successful)
        if token:
            print("\nTesting Profile Operations...")
            
            # Test profile fetch
            self.test_fetch_profile_data()
            
            # Test profile image upload
            self.test_profile_image_upload()
            
            # Test password change
            print("\nTesting Password Change...")
            password_data = {
                "oldPassword": test_user["password"], 
                "newPassword": "NewPassword123@!"
            }
            self.test_change_password(password_data)
        
        # 5. Test password reset flow
        print("\nTesting Password Reset Flow...")
        forget_result = self.test_forget_password({"email": test_user["email"]})
        
        if forget_result:
            # Test forget password verification
            verify_data = {
                "token": "dummy_token",
                "otp": "123456"
            }
            self.test_forget_password_verify(verify_data)
            
            # Test reset password
            reset_data = {"newPassword": "ResetPassword123@!"}
            self.test_reset_password(reset_data, "dummy_reset_token")
        
        # 6. Test social signin
        print("\nTesting Social Sign-in...")
        social_data = {
            "email": f"social{timestamp}@example.com",
            "fcmToken": "fcm_token_12345_example",
            "image": "https://example.com/profile.jpg",
            "fullName": "Social User",
            "phoneNumber": "1234567890",
            "address": "123 Main St, Test City"
        }
        self.test_social_signin(social_data)
        
        self.print_summary()
        
    def print_summary(self):
        """Print detailed test summary"""
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        
        if total_tests > 0:
            success_rate = (passed_tests/total_tests)*100
            print(f"Success Rate: {success_rate:.1f}%")
            
            # Show status distribution
            status_codes = {}
            for result in self.results:
                code = result['status_code']
                status_codes[code] = status_codes.get(code, 0) + 1
            
            print(f"\nHTTP Status Code Distribution:")
            for code, count in sorted(status_codes.items()):
                print(f"   {code}: {count} requests")
        
        if failed_tests > 0:
            print(f"\nFailed Tests Details:")
            for result in self.results:
                if not result['success']:
                    print(f"   • {result['method']} {result['endpoint']}")
                    print(f"     Status: {result['status_code']} | {result['message']}")
        
        if passed_tests > 0:
            print(f"\nSuccessful Tests:")
            for result in self.results:
                if result['success']:
                    print(f"   • {result['method']} {result['endpoint']} - {result['message']}")
        
        # Show collected tokens
        if self.tokens:
            print(f"\nCollected Tokens:")
            for token_type, token in self.tokens.items():
                print(f"   {token_type}: {token[:20]}...")
                    
        # Save results to file
        try:
            with open('api_test_results.json', 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\nDetailed results saved to: api_test_results.json")
        except Exception as e:
            print(f"\nCould not save results to file: {e}")

def main():
    print("Steady Hands API Testing Framework")
    print("Server: http://10.10.20.62:5000")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize tester
    tester = APITester()
    
    try:
        # Run comprehensive tests
        tester.run_comprehensive_test()
        print("\n Tests completed successfully!")
        print(" Results saved to: api_test_results.json")
    except Exception as e:
        print(f"Error during testing: {str(e)}")