from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Base, Personaje, Mision
from db import SessionLocal, engine
from cola import Cola

Base.metadata.create_all(bind=engine)
app = FastAPI()
colas_personaje = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/personajes")
def crear_personaje(nombre: str, db: Session = Depends(get_db)):
    nuevo = Personaje(nombre=nombre)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    colas_personaje[nuevo.id] = Cola()
    return nuevo

@app.post("/misiones")
def crear_mision(nombre: str, recompensa_xp: int, db: Session = Depends(get_db)):
    nueva = Mision(nombre=nombre, recompensa_xp=recompensa_xp)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@app.post("/personajes/{id_personaje}/misiones/{id_mision}")
def aceptar_mision(id_personaje: int, id_mision: int, db: Session = Depends(get_db)):
    mision = db.query(Mision).get(id_mision)
    if not mision:
        raise HTTPException(status_code=404, detail="Misión no encontrada")
    colas_personaje[id_personaje].enqueue(mision)
    return {"mensaje": "Misión aceptada"}

@app.post("/personajes/{id_personaje}/completar")
def completar_mision(id_personaje: int, db: Session = Depends(get_db)):
    personaje = db.query(Personaje).get(id_personaje)
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    if colas_personaje[id_personaje].is_empty():
        return {"mensaje": "No hay misiones"}
    mision = colas_personaje[id_personaje].dequeue()
    personaje.xp += mision.recompensa_xp
    db.commit()
    return {"mensaje": f"Misión completada: {mision.nombre}", "xp_ganada": mision.recompensa_xp}

@app.get("/personajes/{id_personaje}/misiones")
def listar_misiones(id_personaje: int):
    if id_personaje not in colas_personaje:
        raise HTTPException(status_code=404, detail="Personaje no tiene misiones")
    return colas_personaje[id_personaje].to_list()
