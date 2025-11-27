# app/api/incidents.py
from fastapi import APIRouter, HTTPException, Query, Depends
from app.models.schemas import IncidentCreate
from app.services.incident_service import registrar_incidente
from app.db.conn import get_db
from app.db.database import get_db as get_sqlalchemy_db
import sqlite3
from app.core.security import get_current_user, require_role, AuthUser
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/registrar")
def registrar(
    data: IncidentCreate, 
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_sqlalchemy_db)
):
    try:
        return registrar_incidente(data, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
def listar_recientes(limit: int = Query(5, ge=1, le=50), user=Depends(get_current_user)):
    """
    Lista los incidentes más recientes (limit por defecto: 5).
    """
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Intentamos leer created_at; si no existe (BD antigua), devolvemos sin esa columna
    try:
        cur.execute(
            """
            SELECT id, cargo_id, vehicle_id, employee_id, type, description, lat, lon, created_at
            FROM incidentes
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    except sqlite3.OperationalError:
        cur.execute(
            """
            SELECT id, cargo_id, vehicle_id, employee_id, type, description, lat, lon
            FROM incidentes
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()
        out = [dict(r) for r in rows]
        for r in out:
            r["created_at"] = None
        return out


@router.delete("/{incidente_id}")
def eliminar_incidente(incidente_id: int, user=Depends(require_role("admin"))):
    """Elimina un incidente por id."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM incidentes WHERE id = ?", (incidente_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(404, detail="Incidente no encontrado")
    return {"deleted": True, "id": incidente_id}
