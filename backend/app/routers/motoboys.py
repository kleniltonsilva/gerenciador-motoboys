# backend/app/routers/motoboys.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, database, auth

router = APIRouter(prefix="/motoboys", tags=["Motoboys"])


@router.post("/", response_model=schemas.MotoboyPublic)
def criar_motoboy(
    motoboy: schemas.MotoboyCreate,
    current_restaurante: models.Restaurante = Depends(auth.get_current_restaurante),
    db: Session = Depends(database.get_db)
):
    """Cadastra motoboy no restaurante logado"""
    # Verifica limite do plano
    limites = {"basico": 3, "medio": 5, "premium": 12}
    limite_max = limites.get(current_restaurante.plano, 3)
    
    count = db.query(models.Motoboy).filter(
        models.Motoboy.tenant_id == current_restaurante.id
    ).count()
    
    if count >= limite_max:
        raise HTTPException(status_code=400, detail=f"Limite do plano '{current_restaurante.plano}' atingido ({limite_max} motoboys)")
    
    novo_motoboy = models.Motoboy(
        tenant_id=current_restaurante.id,  # 🔐 ISOLAMENTO
        nome=motoboy.nome,
        sobrenome=motoboy.sobrenome,
        status="disponivel"
    )
    
    db.add(novo_motoboy)
    db.commit()
    db.refresh(novo_motoboy)
    return novo_motoboy


@router.get("/", response_model=List[schemas.MotoboyPublic])
def listar_motoboys(
    current_restaurante: models.Restaurante = Depends(auth.get_current_restaurante),
    db: Session = Depends(database.get_db)
):
    """Lista motoboys do restaurante logado"""
    motoboys = db.query(models.Motoboy).filter(
        models.Motoboy.tenant_id == current_restaurante.id  # 🔐 FILTRO
    ).all()
    
    return motoboys