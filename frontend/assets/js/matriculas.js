const API = "http://127.0.0.1:5000/api/matriculas";
const API_ALUMNOS = "http://127.0.0.1:5000/api/alumnos";
const API_CURSOS = "http://127.0.0.1:5000/api/cursos";

const tbody = document.getElementById("tbodyMatriculas");
const modalEl = document.getElementById("modalMatricula");
const modal = new bootstrap.Modal(modalEl);
const form = document.getElementById("formMatricula");

// Elementos del Formulario
const selectAlumno = document.getElementById("selectAlumno");
const inputCiclo = document.getElementById("inputCiclo");
const divCursosContainer = document.getElementById("listaCursos"); // Contenedor viejo, lo usaremos para poner el select
const btnGuardar = document.getElementById("btnGuardarMatricula");
const tituloModal = document.querySelector("#modalMatricula .modal-title");

let matriculaIdEditar = null;

// Reemplazar el contenedor de checkboxes por un SELECT dinámicamente o asegurarse que en el HTML exista un container limpio
// Vamos a inyectar un Select en lugar de los checkboxes
divCursosContainer.innerHTML = `
    <label class="form-label fw-semibold">Seleccionar Curso</label>
    <select id="selectCurso" class="form-select" required>
        <option value="">Seleccione ciclo primero...</option>
    </select>
`;
const selectCurso = document.getElementById("selectCurso");


// ==========================================
//  LISTAR
// ==========================================
async function cargarMatriculas() {
  tbody.innerHTML = '<tr><td colspan="6" class="text-center">Cargando...</td></tr>';
  try {
    const res = await fetch(API);
    const data = await res.json();
    
    if(!data.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No hay matrículas</td></tr>';
      return;
    }

    tbody.innerHTML = data.map(m => `
      <tr class="align-middle">
        <td>${m.id}</td>
        <td>${m.alumno}</td>
        <td>${m.curso}</td>
        <td class="text-center">${m.ciclo}</td>
        <td class="text-center"><span class="badge bg-${getColor(m.estado)}">${m.estado}</span></td>
        <td class="text-center">
          <button class="btn btn-sm btn-warning" onclick="abrirEditar(${m.id})">✏️</button>
          <button class="btn btn-sm btn-danger" onclick="eliminarMatricula(${m.id})">🗑️</button>
        </td>
      </tr>
    `).join("");
  } catch (err) { console.error(err); }
}

function getColor(estado) {
    if(estado === 'APROBADO') return 'success';
    if(estado === 'DESAPROBADO') return 'danger';
    return 'primary'; 
}

// ==========================================
//  CARGAS DE DATOS (Combos)
// ==========================================
async function cargarAlumnosCombo() {
    const res = await fetch(API_ALUMNOS);
    const data = await res.json();
    selectAlumno.innerHTML = '<option value="">Seleccione alumno...</option>' + 
        data.map(a => `<option value="${a.id}">${a.apellido} ${a.nombre}</option>`).join("");
}

async function cargarCursosCombo(ciclo) {
    selectCurso.innerHTML = '<option value="">Cargando...</option>';
    if(!ciclo) {
        selectCurso.innerHTML = '<option value="">Seleccione ciclo primero</option>';
        return;
    }
    
    const res = await fetch(API_CURSOS);
    const data = await res.json();
    const filtrados = data.filter(c => c.ciclo == ciclo);
    
    if(filtrados.length === 0) {
        selectCurso.innerHTML = '<option value="">No hay cursos en este ciclo</option>';
    } else {
        selectCurso.innerHTML = '<option value="">Seleccione un curso...</option>' + 
            filtrados.map(c => `<option value="${c.id}">${c.codigo} - ${c.nombre}</option>`).join("");
    }
}

// ==========================================
//  EVENTOS FORMULARIO
// ==========================================
document.getElementById("btnNuevaMatricula").addEventListener("click", async () => {
    matriculaIdEditar = null;
    tituloModal.textContent = "Nueva Matrícula";
    form.reset();
    selectAlumno.disabled = false;
    
    await cargarAlumnosCombo();
    selectCurso.innerHTML = '<option value="">Seleccione ciclo primero</option>';
    modal.show();
});

inputCiclo.addEventListener("change", (e) => {
    cargarCursosCombo(e.target.value);
});

// ==========================================
//  EDITAR
// ==========================================
window.abrirEditar = async (id) => {
    matriculaIdEditar = id;
    tituloModal.textContent = "Editar Matrícula";
    selectAlumno.disabled = true; // No cambiar alumno al editar (regla de negocio común)

    try {
        const res = await fetch(`${API}/${id}`);
        const data = await res.json();
        
        await cargarAlumnosCombo();
        selectAlumno.value = data.id_alumno;
        inputCiclo.value = data.ciclo;
        
        // Cargar cursos del ciclo del alumno y seleccionar el actual
        await cargarCursosCombo(data.ciclo);
        selectCurso.value = data.id_curso;

        modal.show();
    } catch(e) { 
        console.error(e);
        alert("Error al cargar datos para edición"); 
    }
};

// ==========================================
//  GUARDAR (POST / PUT)
// ==========================================
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const alumnoId = selectAlumno.value;
    const cicloVal = inputCiclo.value;
    const cursoId = selectCurso.value;

    if(!alumnoId || !cicloVal || !cursoId) {
        alert("Complete todos los campos");
        return;
    }

    const payload = {
        id_alumno: alumnoId,
        id_curso: cursoId,
        ciclo: cicloVal
    };

    const url = matriculaIdEditar ? `${API}/${matriculaIdEditar}` : API;
    const method = matriculaIdEditar ? "PUT" : "POST";

    try {
        const res = await fetch(url, {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if(!res.ok) throw new Error(data.error || "Error al procesar");

        alert(matriculaIdEditar ? "Matrícula actualizada" : "Matrícula creada");
        modal.hide();
        cargarMatriculas();

    } catch (err) {
        alert(err.message);
    }
});

// ==========================================
//  ELIMINAR
// ==========================================
window.eliminarMatricula = async (id) => {
    if(!confirm("¿Eliminar esta matrícula?")) return;
    try {
        await fetch(`${API}/${id}`, { method: "DELETE" });
        cargarMatriculas();
    } catch(e) { alert("Error al eliminar"); }
};

cargarMatriculas();