from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

from src.database.db import db
from src.services.auth_service import AuthService
from src.services.finance_service import FinanceService
from src.services.goal_service import GoalService
from src.services.report_service import ReportService


app = FastAPI(title="Flujo API", version="1.0.0")


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TransactionRequest(BaseModel):
    user_id: int
    amount: float
    trans_type: str
    category: str
    description: str = ""
    currency: str = "COP"
    transaction_date: Optional[str] = None


@app.on_event("startup")
def on_startup():
    db.init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/register")
def register(data: RegisterRequest):
    valid, message = AuthService.validate_password_strength(data.password)
    if not valid:
        raise HTTPException(status_code=400, detail=message)

    user_id = AuthService.register_user(data.username, data.password, data.email)
    if not user_id:
        raise HTTPException(status_code=409, detail="Usuario o email ya existe")

    return {"user_id": user_id, "message": "Usuario registrado"}


@app.post("/auth/login")
def login(data: LoginRequest):
    user = AuthService.login(data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {"user": user.to_dict()}


@app.get("/finance/summary/{user_id}")
def finance_summary(user_id: int):
    summary = ReportService.get_financial_summary(user_id)
    goals = GoalService.get_total_goals_progress(user_id)
    return {"summary": summary, "goals": goals}


@app.post("/finance/transactions")
def create_transaction(data: TransactionRequest):
    tx_id = FinanceService.create_transaction(
        user_id=data.user_id,
        amount=data.amount,
        trans_type=data.trans_type,
        category=data.category,
        description=data.description,
        currency=data.currency,
        transaction_date=data.transaction_date or date.today().isoformat(),
    )

    if not tx_id:
        raise HTTPException(status_code=400, detail="No se pudo crear la transacción")

    return {"transaction_id": tx_id}


@app.get("/finance/transactions/{user_id}")
def list_transactions(user_id: int, start_date: str, end_date: str):
    tx = FinanceService.get_transactions_by_date_range(user_id, start_date, end_date)
    return {"items": [t.to_dict() for t in tx]}
