from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor # this gives us the column name
import time
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()




class Post(BaseModel):
    #these are the fields that are required
    title: str
    content: str
    published: bool = True # this is for if the user does not provide a published value
    rating: Optional[int] = None # this is for if the user does not provide a rating value

while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='password123', cursor_factory=RealDictCursor)
        cursor = conn.cursor() # this is used to execute sql statements
        print('Database connection established')
        break
    except Exception as error:
        print('Database connection failed')
        print("Error: ", error)
        time.sleep(2)




#my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
#{"title": "favorite foods", "content": "I like pizza", "id": 2}] #this contains all the posts saved in the memory and not in a database

def find_post(id): #this function finds the post with the id that the user provides
    for p in my_posts:
        if p["id"] == id:
            return p

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i # this returns the index of the post

# Decotrator that refrences the url we want it to go to
@app.get("/")
def root():
    return {"message": "Welcome to my API!!!"}

# For testing porpuses to see the connection to sqlalchemy
@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    return {"status": "success"}



# Gets all posts
@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts;""")
    posts = cursor.fetchall()
    #print(posts)
    return {"data": posts}

# Creates a new post
@app.post("/posts", status_code=status.HTTP_201_CREATED) #this is the path to the page we want to see
def create_post(post: Post): #this extracts all of the fields from the body and it puts it into a dictionary
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * ;""", (post.title, post.content, post.published))
    new_post = cursor.fetchone()

    conn.commit() # when we add posts we need to commit the changes
    return {"data": new_post} # this returns the post that was just added


# Get an individual post
@app.get("/posts/{id}") #this is the path to the page we want to see because the user will give us the id {id} is the path parameter
def get_post(id: int, response: Response): #this is the path parameter
    cursor.execute("""SELECT * FROM posts WHERE id = %s;""", (str(id),))
    post = cursor.fetchone()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found") #this is to raise an error if the post is not found

    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    # this is to delete a post
    # 1. Find the index in the array that has required ID
    # 2. my_post.pop(index)
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * ;""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Updating
@app.put("/posts/{id}")
def update_post(id:int, post: Post): # Post is for the right schema
    # 1. Find the index in the array that has required ID
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * ;""", (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")

    return {"data": updated_post}

