from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from db import Base

# Tabla intermedia para misiones aceptadas
personaje_misiones = Table(
    'personaje_misiones', Base.metadata,
    Column('personaje_id', Integer, ForeignKey('personajes.id')),
    Column('mision_id', Integer, ForeignKey('misiones.id'))
)

class Personaje(Base):
    __tablename__ = "personajes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    xp = Column(Integer, default=0)
    misiones = relationship("Mision", secondary=personaje_misiones)

class Mision(Base):
    __tablename__ = "misiones"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    recompensa_xp = Column(Integer)
