from flask import Flask, jsonify
from flask_cors import CORS

# Importar Blueprints
from routes.alumnos.alumnos_routes import alumnos_bp
from routes.cursos.cursos_routes import cursos_bp
from routes.matriculas.matriculas_routes import matriculas_bp
from routes.evaluaciones.evaluaciones_routes import evaluaciones_bp
from routes.reportes.reportes_routes import reportes_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Ruta raíz
    @app.route('/')
    def home():
        return jsonify({
            "mensaje": "API Sistema de Matrícula funcionando correctamente",
            "version": "1.0",
            "endpoints_disponibles": [
                "GET /api/alumnos - Listar alumnos",
                "GET /api/alumnos/<id> - Obtener alumno",
                "POST /api/alumnos - Crear alumno",
                "PUT /api/alumnos/<id> - Actualizar alumno",
                "DELETE /api/alumnos/<id> - Eliminar alumno",
                "GET /api/cursos - Listar cursos",
                "GET /api/matriculas - Listar matrículas",
                "GET /api/evaluaciones - Listar evaluaciones",
                "GET /api/reportes/general - Reporte general"
            ]
        })

    # Registrar módulos
    app.register_blueprint(alumnos_bp)
    app.register_blueprint(cursos_bp)
    app.register_blueprint(matriculas_bp)
    app.register_blueprint(evaluaciones_bp)
    app.register_blueprint(reportes_bp)

    return app

if __name__ == "__main__":
    app = create_app()
app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)