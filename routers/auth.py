from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from database import get_db
from models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

# 1. 비밀번호 암호화 도구 설정
# 기존 bcrypt 부분을 지우거나 주석 처리하고 아래처럼 바꾸세요
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# 2. 데이터 검증용 스키마 (Pydantic)
class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    region: str | None = None # 선택사항

class UserLogin(BaseModel):
    email: str
    password: str

# 3. [회원가입 API]
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # 이미 가입된 이메일인지 확인
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")
    
    # 비밀번호 암호화 (보안 필수!)
    hashed_password = pwd_context.hash(user.password)
    
    # DB 저장
    new_user = User(
        email=user.email,
        password=hashed_password,
        name=user.name,
        region=user.region,
        provider="local"  # 직접 가입이므로 local
    )
    db.add(new_user)
    db.commit()
    
    return {"message": "회원가입 성공", "email": new_user.email}

# 4. [로그인 API]
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # 이메일로 사용자 찾기
    db_user = db.query(User).filter(User.email == user.email).first()
    
    if not db_user:
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 틀립니다.")
    
    # 소셜 로그인 사용자인지 체크
    if db_user.provider != "local":
        raise HTTPException(status_code=400, detail=f"{db_user.provider} 계정으로 로그인해주세요.")

    # 비밀번호 확인 (암호화된 것끼리 비교)
    if not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 틀립니다.")
    
    # 로그인 성공! (실무에선 여기서 토큰을 발급하지만, 일단 성공 메시지와 유저 정보 반환)
    return {
        "message": "로그인 성공",
        "user": {
            "email": db_user.email,
            "name": db_user.name,
            "region": db_user.region
        }
    }