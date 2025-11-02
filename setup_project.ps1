Write-Host "Setting up HealthTrack Fitness Tracker Application..." -ForegroundColor Green
Write-Host ""

Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "Running Django migrations..." -ForegroundColor Yellow
python manage.py makemigrations
python manage.py migrate

Write-Host ""
Write-Host "Creating superuser (optional - you can skip this)..." -ForegroundColor Yellow
python manage.py createsuperuser

Write-Host ""
Write-Host "Setting up React frontend..." -ForegroundColor Yellow
Set-Location fitness-tracker-frontend
npm install
Set-Location ..

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Cyan
Write-Host "1. Run start_backend.bat to start the Django server"
Write-Host "2. Run start_frontend.bat to start the React server"
Write-Host ""
Write-Host "Backend will be available at: http://localhost:8000"
Write-Host "Frontend will be available at: http://localhost:3000"
Write-Host ""
Read-Host "Press Enter to continue"







