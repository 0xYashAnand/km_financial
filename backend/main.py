# main.py
import hashlib
import timedelta
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, make_transient
from models.db_session import DBSession
from models.base_md import User
import math
import datetime


import models.request_models as rqm
import models.base_md as bmd
import app.security as su

app = FastAPI()


def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()

def user_is_admin(current_user_email = Depends(su.get_current_user), db: DBSession = Depends(get_db)):
    current_user = db.get_user_by_email(current_user_email)
    if current_user.is_admin == False:
        raise HTTPException(status_code=403, detail="User is not an admin")
    return current_user


def calculate_monthly_payment(loan_amount, interest_rate, loan_term):
    monthly_interest_rate = interest_rate / (12 * 100)
    total_payments = loan_term
    monthly_payment = (loan_amount * monthly_interest_rate) / (1 - math.pow((1 + monthly_interest_rate), -total_payments))
    return monthly_payment


def update_loan_details(loan_id: int, loan_amount: float, annual_interest_rate: float, loan_term: int, db: DBSession = Depends(get_db)):
    loan_details = bmd.LoanDetails(
        loan_id=loan_id,
        loan_amount=loan_amount,
        annual_interest_rate=annual_interest_rate,
        loan_term=loan_term
    )
    db.add_to_session(loan_details)
    db.commit()


@app.post("/signup")
async def signup(user_details: rqm.UserDetails, db: DBSession = Depends(get_db)):
    existing_user = db.get_user_by_phone_or_email(user_details.phone, user_details.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone or email already registered")

    hashed_password = hashlib.sha256(user_details.password.encode("utf-8")).hexdigest()
    new_user = User(name=user_details.name, phone=user_details.phone,  email=user_details.email, password=hashed_password)
    db.add_to_session(new_user)
    db.commit()

    return {"message": "User successfully registered"}


@app.post("/login")
async def login(loginuser : rqm.LoginUser, db: DBSession = Depends(get_db)):
    user = db.get_user_by_email(loginuser.email)
    hashed_password = hashlib.sha256(loginuser.password.encode("utf-8")).hexdigest()
    if user and user.password == hashed_password:
        access_token = su.genrate_jwt_token(user.email)
        access_token = "".join(access_token)
        userdetails = su.get_current_user(access_token)
        response = {
            "access_token": access_token,
            "email": user.email,
            "userdetails": userdetails,
        }
        return response
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/apply-loan")
async def apply_loan(
    loan_data: rqm.LoanApplication,
    current_user_email = Depends(su.get_current_user),
    db: DBSession = Depends(get_db)
):
    user = db.get_user_by_email(current_user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_loan = bmd.Loan(
        user_id=user.id,
        name=user.name, 
        phone=user.phone, 
        email=user.email, 
        loan_amount=loan_data.loan_amount, 
        loan_type=loan_data.loan_type, 
        annual_interest_rate=loan_data.annual_interest_rate, 
        loan_term=loan_data.annual_interest_rate, 
        employment_details=loan_data.employment_details
    )
    db.add_to_session(new_loan)
    db.commit()

    return {"message": "Loan application submitted successfully"}


@app.put("/loan/{loan_id}/approve")
async def approve_loan_application(
    loan_id: int,
    current_user = Depends(user_is_admin),
    db: DBSession = Depends(get_db)
):
    loan_to_approve = db.get_loan_by_id(loan_id)

    if loan_to_approve:
        loan_to_approve.status = "approved"
        db.session.commit()
        db.session.refresh(loan_to_approve)
        update_loan_details(loan_id, loan_to_approve.loan_amount, loan_to_approve.annual_interest_rate, loan_to_approve.loan_term, db)
        return {
            "loan_id": loan_to_approve.id,
            "user_id": loan_to_approve.user_id,
            "status": loan_to_approve.status,
        }
    else:
        raise HTTPException(status_code=404, detail="Loan not found")
    

@app.put("/loan/{loan_id}/reject")
async def reject_loan_application(
    loan_id: int,
    current_user = Depends(user_is_admin),
    db: DBSession = Depends(get_db)
):
    loan_to_reject = db.get_loan_by_id(loan_id)

    if loan_to_reject:
        loan_to_reject.status = "rejected"
        db.session.commit()
        db.session.refresh(loan_to_reject)

        return {
            "loan_id": loan_to_reject.id,
            "user_id": loan_to_reject.user_id,
            "status": loan_to_reject.status,
        }
    else:
        raise HTTPException(status_code=404, detail="Loan not found")


@app.get("/user_profile")
async def get_user_profile(
    current_user_email = Depends(su.get_current_user),
    db: DBSession = Depends(get_db)
    ):
    current_user = db.get_user_by_email(current_user_email)
    return {
        "user_id": current_user.id,
        "name": current_user.name, 
        "email": current_user.email, 
        "phone": current_user.phone,
    }


@app.put("/update_profile")
async def update_user_profile(
    profile_data: rqm.UpdateUserProfile,
    current_user_email=Depends(su.get_current_user),
    db: DBSession = Depends(get_db)
):
    current_user = db.get_user_by_email(current_user_email)

    if current_user:
        if current_user.name is not None:
            current_user.name = profile_data.name
        db.session.commit()
        db.session.refresh(current_user)
        return {
            "user_id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "phone": current_user.phone,
        }
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.get("/loan/history/{user_id}")
async def get_loan_application_history(
    user_id: int,
    current_user_email=Depends(su.get_current_user),
    db: DBSession = Depends(get_db)
):
    current_user = db.get_user_by_email(current_user_email)
    if current_user or current_user.is_admin == True:
        loan_history = db.get_loan_history_by_user(user_id)
        if loan_history:
            return [
                {
                    "loan_id": loan.id,
                    "user_id": loan.user_id,
                    "name": loan.name,
                    "phone": loan.phone,
                    "email": loan.email,
                    "loan_amount": loan.loan_amount,
                    "loan_type": loan.loan_type,
                    "annual_interest_rate" : loan.annual_interest_rate,
                    "loan_term": loan.loan_term, 
                    "employment_details": loan.employment_details,
                    "status": loan.status,
                }
                for loan in loan_history
            ]

    return []


@app.get("/loan/{loan_id}")
async def get_loan_details(
    loan_id: int,
    current_user_email = Depends(su.get_current_user),
    db: DBSession = Depends(get_db)
):
    current_user = db.get_user_by_email(current_user_email)
    loan = db.get_loan_by_id(loan_id)

    if loan or current_user.is_admin == True:
        if loan.user_id == current_user.id or current_user.is_admin == True:
            return {
                "loan_id": loan.id,
                "user_id": loan.user_id,
                "name": loan.name,
                "phone": loan.phone,
                "email": loan.email,
                "loan_amount": loan.loan_amount,
                "loan_type": loan.loan_type,
                "annual_interest_rate" : loan.annual_interest_rate,
                "loan_term": loan.loan_term,
                "employment_details": loan.employment_details,
                "status": loan.status,
            }
        else:
            raise HTTPException(status_code=404, detail="You don't have permission to access this loan.")    

    raise HTTPException(status_code=404, detail="Loan not found")


@app.put("/loan/update/{loan_id}")
async def update_loan_application(
    update_data: rqm.UpdateLoanApplication,
    loan_id: int,
    current_user_email=Depends(su.get_current_user),
    db: DBSession = Depends(get_db)
):
    current_user = db.get_user_by_email(current_user_email)

    loan_to_update = db.get_loan_by_id(loan_id)

    if loan_to_update:
        if update_data.loan_amount is not None:
            loan_to_update.loan_amount = update_data.loan_amount
        if update_data.loan_type is not None:
            loan_to_update.loan_type = update_data.loan_type
        if update_data.employment_details is not None:
            loan_to_update.employment_details = update_data.employment_details
        db.session.commit()
        db.session.refresh(loan_to_update)

        
        return {
            "loan_id": loan_to_update.id,
            "user_id": loan_to_update.user_id,
            "loan_amount": loan_to_update.loan_amount,
            "loan_type": loan_to_update.loan_type,
            "loan_term": loan_to_update.loan_term, 
            "employment_details": loan_to_update.employment_details,
        }
    else:
        raise HTTPException(status_code=404, detail="Loan not found")


def calculate_total_repayment(monthly_payment, loan_term):
    return monthly_payment * loan_term

@app.post("/loan/calculate")
async def calculate_loan(
    loan_details: rqm.LoanCalculationDetails,
    current_user_email = Depends(su.get_current_user)
):
    try:
        monthly_payment = calculate_monthly_payment(loan_details.loan_amount, loan_details.interest_rate, loan_details.loan_term)
        total_repayment = calculate_total_repayment(monthly_payment, loan_details.loan_term)
        return {"monthly_payment": round(monthly_payment, 2), "total_repayment": round(total_repayment, 2)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.get("/loan/{loan_id}/repayment-schedule")
async def get_repayment_schedule(
    loan_id: int,
    current_user_email = Depends(su.get_current_user),
    db: Session = Depends(get_db)
    ):
    loan = db.query(bmd.Loan).filter(bmd.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    principal = loan.loan_amount
    annual_interest_rate = loan.annual_interest_rate / 100 
    loan_term_months = loan.loan_term

    monthly_interest_rate = annual_interest_rate / 12
    total_payments = loan_term_months
    monthly_payment = (principal * monthly_interest_rate) / (1 - (1 + monthly_interest_rate) ** -total_payments)

    repayment_schedule = []
    balance = principal
    for month in range(1, total_payments + 1):
        interest = balance * monthly_interest_rate
        principal_payment = monthly_payment - interest
        balance -= principal_payment
        due_date = datetime.now() + timedelta(days=month*30) 
        repayment_schedule.append({
            "month": month,
            "due_date": due_date.strftime('%Y-%m-%d'),
            "principal": principal_payment,
            "interest": interest,
            "total_payment": monthly_payment,
            "balance": balance
        })

    return {"repayment_schedule": repayment_schedule}