[README.md](https://github.com/user-attachments/files/23952224/README.md)
# 🎓 Sistema de Matrícula Universitaria

Sistema web completo de gestión académica desarrollado con **Arquitectura Orientada a Servicios (SOA)**. Implementa gestión de alumnos, cursos, matrículas, evaluaciones y reportería académica mediante servicios REST.

---

## 📋 Tabla de Contenidos

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Configuración de Base de Datos](#configuración-de-base-de-datos)
- [Ejecución del Sistema](#ejecución-del-sistema)
- [Uso del Sistema](#uso-del-sistema)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Servicios REST Disponibles](#servicios-rest-disponibles)
- [Tecnologías](#tecnologías)

---

## ✨ Características

### Funcionalidades Principales

- ✅ **Gestión de Alumnos**: CRUD completo con validaciones
- ✅ **Gestión de Cursos**: Administración de cursos por ciclo académico
- ✅ **Sistema de Matrícula**: Matrícula flexible hasta 6 cursos por ciclo
- ✅ **Evaluación de Cursos**: Registro de notas con cálculo automático de aprobación
- ✅ **Reportería Académica**: 3 interfaces de reportes
  - Notas de los 3 últimos ciclos
  - Notas del último ciclo
  - Reporte general por ciclo

### Características Técnicas

- 🏗️ **Arquitectura SOA**: Servicios independientes que se comunican por HTTP
- 📊 **26 Servicios REST**: APIs completas para todos los módulos
- 📝 **Logging Profesional**: Registro con Transaction ID, timestamps ISO 8601, métricas de rendimiento
- 🔒 **Validaciones Exhaustivas**: Validación de datos en frontend y backend
- 🌐 **Interfaz Moderna**: Bootstrap 5 con diseño responsivo
- 🔄 **Sistema de Arrastre**: Cursos desaprobados se llevan al siguiente ciclo

---

## 🏛️ Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                  FRONTEND WEB                       │
│              (Apache HTTP / Python)                 │
│                  Puerto 8080                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Alumnos  │ │  Cursos  │ │Matrícula │          │
│  └──────────┘ └──────────┘ └──────────┘          │
│  ┌──────────┐ ┌──────────┐                        │
│  │Evaluación│ │ Reportes │                        │
│  └──────────┘ └──────────┘                        │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP/REST
                   │
┌──────────────────▼──────────────────────────────────┐
│              BACKEND API (Flask)                    │
│                 Puerto 5000                         │
│  ┌──────────────────────────────────────────────┐  │
│  │  Servicios REST (Blueprints)                 │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │  │
│  │  │ Alumnos  │  │  Cursos  │  │Matrícula │  │  │
│  │  │ Service  │  │ Service  │  │ Service  │  │  │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  │  │
│  │       │             │              │         │  │
│  │  ┌────▼─────┐  ┌───▼──────┐  ┌───▼─────┐  │  │
│  │  │Evaluación│  │ Reportes │  │  Utils  │  │  │
│  │  │ Service  │  │ Service  │  │ Logger  │  │  │
│  │  └──────────┘  └──────────┘  └─────────┘  │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │         Capa de Logging Profesional          │  │
│  │  - Transaction ID                            │  │
│  │  - Timestamps ISO 8601                       │  │
│  │  - Métricas de rendimiento                   │  │
│  └──────────────────────────────────────────────┘  │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│              BASE DE DATOS                          │
│            MySQL / SQLite                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ alumnos  │ │  cursos  │ │matrícula │           │
│  └──────────┘ └──────────┘ └──────────┘           │
│  ┌──────────┐                                      │
│  │evaluación│                                      │
│  └──────────┘                                      │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Requisitos Previos

### Software Necesario

- **Python**: 3.8 o superior
- **Base de Datos**: MySQL 8.0+ o SQLite 3.x
- **Navegador Web**: Chrome, Firefox, Edge (versiones recientes)
- **Servidor Web** (opcional): Apache HTTP Server o Python HTTP Server

### Librerías Python

```
Flask==2.3.0
flask-cors==4.0.0
mysql-connector-python==8.0.33
requests==2.31.0
```

---

## 📥 Instalación

### 1. Clonar o Descargar el Proyecto

```bash
# Si tienes el proyecto en un ZIP
unzip Sistema_Matricula_FINAL.zip
cd Sistema_Matricula_FINAL/Trabajo_actulizado/Trabajo
```

### 2. Crear Entorno Virtual (Recomendado)

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate

# En Linux/Mac:
source venv/bin/activate
```

### 3. Instalar Dependencias del Backend

```bash
cd backend_api
pip install -r requirements.txt
```

**Contenido de `requirements.txt`:**
```
Flask==2.3.0
flask-cors==4.0.0
mysql-connector-python==8.0.33
requests==2.31.0
```

Si no existe el archivo `requirements.txt`, instalar manualmente:
```bash
pip install Flask flask-cors mysql-connector-python requests
```

---

## 🗄️ Configuración de Base de Datos

### Opción 1: SQLite (Más Simple - Recomendado para Pruebas)

SQLite no requiere instalación de servidor de base de datos.

```bash
cd backend_api
python crear_bd_sqlite.py
```

Esto creará automáticamente:
- Base de datos: `sistema_matricula.db`
- Tablas: alumnos, cursos, matriculas, evaluaciones
- Datos de prueba: 11 alumnos, 60 cursos

**Ventajas de SQLite:**
- ✅ No requiere instalación de MySQL
- ✅ Portátil (un solo archivo)
- ✅ Ideal para demostraciones

---

### Opción 2: MySQL (Producción)

#### 2.1. Instalar MySQL

- **Windows**: Descargar MySQL Installer desde [mysql.com](https://dev.mysql.com/downloads/installer/)
- **Linux**: 
  ```bash
  sudo apt-get update
  sudo apt-get install mysql-server
  ```

#### 2.2. Crear Base de Datos

```bash
# Conectar a MySQL
mysql -u root -p

# En el prompt de MySQL:
source ruta/al/archivo/sistema_matricula.sql
```

O ejecutar el script SQL manualmente que crea:
- Base de datos `sistema_matricula`
- 4 tablas principales
- 60 cursos (6 por ciclo, 10 ciclos)
- 11 alumnos de prueba
- Matrículas y evaluaciones de ejemplo

#### 2.3. Configurar Conexión

Editar archivo `backend_api/config.py`:

```python
# Para MySQL
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'tu_password',
    'database': 'sistema_matricula',
    'port': 3306
}

# Para SQLite (dejar como está)
# DATABASE_CONFIG = {'database': 'sistema_matricula.db'}
```

---

## 🚀 Ejecución del Sistema

### Paso 1: Iniciar Backend (API REST)

```bash
cd backend_api
python app.py
```

**Salida esperada:**
```
⚡ CARGANDO ARCHIVO DE ALUMNOS DESDE ESTE BACKEND ⚡
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

✅ **Backend corriendo en:** `http://127.0.0.1:5000`

---

### Paso 2: Iniciar Frontend (Interfaz Web)

**Abrir una NUEVA terminal/cmd** (mantener el backend corriendo):

#### Opción A: Python HTTP Server (Simple)

```bash
cd frontend
python -m http.server 8080
```

**Salida esperada:**
```
Serving HTTP on :: port 8080 (http://[::]:8080/) ...
```

✅ **Frontend disponible en:** `http://localhost:8080`

---

#### Opción B: Apache HTTP Server

1. **Instalar XAMPP** (incluye Apache)
2. **Copiar carpeta `frontend`** a `C:\xampp\htdocs\sistema_matricula`
3. **Iniciar Apache** desde XAMPP Control Panel
4. **Abrir navegador:** `http://localhost/sistema_matricula/index.html`

---

### Paso 3: Acceder al Sistema

Abrir navegador en: **`http://localhost:8080/index.html`**

Deberías ver el dashboard principal con 5 módulos:
- 👨‍🎓 Alumnos
- 📚 Cursos
- 📝 Matrículas
- 📊 Evaluaciones
- 📈 Reportes

---

## 📖 Uso del Sistema

### 1. Gestión de Alumnos

**URL:** `http://localhost:8080/alumnos.html`

**Operaciones:**
- ✅ **Crear alumno**: Click "Nuevo Alumno" → Llenar formulario
- ✅ **Editar alumno**: Click botón amarillo (lápiz)
- ✅ **Eliminar alumno**: Click botón rojo (X)

**Validaciones:**
- DNI: 8 dígitos numéricos
- Edad: Mínimo 16 años
- Teléfono: 9 dígitos, inicia con 9
- Nombre/Apellido: Solo letras

---

### 2. Gestión de Cursos

**URL:** `http://localhost:8080/cursos.html`

**Operaciones:**
- ✅ Listar cursos por ciclo
- ✅ Crear nuevo curso
- ✅ Editar curso existente
- ✅ Eliminar curso

**Datos requeridos:**
- Código: Ej. "MAT101"
- Nombre: Ej. "Matemática Básica"
- Créditos: 1-5
- Ciclo: 1-10

---

### 3. Matrícula de Cursos

**URL:** `http://localhost:8080/matriculas.html`

**Proceso:**
1. Seleccionar alumno del dropdown
2. Ver cursos jalados (obligatorios) y disponibles
3. Seleccionar hasta 6 cursos
4. Confirmar matrícula

**Reglas de negocio:**
- ⚠️ Máximo 6 cursos por ciclo
- ⚠️ Cursos desaprobados son obligatorios
- ⚠️ No se puede matricular 2 veces el mismo curso en el mismo ciclo

---

### 4. Evaluación de Cursos

**URL:** `http://localhost:8080/evaluaciones.html`

**Proceso:**
1. Ver lista de matrículas pendientes
2. Seleccionar matrícula
3. Ingresar nota (0-20)
4. Sistema calcula automáticamente:
   - Aprobado: nota ≥ 10.5
   - Desaprobado: nota < 10.5

---

### 5. Reportes Académicos

**URL:** `http://localhost:8080/reportes.html`

**3 Interfaces Obligatorias:**

#### TAB 1: Notas de los 3 Últimos Ciclos
- Muestra hasta los 3 ciclos más recientes
- Agrupa cursos por ciclo
- Estadísticas de aprobados/desaprobados

#### TAB 2: Notas del Último Ciclo
- Solo muestra el ciclo más reciente
- Promedio del ciclo
- Estadísticas detalladas

#### TAB 3: Reporte General
- Muestra TODOS los ciclos del alumno
- Estadísticas globales
- Historial académico completo

---

## 📁 Estructura del Proyecto

```
Sistema_Matricula_FINAL/
│
├── backend_api/                    # Backend Flask
│   ├── app.py                      # Aplicación principal
│   ├── config.py                   # Configuración de BD
│   ├── db.py                       # Conexión a base de datos
│   ├── crear_bd_sqlite.py          # Script crear BD SQLite
│   ├── requirements.txt            # Dependencias Python
│   │
│   ├── routes/                     # Servicios REST
│   │   ├── alumnos/
│   │   │   └── alumnos_routes.py   # 6 servicios de alumnos
│   │   ├── cursos/
│   │   │   └── cursos_routes.py    # 6 servicios de cursos
│   │   ├── matriculas/
│   │   │   └── matriculas_routes.py # 6 servicios de matrícula
│   │   ├── evaluaciones/
│   │   │   └── evaluaciones_routes.py # 6 servicios de evaluación
│   │   └── reportes/
│   │       └── reportes_routes.py  # 2 servicios de reportes
│   │
│   ├── utils/                      # Utilidades
│   │   └── logger.py               # Sistema de logging profesional
│   │
│   └── logs/                       # Archivos de log
│       ├── sistema_completo.log
│       ├── alumnos/
│       ├── cursos/
│       ├── matriculas/
│       └── evaluaciones/
│
├── frontend/                       # Frontend Web
│   ├── index.html                  # Dashboard principal
│   ├── alumnos.html                # Gestión de alumnos
│   ├── cursos.html                 # Gestión de cursos
│   ├── matriculas.html             # Sistema de matrícula
│   ├── evaluaciones.html           # Registro de notas
│   ├── reportes.html               # 3 reportes obligatorios
│   │
│   └── assets/
│       ├── css/
│       │   └── styles.css          # Estilos personalizados
│       ├── js/
│       │   ├── alumnos.js          # Lógica alumnos
│       │   ├── cursos.js           # Lógica cursos
│       │   ├── matriculas.js       # Lógica matrícula
│       │   ├── evaluaciones.js     # Lógica evaluaciones
│       │   └── reportes.js         # Lógica reportes
│       └── icons/                  # Iconos SVG
│
└── README.md                       # Este archivo
```

---

## 🌐 Servicios REST Disponibles

### Módulo Alumnos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/alumnos` | Listar todos los alumnos activos |
| POST | `/api/alumnos` | Crear nuevo alumno |
| GET | `/api/alumnos/<id>` | Obtener alumno por ID |
| PUT | `/api/alumnos/<id>` | Actualizar datos del alumno |
| DELETE | `/api/alumnos/<id>` | Eliminar alumno (lógico) |
| GET | `/api/alumnos/validar/<id>` | Validar existencia (SOA) |

### Módulo Cursos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/cursos` | Listar todos los cursos activos |
| POST | `/api/cursos` | Crear nuevo curso |
| GET | `/api/cursos/<id>` | Obtener curso por ID |
| PUT | `/api/cursos/<id>` | Actualizar datos del curso |
| DELETE | `/api/cursos/<id>` | Eliminar curso (lógico) |
| GET | `/api/cursos/validar/<id>` | Validar existencia (SOA) |

### Módulo Matrículas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/matriculas` | Listar todas las matrículas |
| POST | `/api/matriculas/flexible` | Crear matrícula (hasta 6 cursos) |
| GET | `/api/matriculas/<id>` | Obtener matrícula por ID |
| GET | `/api/matriculas/cursos-disponibles/<alumno_id>` | Cursos disponibles |
| PUT | `/api/matriculas/<id>` | Actualizar matrícula |
| DELETE | `/api/matriculas/<id>` | Eliminar matrícula |

### Módulo Evaluaciones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/evaluaciones` | Listar todas las evaluaciones |
| POST | `/api/evaluaciones` | Crear evaluación (nota) |
| GET | `/api/evaluaciones/<id>` | Obtener evaluación por ID |
| GET | `/api/evaluaciones/pendientes` | Matrículas sin evaluar |
| PUT | `/api/evaluaciones/<id>` | Actualizar nota |
| DELETE | `/api/evaluaciones/<id>` | Eliminar evaluación |

### Módulo Reportes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/reportes/rendimiento_alumno/<id>?filtro=ULTIMOS_3` | Últimos 3 ciclos |
| GET | `/api/reportes/rendimiento_alumno/<id>?filtro=ULTIMO` | Último ciclo |
| GET | `/api/reportes/rendimiento_alumno/<id>?filtro=TODOS` | Todos los ciclos |
| GET | `/api/reportes/alumnos_ciclo` | Estadísticas por ciclo |

**Total:** 26 servicios REST implementados

---

## 🛠️ Tecnologías

### Backend
- **Python 3.8+**: Lenguaje principal
- **Flask 2.3**: Framework web
- **MySQL Connector**: Driver para MySQL
- **SQLite3**: Base de datos alternativa
- **Requests**: Comunicación HTTP entre servicios

### Frontend
- **HTML5**: Estructura
- **CSS3**: Estilos
- **JavaScript ES6**: Lógica del cliente
- **Bootstrap 5.3**: Framework CSS
- **Fetch API**: Consumo de servicios REST

### Arquitectura
- **SOA**: Arquitectura Orientada a Servicios
- **REST**: APIs RESTful
- **MVC**: Patrón Modelo-Vista-Controlador
- **Blueprints**: Modularización de Flask

---

## 📊 Pruebas y Validación

### Probar Backend con CURL

```bash
# Listar alumnos
curl http://127.0.0.1:5000/api/alumnos

# Crear alumno
curl -X POST http://127.0.0.1:5000/api/alumnos \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Juan","apellido":"Pérez","dni":"72345678","edad":20}'

# Obtener alumno
curl http://127.0.0.1:5000/api/alumnos/1
```

### Probar con Postman

1. Importar colección de endpoints
2. Configurar base URL: `http://127.0.0.1:5000`
3. Ejecutar requests de prueba

---

## 🐛 Solución de Problemas

### Error: "No module named 'flask'"
```bash
pip install Flask
```

### Error: "Connection refused" al consumir servicios
- Verificar que el backend esté corriendo en puerto 5000
- Revisar CORS en `app.py`

### Error: "Database connection failed"
- Verificar credenciales en `config.py`
- Asegurar que MySQL esté corriendo
- Para SQLite, ejecutar `crear_bd_sqlite.py`

### Frontend no carga datos
- Abrir DevTools (F12) → Console
- Verificar errores de CORS
- Confirmar que backend responde en puerto 5000

---

## 📝 Logging

El sistema genera logs profesionales en `backend_api/logs/`

**Formato de log:**
```
[2024-12-04T10:30:15.123Z] [INFO] [TXN-20241204103015-a1b2c3d4] [alumnos] [alumnos_routes.py:85] [listar_alumnos] [PID:1234] [Thread:56789] [IP:127.0.0.1] [GET /api/alumnos] [45.23ms] → Alumnos recuperados: 10 registros
```

**Metadatos incluidos:**
- ✅ Timestamp ISO 8601 UTC
- ✅ Nivel (INFO, WARN, ERROR)
- ✅ Transaction ID único
- ✅ Módulo/Servicio
- ✅ Archivo y línea de código
- ✅ Función ejecutada
- ✅ PID y Thread ID
- ✅ IP del cliente
- ✅ Método HTTP y URI
- ✅ Tiempo de procesamiento

---

## 👥 Autor

**Curso:** Arquitectura Orientada a Servicios  
**Proyecto:** Sistema de Matrícula Universitaria  
**Año:** 2024

---

## 📄 Licencia

Este proyecto es desarrollado con fines académicos para el curso de Arquitectura Orientada a Servicios.

---

## 🆘 Soporte

Para preguntas o problemas:
1. Revisar la sección de [Solución de Problemas](#solución-de-problemas)
2. Verificar los logs en `backend_api/logs/sistema_completo.log`
3. Consultar con el instructor del curso

---

**¡Sistema listo para demostración y evaluación! 🎉**
