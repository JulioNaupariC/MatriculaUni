const API = "http://127.0.0.1:5000/api/evaluaciones";

const tbody = document.getElementById("tbodyEvaluaciones");
const modalEl = document.getElementById("modalEvaluacion");
const modal = new bootstrap.Modal(modalEl);
const form = document.getElementById("formEvaluacion");
const selectMatricula = document.getElementById("selectMatricula");
const inputNota = document.getElementById("inputNota");
const tituloModal = document.querySelector("#modalEvaluacion .modal-title");

let evaluacionIdEditar = null;

// ==========================================
//  LISTAR
// ==========================================
async function cargarEvaluaciones() {
  tbody.innerHTML = '<tr><td colspan="7" class="text-center">Cargando...</td></tr>';
  try {
    const res = await fetch(API);
    const data = await res.json();
    
    if(!data.length) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No hay evaluaciones registradas</td></tr>';
      return;
    }

    tbody.innerHTML = data.map(e => `
      <tr class="align-middle">
        <td>${e.id}</td>
        <td>${e.alumno}</td>
        <td>${e.curso}</td>
        <td class="text-center">${e.ciclo}</td>
        <td class="text-center fw-bold">${e.nota}</td>
        <td class="text-center"><span class="badge bg-${e.aprobado?'success':'danger'}">${e.aprobado?'APROBADO':'DESAPROBADO'}</span></td>
        <td class="text-center">
          <button class="btn btn-sm btn-warning" onclick="abrirEditar(${e.id}, ${e.nota})">✏️</button>
          <button class="btn btn-sm btn-danger" onclick="eliminarEvaluacion(${e.id})">🗑️</button>
        </td>
      </tr>
    `).join("");
  } catch (err) { console.error(err); }
}

// ==========================================
//  CARGAR PENDIENTES
// ==========================================
async function cargarPendientes() {
    const res = await fetch(`${API}/pendientes`);
    const data = await res.json();
    
    if(data.length === 0) {
        selectMatricula.innerHTML = '<option value="">No hay alumnos pendientes</option>';
    } else {
        selectMatricula.innerHTML = '<option value="">Seleccione alumno...</option>' + 
            data.map(m => `<option value="${m.id_matricula}">${m.alumno} - ${m.curso} (Ciclo ${m.ciclo})</option>`).join("");
    }
}

// ==========================================
//  NUEVA EVALUACION
// ==========================================
document.getElementById("btnNuevaEvaluacion").addEventListener("click", async () => {
    evaluacionIdEditar = null;
    tituloModal.textContent = "Registrar Evaluación";
    form.reset();
    selectMatricula.disabled = false;
    document.getElementById("notaFeedback").textContent = ""; // Limpiar feedback visual
    
    await cargarPendientes();
    modal.show();
});

// ==========================================
//  EDITAR EVALUACION
// ==========================================
window.abrirEditar = (id, notaActual) => {
    evaluacionIdEditar = id;
    tituloModal.textContent = "Editar Nota";
    
    // Al editar, no cargamos pendientes porque ya está evaluado. 
    // Ponemos una opción "dummy" para que se vea bonito.
    selectMatricula.innerHTML = '<option selected>Alumno (Bloqueado)</option>';
    selectMatricula.disabled = true;
    
    inputNota.value = notaActual;
    // Disparar evento input para actualizar color (aprobado/desaprobado)
    inputNota.dispatchEvent(new Event('input'));
    
    modal.show();
};

// ==========================================
//  GUARDAR
// ==========================================
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const url = evaluacionIdEditar ? `${API}/${evaluacionIdEditar}` : API;
    const method = evaluacionIdEditar ? "PUT" : "POST";
    
    const body = {
        nota: inputNota.value
    };

    // Solo enviamos id_matricula si es nuevo registro
    if(!evaluacionIdEditar) {
        body.id_matricula = selectMatricula.value;
    }

    try {
        const res = await fetch(url, {
            method: method, 
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(body)
        });
        const data = await res.json();
        
        if(!res.ok) throw new Error(data.error);
        
        alert("Guardado correctamente");
        modal.hide();
        cargarEvaluaciones();
    } catch(err) {
        alert(err.message);
    }
});

// ==========================================
//  ELIMINAR
// ==========================================
window.eliminarEvaluacion = async (id) => {
    if(!confirm("¿Eliminar evaluación? La matrícula volverá a estado MATRICULADO.")) return;
    try {
        await fetch(`${API}/${id}`, { method: "DELETE" });
        cargarEvaluaciones();
    } catch(e) { alert("Error al eliminar"); }
};

// Visual: Color nota
inputNota.addEventListener("input", (e) => {
    const val = parseFloat(e.target.value);
    const feedback = document.getElementById("notaFeedback");
    if(!isNaN(val)) {
        feedback.textContent = val >= 10.5 ? "✅ APROBADO" : "❌ DESAPROBADO";
        feedback.className = val >= 10.5 ? "text-success small fw-bold" : "text-danger small fw-bold";
    } else {
        feedback.textContent = "";
    }
});

cargarEvaluaciones();