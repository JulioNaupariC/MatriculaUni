"""
Sistema de Logging Completo - Arquitectura Orientada a Servicios
Implementa TODOS los atributos del PDF del Laboratorio Semana 11

Atributos implementados:
✅ %(asctime)s - Timestamp en ISO 8601 UTC
✅ %(levelname)s - Nivel (INFO, WARN, ERROR, DEBUG)
✅ %(name)s - Nombre del logger/módulo
✅ %(filename)s - Archivo fuente
✅ %(funcName)s - Función que generó el log
✅ %(lineno)d - Número de línea
✅ %(process)d - PID del proceso
✅ %(thread)d - Thread ID
✅ %(message)s - Mensaje del log
✅ Transaction ID - ID único por request
✅ IP Cliente - Con soporte X-Forwarded-For
✅ Método HTTP - GET, POST, PUT, DELETE
✅ URI - Path completo
✅ Tiempo de procesamiento - En milisegundos
"""

import os
import logging
import time
import uuid
from datetime import datetime, timezone
from flask import request, g
from functools import wraps

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
BASE_LOG_DIR = os.path.abspath(BASE_LOG_DIR)

# Crear directorio de logs si no existe
os.makedirs(BASE_LOG_DIR, exist_ok=True)

# Diccionario para almacenar tiempos de inicio de requests
tiempos_inicio = {}


def generar_transaction_id():
    """
    Genera un ID único de transacción para rastrear requests entre servicios.
    Formato: TXN-YYYYMMDDHHMMSS-UUID8
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique = str(uuid.uuid4())[:8]
    return f"TXN-{timestamp}-{unique}"


def obtener_request_id():
    """
    Obtiene o crea un ID único para la request actual.
    Este ID permite rastrear una solicitud completa a través del sistema.
    """
    if not hasattr(g, 'request_id'):
        # Generar ID único: UUID + timestamp
        g.request_id = f"REQ-{uuid.uuid4().hex[:8]}-{int(time.time() * 1000) % 1000000}"
    return g.request_id


def obtener_ip_cliente():
    """
    Obtiene la IP del cliente manejando proxies (X-Forwarded-For).
    Buena práctica según el PDF.
    """
    try:
        if request:
            # Manejar X-Forwarded-For para proxies
            ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if ip and ',' in ip:
                # Tomar la primera IP si hay múltiples
                ip = ip.split(',')[0].strip()
            return ip
        return "UNKNOWN"
    except:
        return "CLI"


def obtener_datos_request():
    """
    Extrae metadatos relevantes de la request actual.
    """
    try:
        if request:
            return {
                "metodo": request.method,
                "uri": request.path,
                "ip": obtener_ip_cliente(),
                "request_id": obtener_request_id()
            }
        return {
            "metodo": "CLI",
            "uri": "/",
            "ip": "SYSTEM",
            "request_id": "SYSTEM"
        }
    except:
        return {
            "metodo": "UNKNOWN",
            "uri": "/",
            "ip": "UNKNOWN",
            "request_id": "UNKNOWN"
        }


def registrar_log(modulo: str, nivel: str, mensaje: str, **kwargs):
    """
    Registra un log con TODOS los metadatos requeridos por el PDF.
    
    Args:
        modulo: Nombre del módulo/servicio (ej: "alumnos", "cursos")
        nivel: Nivel del log (INFO, WARN, ERROR, DEBUG)
        mensaje: Mensaje descriptivo del evento
        **kwargs: Datos adicionales opcionales
    
    Formato del log:
    [TIMESTAMP] [NIVEL] [REQUEST_ID] [MODULO] [FILENAME:LINENO] [FUNC]
    [PID:123] [THREAD:456] [IP:127.0.0.1] [GET /api/alumnos] [DURACION] MENSAJE
    """
    
    # Obtener datos de la request
    request_data = obtener_datos_request()
    
    # Timestamp ISO 8601 UTC
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    
    # Obtener información del caller (archivo, línea, función)
    import inspect
    frame = inspect.currentframe()
    caller_frame = frame.f_back
    caller_filename = os.path.basename(caller_frame.f_code.co_filename)
    caller_lineno = caller_frame.f_lineno
    caller_function = caller_frame.f_code.co_name
    
    # PID y Thread ID
    pid = os.getpid()
    import threading
    thread_id = threading.get_ident()
    
    # Calcular duración si existe
    duracion_str = ""
    request_id = request_data["request_id"]
    if request_id in tiempos_inicio:
        duracion = (time.time() - tiempos_inicio[request_id]) * 1000
        duracion_str = f"[{duracion:.2f}ms]"
    
    # Construir línea de log con TODOS los metadatos
    linea_log = (
        f"[{timestamp}] "
        f"[{nivel:5}] "
        f"[{request_data['request_id']}] "
        f"[{modulo:15}] "
        f"[{caller_filename}:{caller_lineno:3}] "
        f"[{caller_function:20}] "
        f"[PID:{pid}] "
        f"[Thread:{thread_id}] "
        f"[IP:{request_data['ip']:15}] "
        f"[{request_data['metodo']:6} {request_data['uri']:40}] "
        f"{duracion_str:12} "
        f"→ {mensaje}\n"
    )
    
    # Guardar en archivo del módulo
    ruta_modulo = os.path.join(BASE_LOG_DIR, modulo)
    os.makedirs(ruta_modulo, exist_ok=True)
    ruta_log = os.path.join(ruta_modulo, f"{modulo}.log")
    
    with open(ruta_log, "a", encoding="utf-8") as file:
        file.write(linea_log)
    
    # Guardar en log centralizado
    log_centralizado = os.path.join(BASE_LOG_DIR, "sistema_completo.log")
    with open(log_centralizado, "a", encoding="utf-8") as file:
        file.write(linea_log)


def iniciar_medicion():
    """
    Inicia el contador de tiempo para la request actual.
    Se llama al inicio de cada endpoint.
    """
    try:
        request_data = obtener_datos_request()
        request_id = request_data["request_id"]
        tiempos_inicio[request_id] = time.time()
        
        registrar_log(
            "system",
            "INFO",
            f"=== INICIO REQUEST: {request_data['metodo']} {request_data['uri']} ==="
        )
    except Exception as e:
        print(f"Error al iniciar medición: {e}")


def finalizar_medicion():
    """
    Finaliza el contador de tiempo y registra el tiempo total.
    Se llama al final de cada endpoint.
    """
    try:
        request_data = obtener_datos_request()
        request_id = request_data["request_id"]
        
        if request_id in tiempos_inicio:
            duracion = (time.time() - tiempos_inicio[request_id]) * 1000
            registrar_log(
                "system",
                "INFO",
                f"=== FIN REQUEST: Tiempo total: {duracion:.2f}ms ==="
            )
            del tiempos_inicio[request_id]
    except Exception as e:
        print(f"Error al finalizar medición: {e}")


def log_decorator(modulo: str):
    """
    Decorador para logging automático de funciones.
    Registra entrada, salida y excepciones.
    
    Uso:
        @log_decorator("alumnos")
        def mi_funcion():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            iniciar_medicion()
            registrar_log(modulo, "INFO", f"Ejecutando {func.__name__}")
            
            try:
                resultado = func(*args, **kwargs)
                registrar_log(modulo, "INFO", f"{func.__name__} ejecutado exitosamente")
                finalizar_medicion()
                return resultado
                
            except Exception as e:
                registrar_log(modulo, "ERROR", f"Excepción en {func.__name__}: {str(e)}")
                finalizar_medicion()
                raise
        
        return wrapper
    return decorator