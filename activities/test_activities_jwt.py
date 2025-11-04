from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient, APIRequestFactory, force_authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, MagicMock, PropertyMock, ANY
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Q

# Import the models and views we're testing
from activities.models import Activity, ActivityLog
from activities.views import ActivityListCreateView, ActivityDetailView, activity_stats, recent_activities

# Get the User model
User = get_user_model()

class ActivityAPITest(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set up the client with JWT authentication
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Create some test activities
        self.now = timezone.now()
        self.activities = [
            Activity.objects.create(
                title='Morning Workout',
                activity_type='workout',
                status='completed',
                planned_date=self.now - timedelta(days=1),
                duration_minutes=30,
                calories_burned=300,
                user=self.user
            ),
            Activity.objects.create(
                title='Evening Run',
                activity_type='running',
                status='completed',
                planned_date=self.now - timedelta(days=2),
                duration_minutes=45,
                calories_burned=400,
                user=self.user
            ),
            Activity.objects.create(
                title='Yoga Session',
                activity_type='yoga',
                status='pending',
                planned_date=self.now + timedelta(days=1),
                duration_minutes=60,
                calories_burned=200,
                user=self.user
            ),
        ]
        
        # Create activity logs
        self.activity_logs = [
            ActivityLog.objects.create(
                activity=activity,
                old_status='planned',
                new_status=activity.status,
                notes=f'Activity {activity.title} was created with status {activity.status}'
            ) for activity in self.activities
        ]

    def test_activity_creation(self):
        """Test creating a new activity."""
        data = {
            'title': 'New Workout',
            'activity_type': 'workout',
            'status': 'planned',
            'planned_date': (self.now + timedelta(days=2)).isoformat(),
            'duration_minutes': 45,
            'calories_burned': 350,
        }
        
        # Include JWT token in the request
        response = self.client.post(
            '/api/activities/', 
            data, 
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Activity.objects.count(), 4)
        self.assertEqual(Activity.objects.latest('id').title, 'New Workout')

    def test_activity_list(self):
        """Test listing all activities."""
        response = self.client.get(
            '/api/activities/',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if we have pagination in the response
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        
        # Check if we got the expected number of activities
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(len(response.data['results']), 3)  # Using pagination
        
        # Check if the activities are ordered by created_at (descending)
        dates = [item['created_at'] for item in response.data['results']]
        self.assertTrue(dates == sorted(dates, reverse=True))

    def test_activity_detail(self):
        """Test retrieving a single activity."""
        activity = self.activities[0]
        response = self.client.get(
            f'/api/activities/{activity.id}/',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], activity.title)
        self.assertEqual(response.data['activity_type'], activity.activity_type)

    def test_activity_update(self):
        """Test updating an activity."""
        activity = self.activities[0]
        data = {
            'title': 'Updated Workout',
            'activity_type': 'workout',
            'status': 'completed',
            'planned_date': activity.planned_date.isoformat(),
            'duration_minutes': 60,
            'calories_burned': 450,
        }
        
        response = self.client.put(
            f'/api/activities/{activity.id}/',
            data,
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        activity.refresh_from_db()
        self.assertEqual(activity.title, 'Updated Workout')
        self.assertEqual(activity.duration_minutes, 60)
        self.assertEqual(activity.calories_burned, 450)
        
        # Verify the activity log was created
        log = activity.logs.last()
        self.assertEqual(log.old_status, 'planned')
        self.assertEqual(log.new_status, 'completed')

    def test_activity_delete(self):
        """Test deleting an activity."""
        activity = self.activities[0]
        response = self.client.delete(
            f'/api/activities/{activity.id}/',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Activity.objects.count(), 2)
        self.assertFalse(Activity.objects.filter(id=activity.id).exists())

    def test_activity_stats(self):
        """Test getting activity statistics."""
        response = self.client.get(
            '/api/activities/stats/',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if the response contains the expected stats
        self.assertIn('monthly_stats', response.data)
        self.assertIn('totals', response.data)
        self.assertIn('activities_by_type', response.data)
        
        # Verify the stats values
        monthly_stats = response.data['monthly_stats']
        totals = response.data['totals']
        
        self.assertEqual(monthly_stats['total_activities'], 3)
        self.assertEqual(monthly_stats['completed_activities'], 2)
        self.assertEqual(totals['calories_burned'], 900)  # 300 + 400 + 200
        self.assertEqual(totals['duration_minutes'], 135)  # 30 + 45 + 60
        self.assertIn('workout', response.data['activities_by_type'])



@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework_simplejwt.authentication.JWTAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_FILTER_BACKENDS': [
            'django_filters.rest_framework.DjangoFilterBackend',
            'rest_framework.filters.SearchFilter',
            'rest_framework.filters.OrderingFilter',
        ],
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 10,
        'TEST_REQUEST_DEFAULT_FORMAT': 'json'
    }
)
class ActivityFilterTest(APITestCase):
    """Test cases for Activity filtering functionality."""
    
    def setUp(self):
        """Set up test data and client."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set up the client with JWT authentication
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Create test activities with different dates
        self.now = timezone.now()
        self.activities = [
            Activity.objects.create(
                title='Morning Workout',
                activity_type='workout',
                status='completed',
                planned_date=self.now,
                duration_minutes=30,
                calories_burned=300,
                user=self.user
            ),
            Activity.objects.create(
                title='Evening Run',
                activity_type='running',
                status='completed',
                planned_date=self.now - timedelta(days=1),
                duration_minutes=45,
                calories_burned=400,
                user=self.user
            ),
            Activity.objects.create(
                title='Yoga Session',
                activity_type='yoga',
                status='pending',
                planned_date=self.now + timedelta(days=1),
                duration_minutes=60,
                calories_burned=200,
                user=self.user
            ),
            Activity.objects.create(
                title='Swimming',
                activity_type='swimming',
                status='completed',
                planned_date=self.now - timedelta(days=2),
                duration_minutes=30,
                calories_burned=250,
                user=self.user
            ),
            Activity.objects.create(
                title='Cycling',
                activity_type='cycling',
                status='in_progress',
                planned_date=self.now,
                duration_minutes=60,
                calories_burned=500,
                user=self.user
            ),
        ]
    

    
    def test_search_activity(self):
        """Test searching activities by title."""
        response = self.client.get(
            '/api/activities/?search=workout',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Morning Workout')
        
        response = self.client.get(
            '/api/activities/?search=run',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Evening Run')
    

    def test_ordering_activities(self):
        """Test ordering of activities by planned date."""
        response = self.client.get(
            '/api/activities/?ordering=planned_date',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Check if activities are ordered by planned_date (ascending)
        dates = [item['planned_date'] for item in response.data['results']]
        self.assertEqual(dates, sorted(dates))
    
    def test_combined_filters(self):
        """Test combining multiple filters."""
        # Filter by activity_type and status
        response = self.client.get(
            '/api/activities/?activity_type=workout&status=completed',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['activity_type'], 'workout')
        self.assertEqual(response.data['results'][0]['status'], 'completed')
        
        # Filter by search and status
        response = self.client.get(
            '/api/activities/?search=run&status=completed',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Evening Run')
        self.assertEqual(response.data['results'][0]['status'], 'completed')
    

    
    def test_ordering_activities_desc(self):
        """Test ordering activities in descending order."""
        response = self.client.get(
            '/api/activities/?ordering=-planned_date',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Check if activities are ordered by planned_date (descending)
        dates = [item['planned_date'] for item in response.data['results']]
        self.assertEqual(dates, sorted(dates, reverse=True))
    
    def tearDown(self):
        """Clean up after each test."""
        Activity.objects.all().delete()
        User.objects.all().delete()
