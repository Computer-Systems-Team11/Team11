# FastAPI: FastAPI 애플리케이션을 만들고, HTTP 예외를 처리하고, 의존성을 주입하기 위한 라이브러리.
# Pydantic: 데이터 검증 및 설정 관리를 위한 라이브러리.
# SQLAlchemy: 데이터베이스 ORM(Object Relational Mapping) 라이브러리.
# Datetime: 날짜 및 시간 관리를 위한 라이브러리.
# asynccontextmanager: 비동기 컨텍스트 관리자를 위한 라이브러리.
from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import datetime
from contextlib import asynccontextmanager

# DATABASE_URL: 데이터베이스 연결 문자열. 여기서는 SQLite 데이터베이스 파일을 사용.
# Base: SQLAlchemy의 기본 클래스로, 모든 모델 클래스는 이 클래스를 상속받아 정의.
# engine: 데이터베이스와의 연결을 관리하는 SQLAlchemy 엔진.
# SessionLocal: 데이터베이스 세션을 관리하는 클래스.

# 데이터베이스 URL 설정 (필요에 따라 경로 변경 가능)
DATABASE_URL = "sqlite:///./test.db"

# 데이터베이스 설정
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Submission: 제출된 데이터를 저장할 데이터베이스 모델.
# id: 기본 키로 사용되는 고유 ID.
# username: 사용자의 이름.
# password: 사용자의 비밀번호.
# created_at: 제출된 시각.
# updated_at: 마지막으로 갱신된 시각.
# status: 제출 상태, 기본값은 "SUBMITTED".
# Base.metadata.create_all(bind=engine): 데이터베이스 테이블을 생성.


class Submission(Base):
    __tablename__ = "submission"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    status = Column(String, default="SUBMITTED")

Base.metadata.create_all(bind=engine)

# SubmissionCreate: 제출된 데이터를 검증하는 Pydantic 모델.
# username: 사용자의 이름.
# password: 사용자의 비밀번호.
# code: 제출된 코드.

# Pydantic 모델
class SubmissionCreate(BaseModel):
    username: str
    password: str
    code: str

# lifespan: 애플리케이션의 시작과 종료 시 실행되는 비동기 컨텍스트 관리자.
#비동기 작업=프로그램이 다른 작업을 기다리지 않고 여러 작업을 처리할수 있는방법
#비동기 컨텍스트는 비동기 작업을 설정하고 정리하는데 사용되는 도구
# print("Application startup"): 애플리케이션 시작 시 메시지 출력.
# yield: 애플리케이션이 실행되는 동안의 컨텍스트.
# print("Application shutdown"): 애플리케이션 종료 시 메시지 출력.

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup")
    yield
    print("Application shutdown")

# app: FastAPI 애플리케이션 인스턴스.
# lifespan: 애플리케이션 수명 주기 이벤트 핸들러로 지정.

# FastAPI 앱 생성
app = FastAPI(lifespan=lifespan)

# get_db: 데이터베이스 세션을 생성하고, 요청이 끝난 후 세션을 닫는 함수. 의존성 주입에 사용

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# @app.post("/submit"): POST 요청을 처리하는 엔드포인트.
# create_submission: 제출된 데이터를 처리하는 함수.
# submission: 요청 본문에서 검증된 데이터를 받음.
# db: 데이터베이스 세션을 의존성 주입으로 받음.
# HTTPException: 필수 필드가 누락된 경우 400 오류 반환.
# db_submission: 데이터베이스에 새로운 제출 데이터 저장.
# code_file.write(submission.code): 제출된 코드를 파일로 저장.
# return: 제출 ID를 포함한 응답 반환.

@app.post("/submit", status_code=200)
async def create_submission(submission: SubmissionCreate, db: Session = Depends(get_db)):
    if not submission.username or not submission.password or not submission.code:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # 데이터베이스에 제출 저장
    db_submission = Submission(
        username=submission.username,
        password=submission.password
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)

    # 코드 파일로 저장
    with open(f"codes/{db_submission.id}.py", "w") as code_file:
        code_file.write(submission.code)

    return {"reservation_id": db_submission.id}

# custom_404_handler: 404 오류를 처리하는 함수.
# custom_500_handler: 500 오류를 처리하는 함수.

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    return {"error": "Not Found"}

@app.exception_handler(500)
async def custom_500_handler(request: Request, exc: HTTPException):
    return {"error": "Internal Server Error"}

# uvicorn.run: Uvicorn을 사용하여 애플리케이션을 실행.
# host="0.0.0.0": 모든 IP 주소에서 접근 가능하도록 설정.
# port=8000: 8000 포트에서 애플리케이션 실행.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)