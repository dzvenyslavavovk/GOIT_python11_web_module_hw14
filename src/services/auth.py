from datetime import datetime, timedelta
from typing import Optional

import redis as redis
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer  # Bearer token
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.database.db import get_db
from src.repository import users as repository_users
from src.conf.config import settings


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def verify_password(self, plain_password, hashed_password):
        """
    The verify_password function takes a plain-text password and hashed
    password as arguments. It then uses the pwd_context object to verify that the
    plain-text password matches the hashed one.

    :param self: Make the method a bound method, which means that it can be called on an instance of the class
    :param plain_password: Pass in the password that is entered by the user
    :param hashed_password: Check if the password is hashed
    :return: A boolean value
    :doc-author: Trelent
    """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
    The get_password_hash function takes a password as input and returns the hash of that password.
    The hash is generated using the pwd_context object, which is an instance of Flask-Bcrypt's Bcrypt class.

    :param self: Represent the instance of the class
    :param password: str: Specify the password that will be hashed
    :return: A hash of the password
    :doc-author: Trelent
    """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
    The create_access_token function creates a new access token.
        Args:
            data (dict): A dictionary containing the claims to be encoded in the JWT.
            expires_delta (Optional[float]): An optional parameter specifying how long, in seconds,
                the access token should last before expiring. If not specified, it defaults to 15 minutes.

    :param self: Represent the instance of the class
    :param data: dict: Pass the data to be encoded in the jwt token
    :param expires_delta: Optional[float]: Specify the time in seconds that the access token will be valid for
    :return: A jwt token that is encoded with the user's data, a timestamp for when it was created and an expiration date
    :doc-author: Trelent
    """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
    The create_refresh_token function creates a refresh token for the user.
        Args:
            data (dict): A dictionary containing the user's id and username.
            expires_delta (Optional[float]): The number of seconds until the token expires, defaults to None.

    :param self: Represent the instance of the class
    :param data: dict: Pass in the user's id and username
    :param expires_delta: Optional[float]: Set the expiration time of the refresh token
    :return: A jwt that contains the user's id,
    :doc-author: Trelent
    """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
    The get_current_user function is a dependency that will be used in the
        protected endpoints. It takes a token as an argument and returns the user
        if it's valid, or raises an exception otherwise.

    :param self: Make the function a method of the class
    :param token: str: Get the token from the authorization header
    :param db: Session: Get the database session
    :return: A user object
    :doc-author: Trelent
    """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("scope") == "access_token":
                email = payload.get("sub")
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user

    async def decode_refresh_token(self, refresh_token: str):
        """
    The decode_refresh_token function is used to decode the refresh token.
    It takes a refresh_token as an argument and returns the email of the user if it's valid.
    If not, it raises an HTTPException with status code 401 (UNAUTHORIZED) and detail 'Could not validate credentials'.


    :param self: Represent the instance of the class
    :param refresh_token: str: Pass in the refresh token that was received from the client
    :return: The email address of the user
    :doc-author: Trelent
    """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    def create_email_token(self, data: dict):
        """
    The create_email_token function takes a dictionary of data and returns a token.
    The token is encoded with the SECRET_KEY, which is stored in the .env file.
    The algorithm used to encode the token is also stored in the .env file.

    :param self: Make the function a method of the class
    :param data: dict: Pass in the data that will be encoded into a jwt
    :return: A token that is encoded with the user's email, a timestamp and an expiration date
    :doc-author: Trelent
    """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    def get_email_from_token(self, token: str):
        """
    The get_email_from_token function takes a token as an argument and returns the email associated with that token.
    It does this by decoding the JWT using our SECRET_KEY and ALGORITHM, then checking to make sure that it has a scope of 'email_token'.
    If so, it returns the email address from the payload's sub field. If not, it raises an HTTPException with status code 401 (Unauthorized)
    and detail message &quot;Invalid scope for token&quot;. If there is any other error in decoding or validating the JWT, we raise another
    HTTPException with status code 422 (Unprocess

    :param self: Represent the instance of the class
    :param token: str: Pass in the token that is sent to the user's email
    :return: The email address associated with the token
    :doc-author: Trelent
    """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'email_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()