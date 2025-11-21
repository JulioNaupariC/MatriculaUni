const API = "http://localhost:5000/api/cursos";

const tbody = document.getElementById("tablaCursos");
const alertContainer = document.getElementById("alertContainer");

const modal = new bootstrap.Modal(document.getElementById("modalCurso"));
const form = document.getElementById("formCurso");

const codigoInput = document.getElementById("codigo");
const nombreInput = document.getElementById("nombre");
const creditosInput = document.getElementById("creditos");
const cicloInput = document.getElementById("ciclo");


// =====================================================
//    LISTAR CURSOS
// =====================================================
async function cargarCursos() {
  tbody.innerHTML = `
    <tr>
      <td colspan="5" class="text-center text-muted py-3">Cargando...</td>
    </tr>
  `;

  try {
    const res = await fetch(API);
    const data = await res.json();

    tbody.innerHTML = "";

    if (!data.length) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" class="text-center py-4 text-muted">No hay cursos registrados.</td>
        </tr>
      `;
      return;
    }

    data.forEach(c => {
      tbody.innerHTML += `
        <tr>
          <td>${c.id}</td>
          <td>${c.codigo || '-'}</td>
          <td>${c.nombre}</td>
          <td>${c.creditos || '-'}</td>
          <td>${c.ciclo}</td>
        </tr>
      `;
    });

  } catch (error) {
    mostrarAlerta("No se pudo cargar los cursos.", "danger");
  }
}


// =====================================================
//    ALERTAS
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
//    CREAR CURSO
// =====================================================
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const nuevoCurso = {
    codigo: codigoInput.value.trim(),
    nombre: nombreInput.value.trim(),
    creditos: parseInt(creditosInput.value),
    ciclo: parseInt(cicloInput.value)
  };

  // Validación básica
  if (!nuevoCurso.codigo) {
    mostrarAlerta("El código es obligatorio", "warning");
    return;
  }

  if (!nuevoCurso.nombre) {
    mostrarAlerta("El nombre es obligatorio", "warning");
    return;
  }

  if (isNaN(nuevoCurso.creditos) || nuevoCurso.creditos < 1 || nuevoCurso.creditos > 5) {
    mostrarAlerta("Los créditos deben estar entre 1 y 5", "warning");
    return;
  }

  if (isNaN(nuevoCurso.ciclo) || nuevoCurso.ciclo < 1 || nuevoCurso.ciclo > 10) {
    mostrarAlerta("El ciclo debe estar entre 1 y 10", "warning");
    return;
  }

  try {
    const res = await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(nuevoCurso)
    });

    const data = await res.json();

    if (!res.ok) {
      mostrarAlerta(data.errores ? data.errores.join("<br>") : data.error, "warning");
      return;
    }

    mostrarAlerta("Curso registrado correctamente.");
    modal.hide();
    form.reset();
    cargarCursos();

  } catch (error) {
    console.error("Error:", error);
    mostrarAlerta("Error al registrar curso.", "danger");
  }
});


// =====================================================
//    INICIAR
// =====================================================
cargarCursos();