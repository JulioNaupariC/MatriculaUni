import sqlite3
import os

# Ruta de la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), "sistema_matricula.db")

# Eliminar BD si existe (para empezar limpio)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("Base de datos anterior eliminada")

# Crear conexión
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Creando tablas...")

# ═══════════════════════════════════════════════════════════════════════
# CREAR TABLAS
# ═══════════════════════════════════════════════════════════════════════

cursor.execute("""
CREATE TABLE alumnos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    edad INTEGER,
    dni TEXT UNIQUE NOT NULL,
    correo TEXT,
    telefono TEXT,
    ciclo_actual INTEGER DEFAULT 1,
    activo INTEGER DEFAULT 1,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE cursos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    creditos INTEGER NOT NULL,
    ciclo INTEGER NOT NULL,
    activo INTEGER DEFAULT 1,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE matriculas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_alumno INTEGER NOT NULL,
    id_curso INTEGER NOT NULL,
    ciclo INTEGER NOT NULL,
    fecha_matricula TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado TEXT DEFAULT 'MATRICULADO',
    FOREIGN KEY (id_alumno) REFERENCES alumnos(id) ON DELETE CASCADE,
    FOREIGN KEY (id_curso) REFERENCES cursos(id) ON DELETE CASCADE,
    UNIQUE(id_alumno, id_curso, ciclo)
)
""")

cursor.execute("""
CREATE TABLE evaluaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_matricula INTEGER NOT NULL,
    nota REAL NOT NULL,
    fecha_evaluacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aprobado INTEGER AS (CASE WHEN nota >= 10.5 THEN 1 ELSE 0 END) STORED,
    FOREIGN KEY (id_matricula) REFERENCES matriculas(id) ON DELETE CASCADE
)
""")

print("✅ Tablas creadas")

# ═══════════════════════════════════════════════════════════════════════
# INSERTAR ALUMNOS
# ═══════════════════════════════════════════════════════════════════════

alumnos = [
    ('Juan', 'Pérez García', 20, '72345678', 'juan.perez@univ.edu.pe', '987654321', 1),
    ('María', 'López Torres', 19, '73456789', 'maria.lopez@univ.edu.pe', '987654322', 1),
    ('Carlos', 'Ramírez Silva', 21, '74567890', 'carlos.ramirez@univ.edu.pe', '987654323', 2),
    ('Ana', 'Mendoza Flores', 20, '75678901', 'ana.mendoza@univ.edu.pe', '987654324', 2),
    ('Luis', 'Castillo Rojas', 22, '76789012', 'luis.castillo@univ.edu.pe', '987654325', 3),
    ('Rosa', 'Vega Morales', 19, '77890123', 'rosa.vega@univ.edu.pe', '987654326', 1),
    ('Pedro', 'Sánchez Cruz', 21, '78901234', 'pedro.sanchez@univ.edu.pe', '987654327', 4),
    ('Laura', 'Díaz Paredes', 20, '79012345', 'laura.diaz@univ.edu.pe', '987654328', 3),
    ('Diego', 'Fernández Quispe', 22, '70123456', 'diego.fernandez@univ.edu.pe', '987654329', 5),
    ('Sofía', 'Martínez Ramos', 19, '71234567', 'sofia.martinez@univ.edu.pe', '987654330', 2),
    ('Miguel', 'Torres Vargas', 21, '70234567', 'miguel.torres@univ.edu.pe', '987654331', 3)
]

cursor.executemany("""
    INSERT INTO alumnos (nombre, apellido, edad, dni, correo, telefono, ciclo_actual)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", alumnos)

print(f"✅ {len(alumnos)} alumnos insertados")

# ═══════════════════════════════════════════════════════════════════════
# INSERTAR CURSOS (60 CURSOS)
# ═══════════════════════════════════════════════════════════════════════

cursos = [
    # CICLO 1
    ('MAT101', 'Matemática Básica', 4, 1),
    ('LEN101', 'Lenguaje y Comunicación', 3, 1),
    ('FIS101', 'Física I', 4, 1),
    ('QUI101', 'Química General', 4, 1),
    ('INF101', 'Introducción a la Informática', 3, 1),
    ('SOC101', 'Realidad Nacional', 2, 1),
    # CICLO 2
    ('MAT201', 'Cálculo I', 5, 2),
    ('FIS201', 'Física II', 4, 2),
    ('QUI201', 'Química Orgánica', 4, 2),
    ('INF201', 'Programación I', 4, 2),
    ('EST201', 'Estadística I', 3, 2),
    ('ADM201', 'Administración General', 3, 2),
    # CICLO 3
    ('MAT301', 'Cálculo II', 5, 3),
    ('INF301', 'Programación II', 4, 3),
    ('EST301', 'Estadística II', 3, 3),
    ('BD301', 'Base de Datos I', 4, 3),
    ('ALG301', 'Algoritmos y Estructuras de Datos', 4, 3),
    ('ING301', 'Inglés Técnico I', 2, 3),
    # CICLO 4
    ('MAT401', 'Matemática Discreta', 4, 4),
    ('INF401', 'Programación Orientada a Objetos', 4, 4),
    ('BD401', 'Base de Datos II', 4, 4),
    ('RED401', 'Redes de Computadoras I', 4, 4),
    ('SIS401', 'Análisis de Sistemas I', 4, 4),
    ('ING401', 'Inglés Técnico II', 2, 4),
    # CICLO 5
    ('ARQ501', 'Arquitectura de Computadoras', 4, 5),
    ('WEB501', 'Desarrollo Web I', 4, 5),
    ('SIS501', 'Análisis de Sistemas II', 4, 5),
    ('RED501', 'Redes de Computadoras II', 4, 5),
    ('SEG501', 'Seguridad Informática', 3, 5),
    ('GES501', 'Gestión de Proyectos I', 3, 5),
    # CICLO 6
    ('WEB601', 'Desarrollo Web II', 4, 6),
    ('MOV601', 'Desarrollo Móvil', 4, 6),
    ('IA601', 'Inteligencia Artificial I', 4, 6),
    ('ARQ601', 'Arquitectura de Software', 4, 6),
    ('CAL601', 'Calidad de Software', 3, 6),
    ('GES601', 'Gestión de Proyectos II', 3, 6),
    # CICLO 7
    ('IA701', 'Inteligencia Artificial II', 4, 7),
    ('BIG701', 'Big Data', 4, 7),
    ('CLO701', 'Computación en la Nube', 4, 7),
    ('IOT701', 'Internet de las Cosas', 4, 7),
    ('ETI701', 'Ética Profesional', 2, 7),
    ('INV701', 'Metodología de la Investigación', 3, 7),
    # CICLO 8
    ('TEL801', 'Telecomunicaciones', 4, 8),
    ('AUD801', 'Auditoría de Sistemas', 4, 8),
    ('EMP801', 'Emprendimiento Digital', 3, 8),
    ('TES801', 'Tesis I', 4, 8),
    ('ELE801', 'Electivo I', 3, 8),
    ('TIC801', 'Tecnologías Emergentes', 3, 8),
    # CICLO 9
    ('TES901', 'Tesis II', 5, 9),
    ('GOB901', 'Gobierno de TI', 4, 9),
    ('BUS901', 'Business Intelligence', 4, 9),
    ('ELE901', 'Electivo II', 3, 9),
    ('SEM901', 'Seminario de Investigación', 3, 9),
    ('PRA901', 'Prácticas Pre-Profesionales', 4, 9),
    # CICLO 10
    ('TES1001', 'Tesis III', 6, 10),
    ('GER1001', 'Gerencia de Proyectos TI', 4, 10),
    ('INN1001', 'Innovación Tecnológica', 3, 10),
    ('ELE1001', 'Electivo III', 3, 10),
    ('INT1001', 'Integración de Sistemas', 4, 10),
    ('SUS1001', 'Sustentación de Tesis', 3, 10)
]

cursor.executemany("""
    INSERT INTO cursos (codigo, nombre, creditos, ciclo)
    VALUES (?, ?, ?, ?)
""", cursos)

print(f"✅ {len(cursos)} cursos insertados")

# ═══════════════════════════════════════════════════════════════════════
# INSERTAR MATRÍCULAS
# ═══════════════════════════════════════════════════════════════════════

matriculas = [
    (1, 1, 1), (1, 2, 1), (1, 5, 1),
    (2, 1, 1), (2, 2, 1), (2, 3, 1), (2, 5, 1),
    (3, 7, 2), (3, 8, 2), (3, 10, 2), (3, 11, 2),
    (4, 7, 2), (4, 10, 2), (4, 12, 2),
    (5, 13, 3), (5, 14, 3), (5, 16, 3), (5, 17, 3), (5, 18, 3)
]

cursor.executemany("""
    INSERT INTO matriculas (id_alumno, id_curso, ciclo)
    VALUES (?, ?, ?)
""", matriculas)

print(f"✅ {len(matriculas)} matrículas insertadas")

# ═══════════════════════════════════════════════════════════════════════
# INSERTAR EVALUACIONES
# ═══════════════════════════════════════════════════════════════════════

evaluaciones = [
    (1, 15.5), (2, 12.0), (3, 14.5),
    (4, 16.0), (5, 13.5), (6, 9.5), (7, 15.0),
    (8, 14.0), (9, 11.5), (10, 17.0), (11, 13.0),
    (12, 10.5), (13, 16.5), (14, 8.0)
]

cursor.executemany("""
    INSERT INTO evaluaciones (id_matricula, nota)
    VALUES (?, ?)
""", evaluaciones)

print(f"✅ {len(evaluaciones)} evaluaciones insertadas")

# ═══════════════════════════════════════════════════════════════════════
# VERIFICAR
# ═══════════════════════════════════════════════════════════════════════

cursor.execute("SELECT COUNT(*) FROM alumnos")
print(f"\n📊 Total alumnos: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM cursos")
print(f"📊 Total cursos: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM matriculas")
print(f"📊 Total matrículas: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM evaluaciones")
print(f"📊 Total evaluaciones: {cursor.fetchone()[0]}")

# Guardar cambios
conn.commit()
conn.close()

print("\n✅ BASE DE DATOS CREADA EXITOSAMENTE")
print(f"📁 Ubicación: {DB_PATH}")
