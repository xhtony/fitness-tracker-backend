import psycopg2
from django.conf import settings

def drop_test_db():
    # Get database settings
    db = settings.DATABASES['default']
    
    # Connect to postgres database to drop the test database
    conn = psycopg2.connect(
        dbname='postgres',
        user=db['USER'],
        password=db['PASSWORD'],
        host=db['HOST'],
        port=db['PORT']
    )
    conn.autocommit = True
    
    # Drop all connections to the test database
    with conn.cursor() as cur:
        cur.execute("""
            SELECT pg_terminate_backend(pid) 
            FROM pg_stat_activity 
            WHERE datname = %s AND pid <> pg_backend_pid()
        """, (db['TEST']['NAME'],))
        
        # Drop the test database
        cur.execute(f'DROP DATABASE IF EXISTS "{db["TEST"]["NAME"]}"')
    
    print(f"Successfully dropped test database: {db['TEST']['NAME']}")

if __name__ == '__main__':
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker_backend.settings')
    django.setup()
    drop_test_db()
