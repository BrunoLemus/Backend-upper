from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://upper:2SoYBr1Oot4GC2ZQvhhTu9uNaOZtyux4@dpg-d3rtr663jp1c73eglgu0-a.oregon-postgres.render.com/bd_etiqueta_upper"



# Para MySQL NO se necesita check_same_thread
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()

# 5️⃣ Dependencia para FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
