from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_usuario_atual
from app.core.config import settings
from app.core.limiter import limiter
from app.core.security import criar_access_token
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import Token, UsuarioCreate, UsuarioRead

router = APIRouter(prefix="/auth", tags=["Autenticacao"])

COOKIE_NAME = "access_token"


def _definir_cookie_token(response: Response, token: str) -> None:
    """
    Grava o JWT num cookie httpOnly. JavaScript no navegador nao
    consegue ler esse cookie (mitiga roubo de token via XSS). O
    middleware do Next.js consegue le-lo, por rodar no servidor/edge.

    Em producao, backend (Render) e frontend (Vercel) ficam em
    dominios diferentes -- isso exige SameSite=None (cookie
    cross-site), que por sua vez so e aceito pelo navegador se
    Secure=True (HTTPS). Em dev, mesmo dominio logico (localhost),
    entao usamos Lax + Secure=False, que funciona sem HTTPS local.
    """
    producao = settings.app_env != "development"
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=producao,
        samesite="none" if producao else "lax",
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


@router.post("/registrar", response_model=UsuarioRead, status_code=201)
@limiter.limit("5/minute")
def registrar(
    request: Request, usuario_in: UsuarioCreate, db: Session = Depends(get_db)
) -> UsuarioRead:
    """Cria uma nova conta de usuario. Retorna 409 se o email ja existir."""
    existente = crud.usuario.get_by_email(db, usuario_in.email)
    if existente:
        raise HTTPException(status_code=409, detail="Este email ja esta cadastrado")
    return crud.usuario.criar(db, usuario_in.email, usuario_in.senha)


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """
    Login. Alem de retornar o token no corpo (compatibilidade com
    Swagger/testes), grava o mesmo token num cookie httpOnly -- e esse
    cookie que o frontend passa a usar de fato.
    """
    usuario = crud.usuario.autenticar(db, form_data.username, form_data.password)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Email ou senha invalidos")
    access_token = criar_access_token(subject=usuario.email)
    _definir_cookie_token(response, access_token)
    return Token(access_token=access_token)


@router.post("/logout", status_code=204)
def logout(response: Response) -> None:
    """Remove o cookie de sessao. Chamado pelo botao 'Sair' no frontend."""
    response.delete_cookie(key=COOKIE_NAME, path="/")


@router.get("/me", response_model=UsuarioRead)
def me(usuario_atual: Usuario = Depends(get_usuario_atual)) -> UsuarioRead:
    """Retorna os dados do usuario autenticado pelo token atual."""
    return usuario_atual