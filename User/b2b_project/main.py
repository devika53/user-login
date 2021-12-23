from fastapi import FastAPI,status,Depends,HTTPException
from db.database import SessionLocal
from db import models

import schemas
from typing import List
from pydantic import BaseModel
from auth.jwt_handler import signJWT
from auth.jwt_bearer import JWTBearer
from auth.jwt_handler import decodeJWT


app=FastAPI()

db=SessionLocal()

#To signup a user
@app.post('/signup', response_model=schemas.User)
def create_user(userone:schemas.User):
    user_signup=db.query(models.User_data).filter(models.User_data.email == userone.email).first()
    try:
        if user_signup is None:
            new_user=models.User_data(
                email=userone.email,
                username=userone.username,
                password=userone.password
            )
            db.add(new_user)
            db.commit()
            return  new_user
    except Exception:
        raise HTTPException(
                            409,
                            detail="email already taken and user exists",
                        )

# to login a user
@app.post('/login')
def login(user:schemas.UserLogin):
    user_login=db.query(models.User_data).filter(models.User_data.username == user.username and models.User_data.password == user.password).first()
    if user_login is not None:
        return signJWT(user.username)

# add items only for authenticated users
@app.post('/item', dependencies=[Depends(JWTBearer())], response_model=schemas.Item)
def create_item(item:schemas.Item):
    new_item=models.Item(
        id=item.id,
        item_name=item.item_name,
        item_description=item.item_description
    )
    db.add(new_item)
    db.commit()
    return  new_item

# to get the current_user
@app.get('/user/{token}')
def get_current_user(token):
    current_user = decodeJWT(token)
    return current_user

#get all users
@app.get('/users')
def get_users():
    items=db.query(models.User_data).all()
    return items


