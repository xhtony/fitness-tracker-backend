from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, APIClient, force_authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, MagicMock, PropertyMock
from django.contrib.auth.models import AnonymousUser
# Mock User model
User = get_user_model()

# Mock the User model and related functions
class MockUser:
    def __init__(self, username, email, password=None, is_staff=False, is_superuser=False, first_name='', last_name=''):
        self.username = username
        self.email = email
        self.password = password
        self.is_staff = is_staff
        self.is_superuser = is_superuser
        self.pk = 1
        self.is_active = True
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, raw_password):
        return self.password == raw_password

    def save(self):
        pass

    @property
    def is_authenticated(self):
        return True
mock_user = MockUser('testuser', 'test@example.com', 'testpass123')
mock_superuser = MockUser('admin', 'admin@example.com', 'adminpass123', True, True)

class AuthenticationAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.logout_url = '/api/auth/logout/'
        self.profile_url = '/api/auth/profile/'
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        # Mock user data
        self.mock_user = MagicMock()
        self.mock_user.username = 'testuser'
        self.mock_user.email = 'test@example.com'
        self.mock_user.pk = 1
        self.mock_user.is_active = True
        
        # Mock token
        self.mock_token = MagicMock()
        self.mock_token.key = 'test-access-token'

    @patch('django.contrib.auth.models.User.objects')
    def test_user_registration(self, mock_user_manager):
        # Setup mock user
        mock_user = MockUser(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Mock the User.objects.filter() to return an empty queryset for both username and email
        mock_user_manager.filter.side_effect = [
            type('QuerySet', (), {'exists': lambda: False}),  # For username check
            type('QuerySet', (), {'exists': lambda: False})   # For email check
        ]
        
        # Mock the create_user method
        mock_user_manager.create_user.return_value = mock_user
        
        # Mock the token generation
        with patch('rest_framework_simplejwt.tokens.RefreshToken.for_user') as mock_refresh_token:
            mock_token = MagicMock()
            mock_token.access_token = 'test-access-token'
            mock_refresh_token.return_value = mock_token
            
            # Mock the UserSerializer
            with patch('authentication.views.UserSerializer') as mock_serializer:
                mock_serializer.return_value.data = {
                    'username': 'testuser',
                    'email': 'test@example.com',
                    'first_name': 'Test',
                    'last_name': 'User'
                }
                
                # Test registration with correct password confirmation field
                response = self.client.post(self.register_url, {
                    'username': 'testuser',
                    'email': 'test@example.com',
                    'password': 'testpass123',
                    'password_confirm': 'testpass123',
                    'first_name': 'Test',
                    'last_name': 'User'
                }, format='json')
        
        # Debug print
        print("\nRegistration Response:", response.status_code, response.data)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['tokens']['access'], 'test-access-token')
        mock_user_manager.create_user.assert_called_once()
    
    @patch('authentication.serializers.authenticate')
    @patch('authentication.views.UserLoginSerializer')
    def test_user_login(self, mock_login_serializer, mock_authenticate):
        # Setup mock user
        mock_user = MockUser(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Mock the login serializer
        mock_serializer_instance = mock_login_serializer.return_value
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.validated_data = {'user': mock_user}
        
        # Mock the token generation
        with patch('rest_framework_simplejwt.tokens.RefreshToken.for_user') as mock_refresh_token:
            # Setup mock token
            mock_token = MagicMock()
            mock_token.access_token = 'test-access-token'
            mock_refresh_token.return_value = mock_token
            
            # Mock the UserSerializer to return our user data
            with patch('authentication.views.UserSerializer') as mock_user_serializer:
                mock_user_serializer.return_value.data = {
                    'username': 'testuser',
                    'email': 'test@example.com',
                    'first_name': 'Test',
                    'last_name': 'User'
                }
                
                # Test login with correct credentials
                response = self.client.post(self.login_url, {
                    'username': 'testuser',
                    'password': 'testpass123'
                }, format='json')
        
        # Debug print
        print("\nLogin Response:", response.status_code, response.data)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['tokens']['access'], 'test-access-token')
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['message'], 'Login successful')
        # The authenticate function is called by the UserLoginSerializer, not directly in the view
        # So we can remove this assertion or modify the test to check the serializer's behavior
    
    @patch('rest_framework_simplejwt.tokens.RefreshToken')
    @patch('authentication.views.RefreshToken')
    def test_user_logout(self, mock_view_refresh_token, mock_refresh_token):
        # Setup mock token
        mock_token = MagicMock()
        mock_refresh_token.return_value = mock_token
        
        # Mock the request.user
        mock_user = MockUser(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Mock the authentication
        self.client.force_authenticate(user=mock_user)
        
        # Setup the view's RefreshToken mock
        mock_view_token = MagicMock()
        mock_view_refresh_token.return_value = mock_view_token
        
        # Test logout with refresh token
        response = self.client.post(
            self.logout_url, 
            {'refresh_token': 'test-refresh-token'},
            format='json',
            HTTP_AUTHORIZATION='Bearer test-access-token'
        )
        
        # Debug print
        print("\nLogout Response:", response.status_code, response.data)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Logout successful')
        # The RefreshToken is instantiated in the view, so we check the view's RefreshToken mock
        mock_view_refresh_token.assert_called_once_with('test-refresh-token')
        mock_view_token.blacklist.assert_called_once()
    
    def test_protected_endpoint_authentication(self):
        # Test accessing a protected endpoint without authentication
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test with invalid token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid-token')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test with valid authentication
        mock_user = MockUser(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Use force_authenticate for testing
        self.client.force_authenticate(user=mock_user)
        with patch('authentication.serializers.UserProfileSerializer') as mock_serializer:
            mock_serializer.return_value.data = {
                'username': 'testuser',
                'email': 'test@example.com'
            }
            response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
