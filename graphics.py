import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Configura la conexión a la base de datos
conn = psycopg2.connect(
    dbname='demanda_padel',
    user='postgres',
    password='1234',
    host='localhost',
    port='5432'
)

# Crea un cursor
cur = conn.cursor()

# Consulta para obtener los datos de disponibilidad y las pistas
query = """
SELECT p.pista_id, c.nombre AS club_nombre, p.nombre AS pista_nombre, 
       d.fecha, d.hora_inicio, d.duracion_horas, d.fecha_hora_consulta
FROM Disponibilidad d
JOIN Pista p ON d.pista_id = p.pista_id
JOIN Club c ON p.club_id = c.club_id;
"""
cur.execute(query)

# Cargar los resultados en un DataFrame
cols = ['pista_id', 'club_nombre', 'pista_nombre', 'fecha', 'hora_inicio', 'duracion_horas', 'fecha_hora_consulta']
data = cur.fetchall()
df = pd.DataFrame(data, columns=cols)

# Cerrar la conexión
cur.close()
conn.close()

# Definir las franjas horarias basadas en las horas de ejecución
def determinar_franja_horaria(hora):
    if 8 <= hora < 10:
        return '9:00'
    elif 11 <= hora < 13:
        return '12:00'
    elif 14 <= hora < 16:
        return '15:00'
    elif 17 <= hora < 19:
        return '18:00'
    else:
        return '21:00'

# Extraer la hora de la consulta y determinar la franja horaria
df['franja_horaria'] = pd.to_datetime(df['fecha_hora_consulta']).dt.hour.apply(determinar_franja_horaria)

# Calcular la tasa de ocupación para cada pista en cada franja horaria
HORAS_TOTALES = 16

df_ocupacion = df.groupby(['club_nombre', 'pista_nombre', 'franja_horaria']).agg(
    horas_ocupadas=('duracion_horas', 'sum')
).reset_index()

df_ocupacion['tasa_ocupacion'] = df_ocupacion['horas_ocupadas'] / HORAS_TOTALES * 100

# Mostrar los resultados
print(df_ocupacion)

# Graficar la tasa de ocupación por franja horaria
plt.figure(figsize=(12, 6))
sns.barplot(x='club_nombre', y='tasa_ocupacion', hue='pista_nombre', data=df_ocupacion)
plt.title('Tasa de ocupación de pistas por club y franja horaria')
plt.ylabel('Tasa de ocupación (%)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# Mostrar el gráfico
plt.show()
