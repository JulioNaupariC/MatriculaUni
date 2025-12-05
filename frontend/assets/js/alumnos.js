const API = "http://127.0.0.1:5000/api/alumnos";

const tbody = document.getElementById("tablaAlumnos");
const modalEl = document.getElementById("modalAlumno");
const modal = new bootstrap.Modal(modalEl);
const form = document.getElementById("formAlumno");
const tituloModal = document.getElementById("modalTitulo");

// Inputs
const nombreInput = document.getElementById("nombre");
const apellidoInput = document.getElementById("apellido");
const edadInput = document.getElementById("edad");
const dniInput = document.getElementById("dni");
const correoInput = document.getElementById("correo");
const telefonoInput = document.getElementById("telefono");
const cicloInput = document.getElementById("ciclo");

let alumnoIdEditar = null; // Variable clave

// ==========================================
//  LISTAR
// ==========================================
async function cargarAlumnos() {
  tbody.innerHTML = '<tr><td colspan="8" class="text-center">Cargando...</td></tr>';
  try {
    const res = await fetch(API);
    const data = await res.json();
    
    if (!data.length) {
      tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No hay alumnos</td></tr>';
      return;
    }

    tbody.innerHTML = data.map(a => `
      <tr class="align-middle">
        <td>${a.id}</td>
        <td>${a.apellido}, ${a.nombre}</td>
        <td>${a.dni}</td>
        <td>${a.edad}</td>
        <td>${a.correo || '-'}</td>
        <td>${a.telefono || '-'}</td>
        <td class="text-center"><span class="badge bg-info text-dark">${a.ciclo_actual}</span></td>
        <td class="text-center">
          <button class="btn btn-sm btn-warning me-1" onclick="abrirEditar(${a.id})">✏️</button>
          <button class="btn btn-sm btn-danger" onclick="eliminarAlumno(${a.id})">🗑️</button>
        </td>
      </tr>
    `).join("");
  } catch (error) {
    tbody.innerHTML = '<tr><td colspan="8" class="text-center text-danger">Error de conexión</td></tr>';
  }
}

// ==========================================
//  PREPARAR EDICIÓN
// ==========================================
window.abrirEditar = async (id) => {
  alumnoIdEditar = id;
  tituloModal.textContent = "Editar Alumno";

  try {
    const res = await fetch(`${API}/${id}`);
    const data = await res.json();

    nombreInput.value = data.nombre;
    apellidoInput.value = data.apellido;
    edadInput.value = data.edad;
    dniInput.value = data.dni;
    correoInput.value = data.correo;
    telefonoInput.value = data.telefono;
    cicloInput.value = data.ciclo_actual;

    modal.show();
  } catch (error) {
    alert("Error al cargar alumno");
  }
};

// Limpiar al cerrar o al abrir como nuevo
modalEl.addEventListener('hidden.bs.modal', () => {
  alumnoIdEditar = null;
  form.reset();
  tituloModal.textContent = "Nuevo Alumno";
});

// ==========================================
//  GUARDAR (CREATE / UPDATE)
// ==========================================
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const alumno = {
    nombre: nombreInput.value,
    apellido: apellidoInput.value,
    edad: parseInt(edadInput.value),
    dni: dniInput.value,
    correo: correoInput.value,
    telefono: telefonoInput.value,
    ciclo_actual: parseInt(cicloInput.value)
  };

  // Lógica Post/Put
  const method = alumnoIdEditar ? "PUT" : "POST";
  const url = alumnoIdEditar ? `${API}/${alumnoIdEditar}` : API;

  try {
    const res = await fetch(url, {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(alumno)
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.errores ? data.errores.join("\n") : data.error);

    alert("Guardado correctamente");
    modal.hide();
    cargarAlumnos(); // Refrescar tabla

  } catch (error) {
    alert(error.message);
  }
});

// ==========================================
//  ELIMINAR
// ==========================================
window.eliminarAlumno = async (id) => {
  if (!confirm("¿Seguro de eliminar?")) return;
  try {
    await fetch(`${API}/${id}`, { method: "DELETE" });
    cargarAlumnos();
  } catch (e) { alert("Error al eliminar"); }
};

cargarAlumnos();