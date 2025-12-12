from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.models.presupuesto import Presupuesto

def check_pending_values():
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # Buscar un presupuesto pendiente
        presupuesto = session.query(Presupuesto).filter(
            Presupuesto.pre_vbgg == 0,
            Presupuesto.Pre_vbLib == 1
        ).first()

        if presupuesto:
            print(f"Encontrado Presupuesto Nro: {presupuesto.pre_nro}")
            print(f"pre_vbgg: {presupuesto.pre_vbgg}")
            print(f"pre_vbggUsu: '{presupuesto.pre_vbggUsu}'")
            print(f"pre_vbggDt: {presupuesto.pre_vbggDt}")
            print(f"pre_vbggTime: '{presupuesto.pre_vbggTime}'")
        else:
            print("No se encontraron presupuestos pendientes para analizar.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    check_pending_values()
