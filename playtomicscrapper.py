from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import psycopg2
from datetime import datetime, timedelta
import os
import logging

# Configuración de logs
log_dir = "C:\\personal\\4-Proyectos\\10_Pistas_Padel\\01_Analisis_Demanda\\Scrapp\\logs"  # Especifica la ruta donde se guardarán los logs
if not os.path.exists(log_dir):
    os.makedirs(log_dir)  # Crear el directorio si no existe

# Crear un nombre de archivo de log único con un timestamp
log_filename = os.path.join(log_dir, datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log")

# Configurar el logger
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',  # Cada línea tendrá un timestamp
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Ejemplo de cómo usar los logs en tu código
logging.info("Inicio del procesamiento")


# Función para obtener pistas según el club_id
def obtener_pistas_por_club(conn, club_id):
    cur = conn.cursor()
    
    logging.info("Obteniendo las pistas del club")
    # Consulta SQL para obtener las pistas de un club específico
    query = "SELECT pista_id FROM pista WHERE club_id = %s ORDER BY pista_id ASC;"
    
    # Ejecutar la consulta
    cur.execute(query, (club_id,))
    
    # Obtener todos los resultados
    pistas = cur.fetchall()

    return pistas

# Configura la conexión a la base de datos
conn = psycopg2.connect(
    dbname='demanda_padel',
    user='postgres',
    password='1234',
    host='localhost',  # o la dirección de tu servidor
    port='5432'        # puerto por defecto de PostgreSQL
)

# Crea un cursor
cur = conn.cursor()

logging.info("Consultando todos los clubs definidos en la tabla")
# Consulta para obtener todos los registros de la tabla Club
cur.execute("SELECT club_id, nombre, url_consulta FROM Club;")

# Obtener todos los resultados de la consulta
clubs = cur.fetchall()

# Mostrar los resultados
for club in clubs:
    club_id, nombre, url_consulta = club
    logging.info(f"Club ID: {club_id}, Nombre: {nombre}, URL de Consulta: {url_consulta}")

    # Obtener la fecha actual
    fecha_actual = datetime.now()

    # Bucle para generar las 15 fechas a partir de la actual
    for day in range(15):
        fecha_formateada = fecha_actual.strftime('%Y-%m-%d')

        # Imprimir la fecha
        logging.info("Procesando datos para la fecha: " + fecha_formateada)

        url_consulta_actualizada = url_consulta.replace("yyyy-MM-dd", fecha_formateada)
        logging.info('Consultando: ' + url_consulta_actualizada)

        # Obtener las pistas para el club actual
        pistas = obtener_pistas_por_club(conn, club_id)


        # Es posible que la página cargue parte de su contenido dinámicamente mediante JavaScript (como es común en aplicaciones web modernas). 
        # En estos casos, el contenido se genera después de que la página se carga, y una solicitud requests.get() no puede capturar esa dinámica.
        # Para solucionar este problema, puedes usar una herramienta que simule completamente un navegador, como Selenium, que ejecuta JavaScript 
        # y renderiza la página como lo haría un navegador real.

        # Configurar opciones de Chrome para Selenium
        chrome_options = Options()
        #chrome_options.add_argument("--headless")  # Ejecutar en modo headless (sin abrir el navegador)
        #chrome_options.add_argument("--start-minimized")  # Para 
        chrome_options.add_argument("--start-maximized")  # Maximizar la ventana del navegador

        # Ruta al ChromeDriver
        chrome_driver_path = "C:\\chromedriver\\chromedriver.exe"

        # Inicializar el navegador con Selenium
        service = Service(executable_path=chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Navegar a la página deseada
        driver.get(url_consulta_actualizada)

        # Esperar unos segundos para permitir que el contenido dinámico cargue
        time.sleep(5)  # Ajusta el tiempo según lo necesario


        # Extraer las horas disponibles
        hours_elements = driver.find_elements(By.CLASS_NAME, "bbq2__hour")
        hours = [int(hour.text) for hour in hours_elements]

        # Extraer las franjas de ocupación y disponibilidad de cada pista
        slots_resources = driver.find_elements(By.CLASS_NAME, "bbq2__slots-resource")

        # Almacenar disponibilidad por pista
        pistas_disponibilidad = []

        # Procesar cada pista
        for resource in slots_resources:
            slots = resource.find_elements(By.CLASS_NAME, "bbq2__slot")
            holes = resource.find_elements(By.CLASS_NAME, "bbq2__hole")
            
            disponibilidad_pista = []

            # Procesar slots (disponibles)
            for slot in slots:
                left = int(slot.get_attribute('style').split('left: ')[1].split('px')[0])  # Obtener el left en px
                width = int(slot.get_attribute('style').split('width: ')[1].split('px')[0])  # Obtener el width en px
                
                # Calcular la hora de inicio y duración
                inicio_hora = 7 + (left // 40)  # Hora base a las 7h
                inicio_minutos = (left % 40) * 1.5  # Ajuste para minutos
                inicio_total = inicio_hora + (inicio_minutos / 60)  # Hora total en decimal

                duracion_horas = width / 40  # Duración en horas (si width es 60px, esto dará 1.5)

                disponibilidad_pista.append((inicio_total, duracion_horas, "Disponible"))

            # Procesar holes (ocupados)
            for hole in holes:
                left = int(hole.get_attribute('style').split('left: ')[1].split('px')[0])  # Obtener el left en px
                width = int(hole.get_attribute('style').split('width: ')[1].split('px')[0])  # Obtener el width en px
                
                # Calcular la hora de inicio y duración
                inicio_hora = 7 + (left // 40)  # Hora base a las 7h
                inicio_minutos = (left % 40) * 1.5  # Ajuste para minutos
                inicio_total = inicio_hora + (inicio_minutos / 60)  # Hora total en decimal

                duracion_horas = width / 40  # Duración en horas (si width es 60px, esto dará 1.5)

                disponibilidad_pista.append((inicio_total, duracion_horas, "Ocupado"))


            # Almacenar las franjas de esta pista
            pistas_disponibilidad.append(disponibilidad_pista)

        # Mostrar la disponibilidad de cada pista
        for i, pista in enumerate(pistas_disponibilidad):
            logging.info(f"Pista {i+1}:")
            for franja in pista:
                hora_inicio = int(franja[0])  # Obtener la parte entera para la hora
                minutos_inicio = int((franja[0] - hora_inicio) * 60)  # Convertir la parte decimal a minutos
                duracion = franja[1]

                logging.info(f"   Hora inicio: {hora_inicio}:{minutos_inicio:02d}h, Duración: {duracion} horas, Estado: {franja[2]}")

                # Insertar solo las franjas ocupadas
                if franja[2] == "Ocupado":
                    # Convertir la hora de inicio a formato decimal
                    hora_inicio_decimal = hora_inicio + (minutos_inicio / 60)
                    
                    # Inserta la disponibilidad en la tabla
                    cur.execute("""
                        INSERT INTO Disponibilidad (pista_id, fecha_hora_consulta, fecha, hora_inicio, duracion_horas)
                        VALUES (%s, %s, %s, %s, %s);
                    """, (int(pistas[i][0]), datetime.now(), fecha_formateada, hora_inicio_decimal, duracion))


        # Confirmar la transacción
        conn.commit()

        # Sumar 'i' días a la fecha actual
        fecha_actual = fecha_actual + timedelta(days=1)
        



# Cerrar el cursor y la conexión
cur.close()
conn.close()

logging.info("Franjas ocupadas insertadas correctamente.")


# Cerrar el navegador
driver.quit()

