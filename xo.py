import time
from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import models,database,CRUD,schemas

from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=database.engine)
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/users/", response_model=list[schemas.User])
async def get_all_users(db: Session = Depends(get_db)):
    return CRUD.get_users(db)
@app.get("/users/top", response_model=list[schemas.User])
async def get_all_users(db: Session = Depends(get_db),limit: int | None = None):
    return CRUD.get_top_users(db,limit)
@app.get("/users/{name}")
async def get_user(name: str, db: Session = Depends(get_db)):
    return CRUD.get_user(db, name)
@app.post("/users/")
async def add_user(user : schemas.UserCreate, db : Session = Depends(get_db)):
    past_user = CRUD.get_user(db, user.name)
    if past_user :
        raise HTTPException(403,"the user already exists")
    else:
        new_user = CRUD.create_user(db,user)
        return new_user   
     

@app.post("/users/changeScore")
async def change_user_score(items : List[schemas.Item], db: Session = Depends(get_db)):
    newItems = []
    for item in items:
        past_user = CRUD.get_user(db, item.name)
        if item.status == "Lose":
                if past_user:
                    newItems.append(CRUD.change_user_score(db, item.name, -1))
                else:    
                    user = models.User(name= item.name, score=0)
                    newItems.append( CRUD.create_user(db, user=user))
                    
        elif item.status == "Win":
                if past_user:
                    newItems.append( CRUD.change_user_score(db, item.name, 1))
                else:
                    user = models.User(name= item.name, score=1)
                    newItems.append( CRUD.create_user(db, user=user))
    for item in newItems:
        item.score += 0 
        pass    
    
    return newItems                