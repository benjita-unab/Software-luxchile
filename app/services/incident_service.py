# app/services/incident_service.py
from app.db.conn import get_db
from app.models.schemas import IncidentCreate
from app.db.database import get_db as get_sqlalchemy_db
from app.models.users import User
from fastapi import HTTPException
from sqlalchemy.orm import Session

def _ensure_table(cur):
    # Crea la tabla si no existe (demo simple)
    # Incluye created_at para compatibilidad con init_db
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS incidentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cargo_id TEXT,
            vehicle_id TEXT,
            employee_id TEXT,
            type TEXT,
            description TEXT,
            lat REAL,
            lon REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

def registrar_incidente(data: IncidentCreate, db: Session) -> dict:
    """
    Inserta un incidente y retorna el registro creado.
    Valida que el RUT del empleado exista en la base de datos.
    """
    # VALIDACIÓN: Verificar que el RUT exista en la tabla users
    rut_normalizado = data.employee_id.strip().upper()
    user = db.query(User).filter(User.rut == rut_normalizado).first()
    
    if not user:
        raise HTTPException(
            status_code=400,
            detail=f"El RUT {rut_normalizado} no está registrado en el sistema. Solo los usuarios registrados pueden reportar incidentes."
        )
    
    # Verificar que el usuario esté activo
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail=f"El usuario con RUT {rut_normalizado} está inactivo y no puede registrar incidentes."
        )
    
    conn = get_db()
    cur = conn.cursor()
    _ensure_table(cur)

    cur.execute("""
        INSERT INTO incidentes (cargo_id, vehicle_id, employee_id, type, description, lat, lon)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data.cargo_id,
        data.vehicle_id,
        rut_normalizado,  # Usar el RUT normalizado
        data.type,
        data.description,
        data.location.lat,
        data.location.lon
    ))
    conn.commit()
    new_id = cur.lastrowid

    # Devuelve el registro recién creado
    cur.execute("SELECT id, cargo_id, vehicle_id, employee_id, type, description, lat, lon FROM incidentes WHERE id = ?", (new_id,))
    row = cur.fetchone()
    conn.close()

    return {
        "id": row["id"],
        "cargo_id": row["cargo_id"],
        "vehicle_id": row["vehicle_id"],
        "employee_id": row["employee_id"],
        "type": row["type"],
        "description": row["description"],
        "location": {"lat": row["lat"], "lon": row["lon"]},
        "status": "ok",
        "validated": True  # Indicador de que pasó la validación
    }
