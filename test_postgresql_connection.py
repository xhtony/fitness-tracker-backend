#!/usr/bin/env python3
"""
测试 PostgreSQL 数据库连接
"""

import os
import sys

def test_postgresql_connection():
    """测试 PostgreSQL 数据库连接"""
    
    # 检查是否安装了 psycopg2
    try:
        import psycopg2
        print("✅ psycopg2 已安装")
    except ImportError:
        print("❌ psycopg2 未安装")
        print("请运行: pip install psycopg2-binary")
        return False
    
    # 设置Django环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker_backend.settings')
    
    try:
        import django
        django.setup()
        
        from django.db import connection
        
        # 测试数据库连接
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            print(f"✅ PostgreSQL 连接成功!")
            print(f"PostgreSQL 版本: {version[0]}")
            
            # 测试数据库名称
            cursor.execute("SELECT current_database()")
            current_db = cursor.fetchone()
            print(f"当前数据库: {current_db[0]}")
            
            # 显示表
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = cursor.fetchall()
            if tables:
                print("数据库中的表:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("数据库为空（这是正常的，迁移后会有表）")
                
    except Exception as e:
        print(f"❌ PostgreSQL 连接失败: {e}")
        print("\n请检查:")
        print("1. PostgreSQL 服务器是否可访问")
        print("2. .env 文件中的数据库配置是否正确")
        print("3. 数据库是否存在")
        print("4. 用户名和密码是否正确")
        print("5. 网络连接是否正常")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("HealthTrack PostgreSQL 连接测试")
    print("=" * 50)
    print()
    
    if test_postgresql_connection():
        print()
        print("=" * 50)
        print("✅ 测试完成!")
        print("=" * 50)
        sys.exit(0)
    else:
        print()
        print("=" * 50)
        print("❌ 测试失败")
        print("=" * 50)
        sys.exit(1)

