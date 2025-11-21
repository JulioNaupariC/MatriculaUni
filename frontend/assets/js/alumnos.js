const API = "http://localhost:5000/api/alumnos";

const tbody = document.getElementById("tablaAlumnos");
const alertContainer = document.getElementById("alertContainer");

const modal = new bootstrap.Modal(document.getElementById("modalAlumno"));
const form = document.getElementById("formAlumno");

const idInput = document.getElementById("alumnoId");
const nombreInput = document.getElementById("nombre");
const apellidoInput = document.getElementById("apellido");
const edadInput = document.getElementById("edad");
const dniInput = document.getElementById("dni");
const correoInput = document.getElementById("correo");
const telefonoInput = document.getElementById("telefono");
const cicloInput = document.getElementById("ciclo");
const modalTitulo = document.getElementById("modalTitulo");

// =====================================================
// VALIDACIONES
// =====================================================
function validarAlumnoFront(isEditing = false) {
  let errores = [];

  // Nombre
  if (!/^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$/.test(nombreInput.value.trim())) {
    errores.push("El nombre solo debe contener letras.");
  }

  // Apellido
  if (!/^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$/.test(apellidoInput.value.trim())) {
    errores.push("El apellido solo debe contener letras.");
  }

  // DNI
  if (!/^[0-9]{8}$/.test(dniInput.value.trim())) {
    errores.push("El DNI debe tener exactamente 8 números.");
  }

  // Teléfono
  if (!/^9[0-9]{8}$/.test(telefonoInput.value.trim())) {
    errores.push("El teléfono debe tener 9 dígitos y comenzar con 9.");
  }

  // Correo
  if (correoInput.value.trim().length > 0) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(correoInput.value.trim())) {
      errores.push("Ingrese un correo válido.");
    }
  }

  // Ciclo
  const ciclo = parseInt(cicloInput.value);

  if (ciclo < 1 || ciclo > 10) {
    errores.push("El ciclo debe estar entre 1 y 10.");
  }

  // Si es edición → NO permitir bajar ciclo
  if (isEditing) {
    const cicloOriginal = parseInt(cicloInput.dataset.originalCiclo);
    if (ciclo < cicloOriginal) {
      errores.push(`No puedes reducir el ciclo. Ciclo actual: ${cicloOriginal}.`);
    }
  }

  return errores;
}

// =====================================================
// CARGAR LISTA DE ALUMNOS
// =====================================================
async function cargarAlumnos() {
  tbody.innerHTML = `
    <tr>
      <td colspan="8" class="text-center text-muted py-3">Cargando...</td>
    </tr>
  `;

  try {
    const res = await fetch(API);
    const data = await res.json();

    tbody.innerHTML = "";

    if (!data.length) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" class="text-center py-4 text-muted">No hay alumnos registrados.</td>
        </tr>
      `;
      return;
    }

    data.forEach(a => {
      tbody.innerHTML += `
        <tr class="text-center">
          <td>${a.id}</td>
          <td>${a.nombre} ${a.apellido}</td>
          <td>${a.dni}</td>
          <td>${a.edad}</td>
          <td>${a.correo || "-"}</td>
          <td>${a.telefono || "-"}</td>
          <td>${a.ciclo_actual}</td>
          <td>
            <button class="btn btn-sm btn-outline-primary me-1" onclick="editarAlumno(${a.id})">Editar</button>
            <button class="btn btn-sm btn-outline-danger" onclick="eliminarAlumno(${a.id})">Eliminar</button>
          </td>
        </tr>
      `;
    });

  } catch (error) {
    mostrarAlerta("Error al cargar alumnos.", "danger");
    console.error(error);
  }
}

// =====================================================
// ALERTAS
// =====================================================
function mostrarAlerta(msg, tipo = "success") {
  alertContainer.innerHTML = `
    <div class="alert alert-${tipo} alert-dismissible fade show" role="alert">
      ${msg}
      <button class="btn-close" data-bs-dismiss="alert"></button>
    </div>
  `;
}

// =====================================================
// CREAR / EDITAR ALUMNO
// =====================================================
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const esEdicion = idInput.value !== "";

  const errores = validarAlumnoFront(esEdicion);
  if (errores.length > 0) {
    mostrarAlerta(errores.join("<br>"), "warning");
    return;
  }

  const alumno = {
    nombre: nombreInput.value,
    apellido: apellidoInput.value,
    edad: edadInput.value,
    dni: dniInput.value,
    correo: correoInput.value,
    telefono: telefonoInput.value,
    ciclo_actual: cicloInput.value
  };

  const url = esEdicion ? `${API}/${idInput.value}` : API;
  const method = esEdicion ? "PUT" : "POST";

  try {
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(alumno)
    });

    const data = await res.json();

    if (!res.ok) {
      mostrarAlerta(data.errores ? data.errores.join("<br>") : data.error, "warning");
      return;
    }

    mostrarAlerta(esEdicion ? "Alumno actualizado" : "Alumno registrado");

    modal.hide();
    form.reset();
    idInput.value = "";
    cargarAlumnos();

  } catch (error) {
    mostrarAlerta("Error al guardar.", "danger");
    console.error(error);
  }
});

// =====================================================
// EDITAR ALUMNO
// =====================================================
async function editarAlumno(id) {
  try {
    const res = await fetch(`${API}/${id}`);
    const data = await res.json();

    idInput.value = data.id;
    nombreInput.value = data.nombre;
    apellidoInput.value = data.apellido;
    edadInput.value = data.edad;
    dniInput.value = data.dni;
    correoInput.value = data.correo;
    telefonoInput.value = data.telefono;
    cicloInput.value = data.ciclo_actual;

    // Guardar ciclo original para evitar que baje
    cicloInput.dataset.originalCiclo = data.ciclo_actual;

    modalTitulo.textContent = "Editar Alumno";
    modal.show();

  } catch (error) {
    mostrarAlerta("Error al obtener datos del alumno.", "danger");
  }
}

// =====================================================
// ELIMINAR ALUMNO
// =====================================================
async function eliminarAlumno(id) {
  if (!confirm("¿Eliminar este alumno?")) return;

  try {
    await fetch(`${API}/${id}`, { method: "DELETE" });
    mostrarAlerta("Alumno eliminado.");
    cargarAlumnos();
  } catch (error) {
    mostrarAlerta("No se pudo eliminar.", "danger");
  }
}

// =====================================================
// BOTÓN REFRESCAR
// =====================================================
document.getElementById("btnRefrescar").addEventListener("click", cargarAlumnos);

// =====================================================
// INICIO
// =====================================================
cargarAlumnos();
