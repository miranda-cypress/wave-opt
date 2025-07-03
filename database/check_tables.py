#!/usr/bin/env python3
import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        port=5433,
        database='warehouse_opt',
        user='wave_user',
        password='wave_password'
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cursor.fetchall()
    
    print('Existing tables:')
    for table in tables:
        print(f'  {table[0]}')
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}") 