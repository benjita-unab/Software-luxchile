import sqlite3

print("\n" + "="*80)
print("  LIMPIEZA DE DATOS PREDEFINIDOS")
print("="*80)

# Base de datos operacional (incidentes)
conn = sqlite3.connect("/app/data/inventario.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Ver incidentes antes de eliminar
print("\n🚨 INCIDENTES ANTES DE ELIMINAR:")
cur.execute("SELECT * FROM incidentes")
incidentes_antes = cur.fetchall()
print(f"  Total: {len(incidentes_antes)}")
for inc in incidentes_antes:
    print(f"    - ID {inc['id']}: Carga {inc['cargo_id']}, RUT {inc['employee_id']}, Tipo {inc['type']}")

# Eliminar todos los incidentes
cur.execute("DELETE FROM incidentes")
conn.commit()

# Verificar que se eliminaron
cur.execute("SELECT COUNT(*) as total FROM incidentes")
total = cur.fetchone()['total']

print(f"\n✅ RESULTADO:")
print(f"  Incidentes eliminados: {len(incidentes_antes)}")
print(f"  Incidentes restantes: {total}")

# Reiniciar el autoincrement
cur.execute("DELETE FROM sqlite_sequence WHERE name='incidentes'")
conn.commit()

conn.close()
print("\n" + "="*80 + "\n")
