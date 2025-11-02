#!/usr/bin/env python3
"""
MySQL数据库设置脚本
在运行Django迁移之前，请先运行此脚本创建数据库
"""

import mysql.connector
from mysql.connector import Error
import sys

def create_database():
    """创建MySQL数据库"""
    
    # 数据库配置 - 请根据您的MySQL设置修改这些值
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'your_mysql_password',  # 请修改为您的MySQL密码
        'port': 3306
    }
    
    database_name = 'healthtrack_db'
    
    try:
        # 连接到MySQL服务器
        print(f"正在连接到MySQL服务器...")
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 检查数据库是否已存在
            cursor.execute(f"SHOW DATABASES LIKE '{database_name}'")
            result = cursor.fetchone()
            
            if result:
                print(f"数据库 '{database_name}' 已存在")
            else:
                # 创建数据库
                cursor.execute(f"CREATE DATABASE {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print(f"数据库 '{database_name}' 创建成功")
            
            # 显示所有数据库
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print("当前MySQL服务器上的数据库:")
            for db in databases:
                print(f"  - {db[0]}")
                
    except Error as e:
        print(f"MySQL错误: {e}")
        print("\n请检查:")
        print("1. MySQL服务器是否正在运行")
        print("2. 用户名和密码是否正确")
        print("3. 是否有权限创建数据库")
        return False
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL连接已关闭")
    
    return True

def main():
    print("HealthTrack MySQL数据库设置")
    print("=" * 40)
    
    print("\n在运行此脚本之前，请确保:")
    print("1. MySQL服务器已安装并正在运行")
    print("2. 您知道MySQL的root密码")
    print("3. 已修改此脚本中的密码配置")
    
    response = input("\n是否继续? (y/n): ")
    if response.lower() != 'y':
        print("操作已取消")
        return
    
    if create_database():
        print("\n✅ 数据库设置完成!")
        print("\n下一步:")
        print("1. 安装Python依赖: pip install -r requirements.txt")
        print("2. 运行Django迁移: python manage.py makemigrations")
        print("3. 应用迁移: python manage.py migrate")
        print("4. 创建超级用户: python manage.py createsuperuser")
    else:
        print("\n❌ 数据库设置失败")
        sys.exit(1)

if __name__ == "__main__":
    main()







