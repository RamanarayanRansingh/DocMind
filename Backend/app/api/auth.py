from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from ..models.user import User  
from ..schemas.user import UserCreate, User as UserSchema  
from ..schemas.token import Token
from ..services.auth import AuthService
from ..database import get_db
from ..config import settings
from ..utils.logger import log_info, log_error, log_api_request, log_warning

router = APIRouter(prefix="/api", tags=["Authentication"])

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        # Basic validation
        if (user_data.email == "user@example.com" or user_data.password == "string" 
            or user_data.username == "string" or not user_data.username.strip() 
            or not user_data.email.strip() or not user_data.password.strip()):
            log_warning(f"Invalid registration attempt with email: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All fields are required and must be valid"
            )

        # Check for existing email or username
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        existing_username = db.query(User).filter(User.username == user_data.username).first()

        if existing_email:
            log_warning(f"Registration attempt with existing email: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        if existing_username:
            log_warning(f"Registration attempt with existing username: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Create new user
        hashed_password = AuthService.get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        log_info(f"User registered successfully: {user_data.email}")
        return new_user

    except HTTPException:
        raise
    except Exception as e:
        log_error(e, f"Error during user registration for email: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        log_api_request("POST", "/api/login")
        
        # Authenticate with email (form_data.username contains email)
        user = AuthService.authenticate_user(
            db, 
            email=form_data.username,
            password=form_data.password
        )
        
        if not user:
            log_warning(f"Failed login attempt for email: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": user.email},
            expires_delta=access_token_expires
        )
        
        log_info(f"Successful login for user: {user.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "email": user.email
        }
    
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, f"Error during login for email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/profile", response_model=UserSchema)
async def get_current_user_profile(
    current_user: User = Depends(AuthService.get_current_user)
):
    try:
        log_api_request("GET", "/api/profile", current_user.id)
        log_info(f"Profile retrieved for user: {current_user.email}")
        return current_user  # Returns the authenticated user
    except Exception as e:
        log_error(e, f"Error retrieving profile for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve profile"
        )