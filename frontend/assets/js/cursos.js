const API = "http://127.0.0.1:5000/api/cursos";

const tbody = document.getElementById("tablaCursos");
const modalEl = document.getElementById("modalCurso");
const modal = new bootstrap.Modal(modalEl);
const form = document.getElementById("formCurso");

// Inputs del formulario
const codigoInput = document.getElementById("codigo");
const nombreInput = document.getElementById("nombre");
const creditosInput = document.getElementById("creditos");
const cicloInput = document.getElementById("ciclo");
const tituloModal = document.querySelector("#modalCurso .modal-title");

// Variable de estado para saber si editamos
let cursoIdEditar = null;

// =====================================================
// 1. LISTAR (READ)
// =====================================================
async function cargarCursos() {
  tbody.innerHTML = '<tr><td colspan="6" class="text-center py-3">Cargando...</td></tr>';
  
  try {
    const res = await fetch(API);
    const data = await res.json();

    if (!data.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No hay cursos registrados.</td></tr>';
      return;
    }

    tbody.innerHTML = data.map(c => `
      <tr class="align-middle">
        <td>${c.id}</td>
        <td class="fw-bold text-primary">${c.codigo}</td>
        <td>${c.nombre}</td>
        <td>${c.creditos}</td>
        <td>Ciclo ${c.ciclo}</td>
        <td>
          <button class="btn btn-sm btn-warning me-1" onclick="abrirEditar(${c.id})">✏️ Editar</button>
          <button class="btn btn-sm btn-danger" onclick="eliminarCurso(${c.id})">🗑️ Eliminar</button>
        </td>
      </tr>
    `).join("");

  } catch (error) {
    console.error(error);
    tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Error de conexión</td></tr>';
  }
}

// =====================================================
// 2. PREPARAR EL MODAL (NUEVO vs EDITAR)
// =====================================================

// Botón "+ Nuevo Curso" (Desde el HTML debes asegurarte que este botón no abra el modal directo, sino que llame a esta función o limpiamos al abrir)
modalEl.addEventListener('show.bs.modal', event => {
  // Si el botón que abrió el modal NO es de edición, limpiamos
  if (!event.relatedTarget || !event.relatedTarget.classList.contains('btn-warning')) {
    // Es un "Nuevo Curso"
    if(!cursoIdEditar) {
        form.reset();
        tituloModal.textContent = "Registrar Nuevo Curso";
    }
  }
});

// Función global para abrir edición
window.abrirEditar = async (id) => {
  cursoIdEditar = id; // Guardamos el ID
  tituloModal.textContent = "Editar Curso";
  
  try {
    const res = await fetch(`${API}/${id}`);
    const data = await res.json();
    
    // Llenar campos
    codigoInput.value = data.codigo;
    nombreInput.value = data.nombre;
    creditosInput.value = data.creditos;
    cicloInput.value = data.ciclo;
    
    modal.show();
  } catch (error) {
    alert("Error al cargar los datos del curso");
  }
};

// Reiniciar variable al cerrar modal
modalEl.addEventListener('hidden.bs.modal', () => {
  cursoIdEditar = null;
  form.reset();
});

// =====================================================
// 3. GUARDAR (CREATE / UPDATE)
// =====================================================
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const curso = {
    codigo: codigoInput.value.trim(),
    nombre: nombreInput.value.trim(),
    creditos: parseInt(creditosInput.value),
    ciclo: parseInt(cicloInput.value)
  };

  // Decidir si es POST o PUT
  const method = cursoIdEditar ? "PUT" : "POST";
  const url = cursoIdEditar ? `${API}/${cursoIdEditar}` : API;

  try {
    const res = await fetch(url, {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(curso)
    });

    const data = await res.json();

    if (!res.ok) throw new Error(data.error || "Error al procesar");

    // ÉXITO
    alert(cursoIdEditar ? "Curso actualizado correctamente" : "Curso creado correctamente");
    modal.hide();
    cargarCursos(); // <-- IMPORTANTE: Recargar la tabla

  } catch (error) {
    alert("Error: " + error.message);
  }
});

// =====================================================
// 4. ELIMINAR (DELETE)
// =====================================================
window.eliminarCurso = async (id) => {
  if (!confirm("¿Estás seguro de eliminar este curso?")) return;

  try {
    const res = await fetch(`${API}/${id}`, { method: "DELETE" });
    if (res.ok) {
      alert("Curso eliminado");
      cargarCursos();
    } else {
      alert("No se pudo eliminar (tal vez tiene alumnos matriculados)");
    }
  } catch (error) {
    console.error(error);
  }
};

// Iniciar
cargarCursos();