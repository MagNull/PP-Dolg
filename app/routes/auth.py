from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Employer
from app.schemas import UserCreate, UserResponse, Token

# настройки JWT
SECRET_KEY = "секретный-ключ-для-jwt"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 часа

# хеширование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# схема OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login", auto_error=False
)

router = APIRouter(prefix="/api/auth", tags=["Авторизация"])


# создаём JWT токен
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# получаем текущего пользователя из токена
def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # декодируем токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # ищем пользователя в базе
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user


def get_current_user_optional(
    token: str = Depends(oauth2_scheme_optional), db: Session = Depends(get_db)
):
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        user_id = int(user_id)
    except (JWTError, ValueError, TypeError):
        return None

    return db.query(User).filter(User.id == user_id).first()


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # проверяем что email не занят
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email уже зарегистрирован"
        )

    # хешируем пароль
    hashed_password = pwd_context.hash(user_data.password)

    # создаём пользователя
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        name=user_data.name,
        role=user_data.role,
        faculty_id=user_data.faculty_id,
    )
    db.add(new_user)
    db.flush()

    # если работодатель — создаём профиль компании
    if user_data.role == "employer":
        company = user_data.company_name or user_data.name
        employer = Employer(user_id=new_user.id, company_name=company)
        db.add(employer)

    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    # ищем по email (username = email в форме)
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # проверяем пароль
    if not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # создаём токен
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    # получаем employer_id если пользователь работодатель
    employer_id = None
    if current_user.role == "employer" and current_user.employer:
        employer_id = current_user.employer.id

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        faculty_id=current_user.faculty_id,
        created_at=current_user.created_at,
        employer_id=employer_id,
    )
