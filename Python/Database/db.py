import pymysql

def get_connection():
    return pymysql.connect(
        # Production
        host='172.16.100.93',
        user='root',
        password='',
        database='scott_database',
        port=3306,
    )
    
if __name__ == "__main__":
    try:
        conn = get_connection()
        print("[✅] Connection successful to the database.")
        conn.close()
    except Exception as e:
        print(f"[❌] Error connecting to the database: {e}")