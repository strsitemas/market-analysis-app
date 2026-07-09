from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_usuario_atual
from app.core.security import criar_access_token
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import Token, UsuarioCreate, UsuarioRead

router = APIRouter(prefix="/auth", tags=["Autenticacao"])


@router.post("/registrar", response_model=UsuarioRead, status_code=201)
def registrar(usuario_in: UsuarioCreate, db: Session = Depends(get_db)) -> UsuarioRead:
    """Cria uma nova conta de usuario. Retorna 409 se o email ja existir."""
    existente = crud.usuario.get_by_email(db, usuario_in.email)
    if existente:
        raise HTTPException(status_code=409, detail="Este email ja esta cadastrado")
    return crud.usuario.criar(db, usuario_in.email, usuario_in.senha)


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:
    """
    Login. O OAuth2PasswordRequestForm espera dados de formulario
    (nao JSON): campos "username" (aqui, o email) e "password".
    """
    usuario = crud.usuario.autenticar(db, form_data.username, form_data.password)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Email ou senha invalidos")
    access_token = criar_access_token(subject=usuario.email)
    return Token(access_token=access_token)


@router.get("/me", response_model=UsuarioRead)
def me(usuario_atual: Usuario = Depends(get_usuario_atual)) -> UsuarioRead:
    """Retorna os dados do usuario autenticado pelo token atual."""
    return usuario_atual