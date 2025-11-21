const API = "http://127.0.0.1:5000/api/matriculas";
const API_ALUMNOS = "http://127.0.0.1:5000/api/alumnos";
const API_CURSOS = "http://127.0.0.1:5000/api/cursos";

const tbody = document.getElementById("tbodyMatriculas");
const alertContainer = document.getElementById("alertContainer");
const btnNuevaMatricula = document.getElementById("btnNuevaMatricula");
const modalMatricula = document.getElementById("modalMatricula");
const formMatricula = document.getElementById("formMatricula");
const btnGuardarMatricula = document.getElementById("btnGuardarMatricula");

let alumnos = [];
let cursos = [];
let cursosSeleccionados = [];

// =====================================================
//      ALERTAS
// =====================================================
function mostrarAlerta(msg, tipo = "success") {
  alertContainer.innerHTML = `
    <div class="alert alert-${tipo} alert-dismissible fade show" role="alert">
      ${msg}
      <button class="btn-close" data-bs-dismiss="alert"></button>
    </div>
  `;
  setTimeout(() => {
    alertContainer.innerHTML = "";
  }, 5000);
}

// =====================================================
//      CARGAR ALUMNOS Y CURSOS
// =====================================================
async function cargarAlumnos() {
  try {
    const res = await fetch(API_ALUMNOS);
    if (!res.ok) throw new Error("Error al cargar alumnos");
    alumnos = await res.json();
  } catch (err) {
    console.error("Error cargando alumnos:", err);
    alumnos = [];
  }
}

async function cargarCursos() {
  try {
    const res = await fetch(API_CURSOS);
    if (!res.ok) throw new Error("Error al cargar cursos");
    cursos = await res.json();
  } catch (err) {
    console.error("Error cargando cursos:", err);
    cursos = [];
  }
}

// =====================================================
//      CARGAR MATRÍCULAS
// =====================================================
async function cargarMatriculas() {
  tbody.innerHTML = `
    <tr>
      <td colspan="6" class="text-center py-3">Cargando...</td>
    </tr>
  `;

  try {
    const res = await fetch(API);
    if (!res.ok) {
      throw new Error("Error al cargar matrículas");
    }

    const data = await res.json();

    if (!data.length) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6" class="text-center text-muted py-3">No hay matrículas registradas</td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = data.map(m => `
      <tr>
        <td>${m.id}</td>
        <td>${m.alumno}</td>
        <td>${m.codigo_curso} - ${m.curso}</td>
        <td class="text-center">${m.ciclo}</td>
        <td class="text-center">
          <span class="badge bg-${obtenerColorEstado(m.estado)}">${m.estado}</span>
        </td>
        <td class="text-center">
          <button class="btn btn-sm btn-danger" onclick="eliminarMatricula(${m.id})">
            Eliminar
          </button>
        </td>
      </tr>
    `).join("");

  } catch (err) {
    console.error("Error:", err);
    mostrarAlerta("Error al cargar matrículas", "danger");
    tbody.innerHTML = `
      <tr>
        <td colspan="6" class="text-center text-danger py-3">Error al cargar datos</td>
      </tr>
    `;
  }
}

function obtenerColorEstado(estado) {
  const colores = {
    "MATRICULADO": "primary",
    "APROBADO": "success",
    "DESAPROBADO": "danger",
    "RETIRADO": "warning"
  };
  return colores[estado] || "secondary";
}

// =====================================================
//      RENDERIZAR LISTA DE CURSOS CON CHECKBOXES
// =====================================================
function renderizarCursos(ciclo) {
  const contenedorCursos = document.getElementById("listaCursos");
  
  if (!ciclo) {
    contenedorCursos.innerHTML = '<p class="text-muted">Primero seleccione un ciclo</p>';
    return;
  }

  // Filtrar cursos por ciclo
  const cursosFiltrados = cursos.filter(c => c.ciclo == ciclo);

  if (cursosFiltrados.length === 0) {
    contenedorCursos.innerHTML = '<p class="text-muted">No hay cursos disponibles para este ciclo</p>';
    return;
  }

  contenedorCursos.innerHTML = cursosFiltrados.map(c => `
    <div class="form-check mb-2 p-2 border rounded">
      <input class="form-check-input" type="checkbox" value="${c.id}" id="curso_${c.id}">
      <label class="form-check-label w-100" for="curso_${c.id}">
        <strong>${c.codigo}</strong> - ${c.nombre}
        <small class="text-muted">(${c.creditos} créditos)</small>
      </label>
    </div>
  `).join("");
}

// =====================================================
//      ABRIR MODAL PARA NUEVA MATRÍCULA
// =====================================================
btnNuevaMatricula.addEventListener("click", async () => {
  // Cargar alumnos y cursos
  await cargarAlumnos();
  await cargarCursos();

  // Llenar select de alumnos
  const selectAlumno = document.getElementById("selectAlumno");
  selectAlumno.innerHTML = '<option value="">Seleccione un alumno...</option>' +
    alumnos.map(a => `<option value="${a.id}">${a.nombre} ${a.apellido} (DNI: ${a.dni})</option>`).join("");

  // Limpiar cursos
  document.getElementById("listaCursos").innerHTML = '<p class="text-muted">Primero seleccione un ciclo</p>';
  
  // Limpiar ciclo
  document.getElementById("inputCiclo").value = "";

  // Mostrar modal
  const modal = new bootstrap.Modal(modalMatricula);
  modal.show();
});

// =====================================================
//      CUANDO CAMBIA EL CICLO, MOSTRAR CURSOS
// =====================================================
document.getElementById("inputCiclo").addEventListener("change", (e) => {
  const ciclo = e.target.value;
  renderizarCursos(ciclo);
});

// =====================================================
//      GUARDAR MATRÍCULA (MÚLTIPLES CURSOS)
// =====================================================
formMatricula.addEventListener("submit", async (e) => {
  e.preventDefault();

  const id_alumno = parseInt(document.getElementById("selectAlumno").value);
  const ciclo = parseInt(document.getElementById("inputCiclo").value);

  // Validar alumno
  if (!id_alumno) {
    mostrarAlerta("Debe seleccionar un alumno", "warning");
    return;
  }

  // Validar ciclo
  if (!ciclo || ciclo < 1 || ciclo > 10) {
    mostrarAlerta("El ciclo debe estar entre 1 y 10", "warning");
    return;
  }

  // Obtener cursos seleccionados
  const checkboxes = document.querySelectorAll('#listaCursos input[type="checkbox"]:checked');
  const cursosSeleccionados = Array.from(checkboxes).map(cb => parseInt(cb.value));

  // Validar que haya al menos un curso seleccionado
  if (cursosSeleccionados.length === 0) {
    mostrarAlerta("Debe seleccionar al menos un curso", "warning");
    return;
  }

  console.log("Matriculando alumno:", id_alumno, "en cursos:", cursosSeleccionados, "ciclo:", ciclo);

  // Deshabilitar botón mientras se procesa
  btnGuardarMatricula.disabled = true;
  btnGuardarMatricula.textContent = "Guardando...";

  let exitosos = 0;
  let errores = 0;
  let mensajesError = [];

  // Matricular en cada curso seleccionado
  for (const id_curso of cursosSeleccionados) {
    const datos = {
      id_alumno: id_alumno,
      id_curso: id_curso,
      ciclo: ciclo
    };

    try {
      const res = await fetch(API, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(datos)
      });

      const data = await res.json();

      if (res.ok) {
        exitosos++;
      } else {
        errores++;
        mensajesError.push(data.error || "Error desconocido");
      }

    } catch (err) {
      errores++;
      mensajesError.push("Error de conexión");
    }
  }

  // Reactivar botón
  btnGuardarMatricula.disabled = false;
  btnGuardarMatricula.textContent = "Guardar Matrícula";

  // Mostrar resultado
  if (exitosos > 0 && errores === 0) {
    mostrarAlerta(`✓ ${exitosos} matrícula(s) creada(s) exitosamente`, "success");
  } else if (exitosos > 0 && errores > 0) {
    mostrarAlerta(`✓ ${exitosos} exitosa(s), ✗ ${errores} con error(es): ${mensajesError[0]}`, "warning");
  } else {
    mostrarAlerta(`Error: ${mensajesError.join(", ")}`, "danger");
  }

  // Si hubo al menos un éxito, cerrar modal y recargar
  if (exitosos > 0) {
    // Cerrar modal
    const modal = bootstrap.Modal.getInstance(modalMatricula);
    modal.hide();

    // Limpiar formulario
    formMatricula.reset();
    document.getElementById("listaCursos").innerHTML = "";

    // Recargar lista
    cargarMatriculas();
  }
});

// =====================================================
//      ELIMINAR MATRÍCULA
// =====================================================
async function eliminarMatricula(id) {
  if (!confirm("¿Está seguro de eliminar esta matrícula?")) return;

  try {
    const res = await fetch(`${API}/${id}`, {
      method: "DELETE"
    });

    const data = await res.json();

    if (!res.ok) {
      mostrarAlerta(data.error || "Error al eliminar", "danger");
      return;
    }

    mostrarAlerta("Matrícula eliminada correctamente", "success");
    cargarMatriculas();

  } catch (err) {
    console.error("Error:", err);
    mostrarAlerta("Error al eliminar matrícula", "danger");
  }
}

// =====================================================
//      INICIALIZAR
// =====================================================
cargarMatriculas();