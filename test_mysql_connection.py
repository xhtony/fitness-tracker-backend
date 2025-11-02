#!/usr/bin/env python3
"""
测试MySQL数据库连接
"""

import os
import django
from django.conf import settings
from django.db import connection

def test_mysql_connection():
    """测试MySQL数据库连接"""
    
    # 设置Django环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker_backend.settings')
    django.setup()
    
    try:
        # 测试数据库连接
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✅ MySQL连接成功!")
            print(f"MySQL版本: {version[0]}")
            
            # 测试数据库是否存在
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()
            print(f"当前数据库: {current_db[0]}")
            
            # 显示表
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            if tables:
                print("数据库中的表:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("数据库为空（这是正常的，迁移后会有表）")
                
    except Exception as e:
        print(f"❌ MySQL连接失败: {e}")
        print("\n请检查:")
        print("1. MySQL服务器是否正在运行")
        print("2. 数据库配置是否正确")
        print("3. 用户名和密码是否正确")
        return False
    
    return True

if __name__ == "__main__":
    print("HealthTrack MySQL连接测试")
    print("=" * 40)
    test_mysql_connection()







