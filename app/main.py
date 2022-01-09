from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor # this gives us the column name
import time

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

# Gets all posts
@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    #print(posts)
    return {"data": posts}

# Creates a new post
@app.post("/posts", status_code=status.HTTP_201_CREATED) #this is the path to the page we want to see
def create_post(post: Post): #this extracts all of the fields from the body and it puts it into a dictionary
    post_dict = post.dict() #regular python dictionary
    post_dict['id'] = randrange(0, 10000000) #this is to make the id random so that it is unique
    my_posts.append(post_dict) # this adds the post to the list
    return {"data": post_dict} # this returns the post that was just added


# Get an individual post
@app.get("/posts/{id}") #this is the path to the page we want to see because the user will give us the id {id} is the path parameter
def get_post(id: int, response: Response): #this is the path parameter
    
    post = find_post(id) #this is to find the post with the id that the user provides
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found") #this is to raise an error if the post is not found

    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    # this is to delete a post
    # 1. Find the index in the array that has required ID
    # 2. my_post.pop(index)
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")

    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Updating
@app.put("/posts/{id}")
def update_post(id:int, post: Post): # Post is for the right schema
    # 1. Find the index in the array that has required ID
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")

    post_dict = post.dict()
    post_dict['id'] = id
    my_posts[index] = post_dict
    return {"data": post_dict}

