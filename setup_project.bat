@echo off
echo Setting up HealthTrack Fitness Tracker Application...
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Running Django migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo Creating superuser (optional - you can skip this)...
python manage.py createsuperuser

echo.
echo Setting up React frontend...
cd fitness-tracker-frontend
npm install
cd ..

echo.
echo Setup complete! 
echo.
echo To start the application:
echo 1. Run start_backend.bat to start the Django server
echo 2. Run start_frontend.bat to start the React server
echo.
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:3000
echo.
pause
