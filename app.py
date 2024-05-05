import fastapi
import fastapi as _fastapi
import fastapi.security as _security
import sqlalchemy.orm as _orm
import schemas as _schemas
import services as _services
from typing import List

app = _fastapi.FastAPI()


@app.post("/api/v1/users")
async def register_user(
        user: _schemas.UserRequest,
        db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    # call to check if user with email exists
    db_user = await _services.getUserByEmail(email=user.email,
                                             db=db)
    # if user found through exception
    if db_user:
        raise _fastapi.HTTPException(status_code=400, detail="Email already exist, try with another email")

    # create the user and return a token
    db_user = await _services.create_user(user=user, db=db)
    return await _services.create_token(user=db_user)


@app.post("/api/v1/login")
async def login_user(
        form_data: _security.OAuth2PasswordRequestForm = fastapi.Depends(),
        db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    db_user = await _services.login(email=form_data.username,
                                    password=form_data.password,
                                    db=db)
    # invalid login then throw exception
    if not db_user:
        raise _fastapi.HTTPException(status_code=401, detail="wrong login credentials")
    # create and return the token
    return await _services.create_token(user=db_user)


@app.get('/api/v1/users/current', response_model=_schemas.UserResponse)
async def current_user(user: _schemas.UserResponse = _fastapi.Depends(_services.current_user)):
    return user


@app.post("/api/v1/posts", response_model=_schemas.PostResponse)
async def create_post(
        postRequest: _schemas.PostRequest,
        user: _schemas.UserResponse = _fastapi.Depends(_services.current_user),
        db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    return await _services.create_post(user=user, db=db, post=postRequest)


@app.get("/api/v1/posts/user", response_model=List[_schemas.PostResponse])
async def get_posts_by_user(
        user: _schemas.UserResponse = _fastapi.Depends(_services.current_user),
        db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    return await _services.get_post_by_user(user=user, db=db)


@app.get("/api/v1/posts/{post_id}/", response_model=_schemas.PostResponse)
async def get_post_detail(
        post_id: int,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    post = await _services.get_post_detail(post_id=post_id, db=db)
    return post


@app.delete("/api/v1/posts/{post_id}/")
async def delete_post(
        post_id: int,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        user: _schemas.UserResponse = _fastapi.Depends(_services.current_user),

):
    post = await _services.get_post_detail(post_id=post_id, db=db)
    await _services.delete_post(post=post, db=db)
    return "POST deleted successfully"


@app.put("/api/v1/posts/{post_id}", response_model=_schemas.PostResponse)
async def update_post(
        post_id: int,
        post_request: _schemas.PostRequest,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        user: _schemas.UserResponse = _fastapi.Depends(_services.current_user),
):
    db_post = await _services.get_post_detail(post_id=post_id, db=db)
    return await _services.update_post(post_request=post_request, post=db_post, db=db)


@app.get("/api/v1/posts/all", response_model=List[_schemas.PostResponse])
async def get_posts_by_all(
        db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    return await _services.get_post_by_all(db=db)


@app.get("/api/v1/users/{user_id}", response_model=_schemas.UserResponse)
async def get_user_data(
        user_id: int,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    user = await _services.get_user_detail(user_id=user_id, db=db)
    return user


"""

uvicorn app:app --reload


{
"email": "pouria.f8410@gmail.com",
"name": "pouria far",
"phone": "112233",
"password" : "secret"
}


"""
