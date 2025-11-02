# HealthTrack - Fitness Tracker Application

A comprehensive web-based fitness tracker application built with Django (backend) and React.js (frontend) for HealthTrack Ltd.

## Features

- **User Authentication**: Secure user registration and login with JWT tokens
- **Activity Management**: Create, read, update, and delete daily activities
- **Activity Types**: Support for workouts, meals, steps, sleep, hydration, and custom activities
- **Status Tracking**: Track activity status (planned, in progress, completed, cancelled)
- **Activity Logging**: Automatic logging of status changes with timestamps
- **Dashboard**: Comprehensive overview with statistics and recent activities
- **Search & Filter**: Search activities by title/description and filter by type/status
- **Bulk Operations**: Bulk update status for multiple activities
- **Responsive Design**: Modern, mobile-friendly UI built with Material-UI

## Technology Stack

### Backend
- **Django 4.2.7**: Web framework
- **Django REST Framework**: API development
- **JWT Authentication**: Secure token-based authentication
- **SQLite**: Database (easily configurable for production)
- **CORS**: Cross-origin resource sharing for frontend integration

### Frontend
- **React 18**: User interface library
- **TypeScript**: Type-safe JavaScript
- **Material-UI**: Modern React components
- **React Router**: Client-side routing
- **Axios**: HTTP client for API communication
- **Context API**: State management for authentication

## Project Structure

```
├── fitness_tracker_backend/          # Django backend
│   ├── authentication/               # User authentication app
│   ├── activities/                   # Activities management app
│   └── fitness_tracker_backend/      # Main Django project
├── fitness-tracker-frontend/         # React frontend
│   ├── src/
│   │   ├── components/               # Reusable components
│   │   ├── contexts/                 # React contexts
│   │   ├── pages/                    # Page components
│   │   ├── services/                 # API services
│   │   └── types/                    # TypeScript type definitions
│   └── public/
├── requirements.txt                  # Python dependencies
└── README.md
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run database migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create a superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

4. **Start the Django development server:**
   ```bash
   python manage.py runserver
   ```
   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd fitness-tracker-frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the React development server:**
   ```bash
   npm start
   ```
   The frontend will be available at `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get user profile
- `PATCH /api/auth/profile/` - Update user profile
- `GET /api/auth/dashboard/` - Get dashboard data

### Activities
- `GET /api/activities/` - List activities (with filtering and search)
- `POST /api/activities/` - Create new activity
- `GET /api/activities/{id}/` - Get specific activity
- `PATCH /api/activities/{id}/` - Update activity
- `DELETE /api/activities/{id}/` - Delete activity
- `GET /api/activities/stats/` - Get activity statistics
- `POST /api/activities/bulk-update/` - Bulk update activity status
- `GET /api/activities/recent/` - Get recent activities

## Usage

1. **Registration/Login**: Create an account or log in with existing credentials
2. **Dashboard**: View your activity statistics and recent activities
3. **Activities**: 
   - Create new activities with details like type, duration, calories, etc.
   - Search and filter activities
   - Update activity status (planned → in progress → completed)
   - Bulk update multiple activities
   - Delete unwanted activities
4. **Profile**: Update your personal information

## Activity Types

- **Workout**: Exercise and fitness activities
- **Meal**: Food and nutrition tracking
- **Steps**: Step counting and walking activities
- **Sleep**: Sleep tracking and rest periods
- **Hydration**: Water and fluid intake
- **Other**: Custom activities

## Activity Statuses

- **Planned**: Activity is scheduled for the future
- **In Progress**: Activity is currently being performed
- **Completed**: Activity has been finished
- **Cancelled**: Activity has been cancelled

## Development

### Backend Development
- The Django backend uses Django REST Framework for API development
- JWT tokens are used for authentication
- CORS is configured to allow frontend requests
- Admin interface is available at `/admin/` for database management

### Frontend Development
- React components are built with TypeScript for type safety
- Material-UI provides consistent, modern design
- Context API manages authentication state
- Axios handles API communication with automatic token refresh

## Production Deployment

### Backend
- Configure a production database (PostgreSQL recommended)
- Set up proper environment variables
- Use a production WSGI server (Gunicorn)
- Configure static file serving
- Set up SSL/HTTPS

### Frontend
- Build the React app: `npm run build`
- Serve static files through a web server (Nginx, Apache)
- Configure environment variables for API endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is developed for HealthTrack Ltd. All rights reserved.

## Support

For support or questions, please contact the development team.








