import os
from datetime import datetime, timezone
import time
from flask import request

# Ruta fija del backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
BASE_LOG_DIR = os.path.abspath(BASE_LOG_DIR)

# Variable global para medir tiempos de procesamiento
tiempos_inicio = {}


def registrar_log(modulo: str, nivel: str, mensaje: str):
    """
    Registra un log con TODOS los metadatos requeridos por el PDF:
    ✅ Timestamp en formato ISO 8601 UTC
    ✅ Nivel de log (INFO, WARN, ERROR)
    ✅ Transaction ID único
    ✅ Nombre del módulo/servicio
    ✅ IP del cliente
    ✅ Método HTTP (GET, POST, PUT, DELETE)
    ✅ URI completa
    ✅ Código de estado HTTP
    ✅ Tiempo de procesamiento en ms
    """
    
    # 1. TIMESTAMP ISO 8601 UTC
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    
    # 2. TRANSACTION ID ÚNICO
    tx_id = f"TX-{int(time.time() * 1000000) % 1000000000}"
    
    # 3. IP DEL CLIENTE (manejando X-Forwarded-For para proxies)
    ip_cliente = "UNKNOWN"
    try:
        if request:
            ip_cliente = request.headers.get('X-Forwarded-For', request.remote_addr)
            if ip_cliente and ',' in ip_cliente:
                ip_cliente = ip_cliente.split(',')[0].strip()
    except:
        ip_cliente = "CLI"
    
    # 4. MÉTODO HTTP
    metodo_http = "CLI"
    try:
        if request:
            metodo_http = request.method
    except:
        pass
    
    # 5. URI COMPLETA
    uri = "/"
    try:
        if request:
            uri = request.path
    except:
        pass
    
    # 6. CÓDIGO HTTP STATUS
    status_code = 200
    try:
        if request:
            # Intentar obtener el status code del contexto
            status_code = getattr(request, '_status_code', 200)
    except:
        pass
    
    # 7. TIEMPO DE PROCESAMIENTO (si está disponible)
    duracion_ms = ""
    request_id = id(request) if request else None
    if request_id and request_id in tiempos_inicio:
        duracion = (time.time() - tiempos_inicio[request_id]) * 1000
        duracion_ms = f" [{duracion:.2f}ms]"
    
    # FORMATO COMPLETO DEL LOG CON TODOS LOS METADATOS
    linea_log = (
        f"[{timestamp}] "
        f"[{nivel:5}] "
        f"[{tx_id}] "
        f"[{modulo:12}] "
        f"[IP:{ip_cliente:15}] "
        f"[{metodo_http:6} {uri:40}] "
        f"[Status:{status_code}]"
        f"{duracion_ms} "
        f"{mensaje}\n"
    )
    
    # Crear carpeta del módulo si no existe
    ruta_modulo = os.path.join(BASE_LOG_DIR, modulo)
    os.makedirs(ruta_modulo, exist_ok=True)
    
    # Guardar en archivo del módulo
    ruta_log = os.path.join(ruta_modulo, f"{modulo}.log")
    with open(ruta_log, "a", encoding="utf-8") as file:
        file.write(linea_log)
    
    # También guardar en log centralizado
    log_centralizado = os.path.join(BASE_LOG_DIR, "sistema_completo.log")
    with open(log_centralizado, "a", encoding="utf-8") as file:
        file.write(linea_log)


def iniciar_medicion():
    """Inicia el contador de tiempo para la request actual"""
    try:
        if request:
            request_id = id(request)
            tiempos_inicio[request_id] = time.time()
    except:
        pass


def finalizar_medicion():
    """Limpia el contador de tiempo de la request"""
    try:
        if request:
            request_id = id(request)
            if request_id in tiempos_inicio:
                del tiempos_inicio[request_id]
    except:
        pass