from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from schema import UserLogin, UserRegister
from models import Users
from database import get_session
from sqlmodel import Session, select
from oauth2 import create_access_token, verify_token, create_refresh_token, current_user
from utils import verify, hash

router=APIRouter()

@router.get("/login")
def loginUser(user_credentials:UserLogin, response:Response ,session:Session=Depends(get_session)):
    user=session.exec(select(Users).filter(Users.email==user_credentials.email)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Email Address....")
    if not verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Password")
    access_token = create_access_token(data={"user_id": user.id})
    refresh_token = create_refresh_token(data={"user_id": user.id})
    response.set_cookie(key="accessToken", value=access_token, secure=True, httponly=True)
    response.set_cookie(key="refreshToken", value=refresh_token, secure=True, httponly=True)
    return {"message": "User logged in Successfully..."}

@router.post("/refresh")
def refresh_access_token(response: Response ,refresh_token:str=Cookie(None)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )    
    user_id = verify_token(refresh_token, credentials_exception)
    new_access_token = create_access_token(data={"user_id": user_id})
    response.set_cookie(key="accessToken", value=new_access_token, secure=True, httponly=True)
    return {"Access Token successfully refreshed..."}

@router.post("/register")
def registerUser(user_details: UserRegister, session:Session=Depends(get_session)):
    try:
        print(user_details.name, user_details.email, user_details.password)
        existUser=session.exec(select(Users).where(Users.email==user_details.email)).first()
        print(user_details.name, user_details.email, user_details.password)
        if existUser:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Email Address already Registered...")
        hashedPassword = hash(user_details.password)
        newUser=Users(name=user_details.name, email=user_details.email, password=hashedPassword)
        session.add(newUser)
        session.commit()
        session.refresh(newUser)
        return newUser
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"error": error.detail})
    
@router.get("/me")
def getUserDetails(user=Depends(current_user)):
    return {"message": "You are authenticated!", "user": user}