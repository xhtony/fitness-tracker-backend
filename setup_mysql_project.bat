@echo off
echo Setting up HealthTrack Fitness Tracker Application with MySQL...
echo.

echo ========================================
echo 步骤 1: 安装Python依赖
echo ========================================
pip install -r requirements.txt

echo.
echo ========================================
echo 步骤 2: 设置MySQL数据库
echo ========================================
echo 请确保MySQL服务器正在运行，并且您知道root密码
echo 运行MySQL数据库设置脚本...
python setup_mysql.py

echo.
echo ========================================
echo 步骤 3: 运行Django迁移
echo ========================================
python manage.py makemigrations
python manage.py migrate

echo.
echo ========================================
echo 步骤 4: 创建超级用户（可选）
echo ========================================
echo 您可以选择跳过此步骤
python manage.py createsuperuser

echo.
echo ========================================
echo 步骤 5: 设置React前端
echo ========================================
cd fitness-tracker-frontend
npm install
cd ..

echo.
echo ========================================
echo 设置完成!
echo ========================================
echo.
echo 要启动应用程序:
echo 1. 运行 start_backend.bat 启动Django服务器
echo 2. 运行 start_frontend.bat 启动React服务器
echo.
echo 后端将在以下地址可用: http://localhost:8000
echo 前端将在以下地址可用: http://localhost:3000
echo.
echo 数据库信息:
echo - 类型: MySQL
echo - 数据库名: healthtrack_db
echo - 主机: localhost:3306
echo.
pause







