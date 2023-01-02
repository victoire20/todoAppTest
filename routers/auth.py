import sys
sys.path.append("..")

from starlette import status
from starlette.responses import RedirectResponse, Response

from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Request, Form
from pydantic import BaseModel
from typing import Optional
import models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

templates = Jinja2Templates(directory="templates")


class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str
    phone_number: Optional[str]


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}}
)


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(
        username: str,
        user_id: int,
        expires_delta: Optional[timedelta] = None
):
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


# async def get_current_user(request: Request, token: str = Depends(oauth2_bearer)):
async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            # raise get_user_exception()
            # return None
            logout(request)
        return {"username": username, "id": user_id}
    except JWTError:
        # raise get_user_exception()
        return None


@router.post("/create/user")
async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):
    create_user_model = models.Users()
    create_user_model.email = create_user.email
    create_user_model.username = create_user.username
    create_user_model.first_name = create_user.first_name
    create_user_model.last_name = create_user.last_name
    create_user_model.phone_number = create_user.phone_number

    hash_password = get_password_hash(password=create_user.password)

    create_user_model.hashed_password = hash_password
    create_user_model.is_active = True

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    return create_user_model


@router.post("/token")
async def login_for_access_token(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    print(form_data.username)
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        # raise token_exception()
        return False
    token_expires = timedelta(minutes=20)
    token = create_access_token(user.username, user.id, expires_delta=token_expires)

    response.set_cookie(key="access_token", value=token, httponly=True)

    # return {"token": token}
    return True


@router.get("/", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)
        if not validate_user_cookie:
            msg = "Incorrect Username or Password"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
        return response
    except HTTPException:
        msg = "Unknown Error"
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


@router.get("/logout")
async def logout(request: Request):
    msg = "Logout Successful"
    response = templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    response.delete_cookie(key="access_token")
    return response


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, email: str = Form(...), username: str = Form(...),
                        first_name: str = Form(...), last_name: str = Form(...),
                        password: str = Form(...), password2: str = Form(...),
                        db: Session = Depends(get_db)
):
    validation1 = db.query(models.Users).filter(models.Users.username == username).first()

    validation2 = db.query(models.Users).filter(models.Users.email == email).first()

    if password != password2 or validation1 is not None or validation2 is not None:
        msg = "Invalid registration request"
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})

    user_model = models.Users()
    user_model.username = username
    user_model.email = email
    user_model.first_name = first_name
    user_model.last_name = last_name

    hash_password = get_password_hash(password)
    user_model.hashed_password = hash_password
    user_model.is_active = True

    db.add(user_model)
    db.commit()

    msg = "User successfully created"
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


# Exceptions
def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception


def token_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token_exception_response
