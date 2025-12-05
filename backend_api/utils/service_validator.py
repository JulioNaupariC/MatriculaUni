"""
Validador de Servicios - Arquitectura Orientada a Servicios (SOA)

Este módulo implementa validaciones entre servicios sin acceso directo a BD.
Según el laboratorio: "Los servicios no deben consumir repositorios de otros servicios"
"""

import requests
from utils.logger import registrar_log

# URL base de la API (ajustar según tu configuración)
API_BASE_URL = "http://127.0.0.1:5000/api"


def validar_alumno_existe(alumno_id: int) -> dict:
    """
    Valida si un alumno existe llamando al servicio de alumnos.
    
    Returns:
        dict: {"existe": bool, "mensaje": str, "data": dict | None}
    """
    try:
        registrar_log("service_validator", "INFO", 
                     f"Validando existencia del alumno ID={alumno_id} mediante servicio")
        
        url = f"{API_BASE_URL}/alumnos/{alumno_id}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            alumno_data = response.json()
            registrar_log("service_validator", "INFO", 
                         f"Alumno ID={alumno_id} existe: {alumno_data.get('nombre')} {alumno_data.get('apellido')}")
            return {
                "existe": True,
                "mensaje": "Alumno encontrado",
                "data": alumno_data
            }
        elif response.status_code == 404:
            registrar_log("service_validator", "WARN", 
                         f"Alumno ID={alumno_id} no encontrado")
            return {
                "existe": False,
                "mensaje": "Alumno no encontrado",
                "data": None
            }
        else:
            registrar_log("service_validator", "ERROR", 
                         f"Error al validar alumno: Status {response.status_code}")
            return {
                "existe": False,
                "mensaje": f"Error en servicio de alumnos: {response.status_code}",
                "data": None
            }
            
    except requests.exceptions.Timeout:
        registrar_log("service_validator", "ERROR", 
                     f"Timeout al validar alumno ID={alumno_id}")
        return {
            "existe": False,
            "mensaje": "Timeout en servicio de alumnos",
            "data": None
        }
    except requests.exceptions.RequestException as e:
        registrar_log("service_validator", "ERROR", 
                     f"Excepción al validar alumno: {str(e)}")
        return {
            "existe": False,
            "mensaje": f"Error de conexión con servicio de alumnos: {str(e)}",
            "data": None
        }


def validar_curso_existe(curso_id: int) -> dict:
    """
    Valida si un curso existe llamando al servicio de cursos.
    
    Returns:
        dict: {"existe": bool, "mensaje": str, "data": dict | None}
    """
    try:
        registrar_log("service_validator", "INFO", 
                     f"Validando existencia del curso ID={curso_id} mediante servicio")
        
        url = f"{API_BASE_URL}/cursos/{curso_id}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            curso_data = response.json()
            registrar_log("service_validator", "INFO", 
                         f"Curso ID={curso_id} existe: {curso_data.get('codigo')} - {curso_data.get('nombre')}")
            return {
                "existe": True,
                "mensaje": "Curso encontrado",
                "data": curso_data
            }
        elif response.status_code == 404:
            registrar_log("service_validator", "WARN", 
                         f"Curso ID={curso_id} no encontrado")
            return {
                "existe": False,
                "mensaje": "Curso no encontrado",
                "data": None
            }
        else:
            registrar_log("service_validator", "ERROR", 
                         f"Error al validar curso: Status {response.status_code}")
            return {
                "existe": False,
                "mensaje": f"Error en servicio de cursos: {response.status_code}",
                "data": None
            }
            
    except requests.exceptions.Timeout:
        registrar_log("service_validator", "ERROR", 
                     f"Timeout al validar curso ID={curso_id}")
        return {
            "existe": False,
            "mensaje": "Timeout en servicio de cursos",
            "data": None
        }
    except requests.exceptions.RequestException as e:
        registrar_log("service_validator", "ERROR", 
                     f"Excepción al validar curso: {str(e)}")
        return {
            "existe": False,
            "mensaje": f"Error de conexión con servicio de cursos: {str(e)}",
            "data": None
        }


def validar_matricula_existe(matricula_id: int) -> dict:
    """
    Valida si una matrícula existe llamando al servicio de matrículas.
    
    Returns:
        dict: {"existe": bool, "mensaje": str, "data": dict | None}
    """
    try:
        registrar_log("service_validator", "INFO", 
                     f"Validando existencia de matrícula ID={matricula_id} mediante servicio")
        
        url = f"{API_BASE_URL}/matriculas/{matricula_id}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            matricula_data = response.json()
            registrar_log("service_validator", "INFO", 
                         f"Matrícula ID={matricula_id} existe")
            return {
                "existe": True,
                "mensaje": "Matrícula encontrada",
                "data": matricula_data
            }
        elif response.status_code == 404:
            registrar_log("service_validator", "WARN", 
                         f"Matrícula ID={matricula_id} no encontrada")
            return {
                "existe": False,
                "mensaje": "Matrícula no encontrada",
                "data": None
            }
        else:
            registrar_log("service_validator", "ERROR", 
                         f"Error al validar matrícula: Status {response.status_code}")
            return {
                "existe": False,
                "mensaje": f"Error en servicio de matrículas: {response.status_code}",
                "data": None
            }
            
    except requests.exceptions.Timeout:
        registrar_log("service_validator", "ERROR", 
                     f"Timeout al validar matrícula ID={matricula_id}")
        return {
            "existe": False,
            "mensaje": "Timeout en servicio de matrículas",
            "data": None
        }
    except requests.exceptions.RequestException as e:
        registrar_log("service_validator", "ERROR", 
                     f"Excepción al validar matrícula: {str(e)}")
        return {
            "existe": False,
            "mensaje": f"Error de conexión con servicio de matrículas: {str(e)}",
            "data": None
        }


def validar_datos_matricula(alumno_id: int, curso_id: int) -> dict:
    """
    Valida en paralelo que alumno y curso existan antes de crear matrícula.
    Implementa SOA: no accede directamente a BD, usa servicios.
    
    Returns:
        dict: {"valido": bool, "mensaje": str, "errores": list}
    """
    registrar_log("service_validator", "INFO", 
                 f"Validando datos para matrícula: Alumno={alumno_id}, Curso={curso_id}")
    
    errores = []
    
    # Validar alumno
    resultado_alumno = validar_alumno_existe(alumno_id)
    if not resultado_alumno["existe"]:
        errores.append(f"Alumno inválido: {resultado_alumno['mensaje']}")
    
    # Validar curso
    resultado_curso = validar_curso_existe(curso_id)
    if not resultado_curso["existe"]:
        errores.append(f"Curso inválido: {resultado_curso['mensaje']}")
    
    if errores:
        registrar_log("service_validator", "WARN", 
                     f"Validación de matrícula falló: {', '.join(errores)}")
        return {
            "valido": False,
            "mensaje": "Datos inválidos para matrícula",
            "errores": errores
        }
    
    registrar_log("service_validator", "INFO", 
                 "Validación de matrícula exitosa")
    return {
        "valido": True,
        "mensaje": "Datos válidos",
        "errores": []
    }