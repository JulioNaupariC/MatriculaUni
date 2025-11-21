const API = "http://127.0.0.1:5000/api/evaluaciones";
const API_PENDIENTES = "http://127.0.0.1:5000/api/evaluaciones/pendientes";

const tbody = document.getElementById("tbodyEvaluaciones");
const alertContainer = document.getElementById("alertContainer");
const btnNuevaEvaluacion = document.getElementById("btnNuevaEvaluacion");
const modalEvaluacion = document.getElementById("modalEvaluacion");
const formEvaluacion = document.getElementById("formEvaluacion");

let matriculasPendientes = [];

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
//      CARGAR EVALUACIONES
// =====================================================
async function cargarEvaluaciones() {
  tbody.innerHTML = `
    <tr>
      <td colspan="7" class="text-center py-3">Cargando...</td>
    </tr>
  `;

  try {
    const res = await fetch(API);
    if (!res.ok) {
      throw new Error("Error al cargar evaluaciones");
    }

    const data = await res.json();

    if (!data.length) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" class="text-center text-muted py-3">No hay evaluaciones registradas</td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = data.map(e => `
      <tr>
        <td>${e.id}</td>
        <td>${e.alumno}</td>
        <td>${e.codigo_curso} - ${e.curso}</td>
        <td class="text-center">${e.ciclo}</td>
        <td class="text-center fw-bold">${e.nota}</td>
        <td class="text-center">
          <span class="badge bg-${e.aprobado ? 'success' : 'danger'}">
            ${e.aprobado ? 'APROBADO' : 'DESAPROBADO'}
          </span>
        </td>
        <td class="text-center">
          <button class="btn btn-sm btn-danger" onclick="eliminarEvaluacion(${e.id})">
            Eliminar
          </button>
        </td>
      </tr>
    `).join("");

  } catch (err) {
    console.error("Error:", err);
    mostrarAlerta("Error al cargar evaluaciones", "danger");
    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="text-center text-danger py-3">Error al cargar datos</td>
      </tr>
    `;
  }
}

// =====================================================
//      CARGAR MATRÍCULAS PENDIENTES
// =====================================================
async function cargarPendientes() {
  try {
    const res = await fetch(API_PENDIENTES);
    if (!res.ok) throw new Error("Error al cargar pendientes");
    matriculasPendientes = await res.json();
    return matriculasPendientes;
  } catch (err) {
    console.error("Error cargando pendientes:", err);
    return [];
  }
}

// =====================================================
//      ABRIR MODAL PARA NUEVA EVALUACIÓN
// =====================================================
btnNuevaEvaluacion.addEventListener("click", async () => {
  // Cargar matrículas pendientes
  const pendientes = await cargarPendientes();

  // Llenar select de matrículas
  const selectMatricula = document.getElementById("selectMatricula");
  
  if (pendientes.length === 0) {
    selectMatricula.innerHTML = '<option value="">No hay matrículas pendientes de evaluación</option>';
    mostrarAlerta("No hay matrículas pendientes de evaluación", "info");
    return;
  }

  selectMatricula.innerHTML = '<option value="">Seleccione una matrícula...</option>' +
    pendientes.map(m => `
      <option value="${m.id_matricula}" 
              data-alumno="${m.alumno}" 
              data-curso="${m.codigo_curso} - ${m.curso}"
              data-ciclo="${m.ciclo}">
        ${m.alumno} - ${m.codigo_curso} (${m.curso}) - Ciclo ${m.ciclo}
      </option>
    `).join("");

  // Limpiar campos
  document.getElementById("inputNota").value = "";
  document.getElementById("infoAlumno").textContent = "";
  document.getElementById("infoCurso").textContent = "";
  document.getElementById("infoCiclo").textContent = "";

  // Mostrar modal
  const modal = new bootstrap.Modal(modalEvaluacion);
  modal.show();
});

// =====================================================
//      CUANDO SELECCIONA UNA MATRÍCULA
// =====================================================
document.getElementById("selectMatricula").addEventListener("change", (e) => {
  const option = e.target.selectedOptions[0];
  
  if (option.value) {
    document.getElementById("infoAlumno").textContent = option.dataset.alumno;
    document.getElementById("infoCurso").textContent = option.dataset.curso;
    document.getElementById("infoCiclo").textContent = option.dataset.ciclo;
  } else {
    document.getElementById("infoAlumno").textContent = "";
    document.getElementById("infoCurso").textContent = "";
    document.getElementById("infoCiclo").textContent = "";
  }
});

// =====================================================
//      GUARDAR EVALUACIÓN
// =====================================================
formEvaluacion.addEventListener("submit", async (e) => {
  e.preventDefault();

  const id_matricula = parseInt(document.getElementById("selectMatricula").value);
  const nota = parseFloat(document.getElementById("inputNota").value);

  // Validar
  if (!id_matricula) {
    mostrarAlerta("Debe seleccionar una matrícula", "warning");
    return;
  }

  if (isNaN(nota) || nota < 0 || nota > 20) {
    mostrarAlerta("La nota debe estar entre 0 y 20", "warning");
    return;
  }

  // Preparar datos
  const datos = {
    id_matricula: id_matricula,
    nota: nota
  };

  console.log("Enviando evaluación:", datos);

  try {
    const res = await fetch(API, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(datos)
    });

    const data = await res.json();

    if (!res.ok) {
      mostrarAlerta(data.error || "Error al crear evaluación", "danger");
      return;
    }

    const estado = data.aprobado ? "APROBADO ✓" : "DESAPROBADO ✗";
    mostrarAlerta(`Evaluación registrada: ${estado} (Nota: ${nota})`, data.aprobado ? "success" : "warning");
    
    // Cerrar modal
    const modal = bootstrap.Modal.getInstance(modalEvaluacion);
    modal.hide();

    // Limpiar formulario
    formEvaluacion.reset();

    // Recargar lista
    cargarEvaluaciones();

  } catch (err) {
    console.error("Error:", err);
    mostrarAlerta("Error en la comunicación con el servidor", "danger");
  }
});

// =====================================================
//      ELIMINAR EVALUACIÓN
// =====================================================
async function eliminarEvaluacion(id) {
  if (!confirm("¿Está seguro de eliminar esta evaluación?\nLa matrícula volverá a estado MATRICULADO.")) return;

  try {
    const res = await fetch(`${API}/${id}`, {
      method: "DELETE"
    });

    const data = await res.json();

    if (!res.ok) {
      mostrarAlerta(data.error || "Error al eliminar", "danger");
      return;
    }

    mostrarAlerta("Evaluación eliminada correctamente", "success");
    cargarEvaluaciones();

  } catch (err) {
    console.error("Error:", err);
    mostrarAlerta("Error al eliminar evaluación", "danger");
  }
}

// =====================================================
//      VALIDACIÓN EN TIEMPO REAL DE LA NOTA
// =====================================================
document.getElementById("inputNota").addEventListener("input", (e) => {
  const nota = parseFloat(e.target.value);
  const feedback = document.getElementById("notaFeedback");
  
  if (isNaN(nota)) {
    feedback.textContent = "";
    feedback.className = "";
  } else if (nota < 0 || nota > 20) {
    feedback.textContent = "⚠️ La nota debe estar entre 0 y 20";
    feedback.className = "text-danger small";
  } else if (nota >= 10.5) {
    feedback.textContent = "✓ APROBADO";
    feedback.className = "text-success fw-bold small";
  } else {
    feedback.textContent = "✗ DESAPROBADO";
    feedback.className = "text-danger fw-bold small";
  }
});

// =====================================================
//      INICIALIZAR
// =====================================================
cargarEvaluaciones();