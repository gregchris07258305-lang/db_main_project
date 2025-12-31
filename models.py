from sqlalchemy import Column, Integer, Text, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# 1. 정책 테이블 (기존)
class Policy(Base):
    __tablename__ = "being_test"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    summary = Column(Text)
    period = Column(Text)
    link = Column(Text)
    genre = Column(Text)
    region = Column(Text)
    original_id = Column(Text)

# 2. 사용자 테이블 (신규)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 여기서 String을 사용하기 때문에 맨 위 import에 String이 꼭 있어야 합니다.
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=True)
    region = Column(String, nullable=True)
    provider = Column(String, default="local", nullable=True)
    
    # [NEW] 유료 멤버십 등급 (free / premium)
    subscription_level = Column(String, default="free")

    # [NEW] 관계 설정 (유저가 지워지면 행동 로그도 지워짐)
    # [NEW] 관계 설정 (User.email <-> UserAction.user_email)
    actions = relationship("UserAction", back_populates="user", cascade="all, delete", foreign_keys="UserAction.user_email")

# 3. 유저 행동 로그 테이블 (PM님 스키마인 'users_action'에 맞춤)
class UserAction(Base):
    __tablename__ = "users_action"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 1. user_id 대신 user_email 사용
    user_email = Column(String, ForeignKey("users.email"))
    
    # 2. policy_id (동일)
    policy_id = Column(Integer, ForeignKey("being_test.id"))
    
    # 3. action_type -> type
    type = Column(String, nullable=False)
    
    # 4. timestamp -> created_at
    created_at = Column(DateTime, default=datetime.now)

    # Relationship (Join condition 명시)
    user = relationship("User", back_populates="actions", foreign_keys=[user_email])
    