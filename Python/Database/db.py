import pymysql, os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return pymysql.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME'),
        port=int(os.environ.get('DB_PORT')),
    )
    
if __name__ == "__main__":
    try:
        conn = get_connection()
        print("[✅] Connection successful to the database.")
        conn.close()
    except Exception as e:
        print(f"[❌] Error connecting to the database: {e}")
