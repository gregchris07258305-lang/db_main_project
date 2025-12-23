# setup_db.py
import os
import json
from sqlalchemy.orm import Session

# ★ 핵심: 우리가 만든 프로젝트 파일들에서 가져오기
from database import SessionLocal, engine
from models import Base, Policy 

# 1. 환경 설정 (경로만 필요)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 유틸리티 함수
def normalize_region_name(input_str: str) -> str:
    if not input_str: return "전국"
    if len(input_str) >= 2:
        return input_str[:2]
    return input_str

# 3. 메인 로직
def setup_database():
    print("🚀 [Setup] DB 테이블 생성 및 데이터 적재 시작...")
    
    # 테이블 생성 (models.py에 정의된 내용을 바탕으로 생성)
    Base.metadata.create_all(bind=engine)
    print("✅ [Setup] 테이블(being_test 포함) 생성/확인 완료.")
    
    db = SessionLocal()
    try:
        # 데이터 중복 적재 방지
        if db.query(Policy).first() is None:
            json_path = os.path.join(BASE_DIR, "policies_remake.json")
            
            if os.path.exists(json_path):
                print(f"📦 [Setup] {json_path} 데이터 로드 중...")
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                policies = []
                for item in data:
                    raw_region = item.get("region", "전국")
                    norm_region = normalize_region_name(raw_region)
                    
                    p = Policy(
                        title=item.get("title"),
                        summary=item.get("summary"),
                        period=item.get("period"),
                        link=item.get("link"),
                        genre=item.get("genre"),
                        region=norm_region,
                        original_id=str(item.get("original_id", ""))
                    )
                    policies.append(p)
                
                db.add_all(policies)
                db.commit()
                print(f"✅ [Setup] {len(policies)}개 정책 데이터 적재 완료!")
            else:
                print("⚠️ [Setup] policies_remake.json 파일을 찾을 수 없습니다.")
        else:
            print("ℹ️ [Setup] 데이터가 이미 존재합니다. (Skip)")
            
    except Exception as e:
        print(f"🔥 [Setup] 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_database()