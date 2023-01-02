import sys
sys.path.append('...')

from starlette import status
from starlette.responses import RedirectResponse

from fastapi import Depends, APIRouter, HTTPException, status, Form, Request
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
from pydantic import BaseModel
from .auth import get_current_user, get_user_exception, verify_password, get_password_hash

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.get('/', response_class=HTMLResponse)
async def get_user(request: Request, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse('user.html', {"request": request, "user": user})


@router.post('/update-user')
async def update_user(
    request: Request, 
    username: str = Form(...),
    password: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    msg_class = "warning"
    
    if password == new_password:
        msg = "Dont use same password !"
        return templates.TemplateResponse('user.html', {"request": request, "user": user, "msg": msg, "msg_class": msg_class})
    
    hash_password = get_password_hash(new_password)
    current_user = db.query(models.Users).filter(models.Users.id == user.get('id')).first()
    
    if not verify_password(password, current_user.hashed_password):
        msg = "Current password is not correct !"
        return templates.TemplateResponse('user.html', {"request": request, "user": user, "msg": msg, "msg_class": msg_class})
    
    current_user.username = username
    current_user.password = hash_password
    
    db.commit()
    db.refresh(current_user)
    
    msg = "The password is successfuly updated !"
    response = templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    response.delete_cookie(key="access_token")
    return response
    