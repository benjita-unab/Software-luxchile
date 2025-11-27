import sqlite3
import os

print("\n" + "="*80)
print("  VERIFICACIÓN Y LIMPIEZA DE INCIDENTES")
print("="*80)

db_path = "/app/data/inventario.db"
print(f"\n📂 Base de datos: {db_path}")
print(f"   Existe: {os.path.exists(db_path)}")

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Listar todas las tablas
print("\n📋 TABLAS EN LA BASE DE DATOS:")
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
for table in tables:
    print(f"  - {table['name']}")

# Si existe la tabla incidentes, limpiarla
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='incidentes'")
if cur.fetchone():
    print("\n🚨 INCIDENTES ACTUALES:")
    cur.execute("SELECT * FROM incidentes")
    incidentes = cur.fetchall()
    
    if incidentes:
        print(f"  Total: {len(incidentes)}")
        for inc in incidentes:
            print(f"    - ID {inc['id']}: Carga {inc['cargo_id']}, RUT {inc['employee_id']}, Tipo {inc['type']}")
        
        # Eliminar todos
        cur.execute("DELETE FROM incidentes")
        cur.execute("DELETE FROM sqlite_sequence WHERE name='incidentes'")
        conn.commit()
        print("\n✅ Todos los incidentes han sido eliminados")
    else:
        print("  ✅ No hay incidentes registrados (tabla vacía)")
else:
    print("\n⚠️  La tabla 'incidentes' aún no existe (se creará al registrar el primer incidente)")

conn.close()
print("\n" + "="*80 + "\n")
