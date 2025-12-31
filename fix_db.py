from database import engine
from sqlalchemy import text

def fix_schema():
    with engine.connect() as conn:
        print("Checking users table...")
        try:
            # 1. users 테이블에 subscription_level 컬럼 추가
            # IF NOT EXISTS 구문은 PostgreSQL에서 컬럼 추가에는 기본적으로 지원하지 않으므로,
            # 예외 처리를 하거나 확인 후 추가해야 함. 여기서는 심플하게 시도하고 에러나면 무시(이미 있음).
            print("Attempting to add 'subscription_level' column to 'users' table...")
            conn.execute(text("ALTER TABLE users ADD COLUMN subscription_level VARCHAR DEFAULT 'free'"))
            conn.commit()
            print("Successfully added 'subscription_level' column.")
        except Exception as e:
            print(f"Column might already exist or other error: {e}")
            
        print("Schema fix process completed.")

if __name__ == "__main__":
    fix_schema()
