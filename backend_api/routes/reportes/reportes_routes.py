from flask import Blueprint, jsonify, request
# Solo importamos los servicios que vamos a usar
from routes.matriculas.matriculas_routes import servicio_rendimiento_alumno, servicio_reporte_alumnos_ciclo

reportes_bp = Blueprint("reportes_bp", __name__, url_prefix="/api/reportes")

# ============================
# REPORTE 1: RENDIMIENTO POR ALUMNO (Inteligente)
# ============================
@reportes_bp.route("/rendimiento_alumno/<int:alumno_id>", methods=["GET"])
def rendimiento_alumno(alumno_id):
    filtro = request.args.get('filtro', 'TODOS')
    try:
        data = servicio_rendimiento_alumno(alumno_id, filtro)
        return jsonify({"historial_academico": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================
# REPORTE 2: ALUMNOS POR CICLO
# ============================
@reportes_bp.route("/alumnos_ciclo", methods=["GET"])
def alumnos_ciclo():
    try:
        return jsonify(servicio_reporte_alumnos_ciclo()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500