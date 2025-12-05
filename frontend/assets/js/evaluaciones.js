const API = "http://127.0.0.1:5000/api/evaluaciones";

const tbody = document.getElementById("tbodyEvaluaciones");
const modalEl = document.getElementById("modalEvaluacion");
const modal = new bootstrap.Modal(modalEl);
const form = document.getElementById("formEvaluacion");
const tituloModal = document.getElementById("tituloModal");

const divSelectMatricula = document.getElementById("divSelectMatricula");
const selectMatricula = document.getElementById("selectMatricula");
const inputNota = document.getElementById("inputNota");
const previewEstado = document.getElementById("previewEstado");
const textoEstado = document.getElementById("textoEstado");

let evaluacionIdEditar = null;

// ==========================================
//  LISTAR EVALUACIONES AGRUPADAS: CICLO → ALUMNO → CURSOS
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

    // Agrupar por ciclo_matricula → alumno
    const porCiclo = {};
    data.forEach(e => {
      const ciclo = e.ciclo_matricula;
      const alumno = e.alumno;
      
      if(!porCiclo[ciclo]) porCiclo[ciclo] = {};
      if(!porCiclo[ciclo][alumno]) porCiclo[ciclo][alumno] = [];
      
      porCiclo[ciclo][alumno].push(e);
    });

    // Ordenar ciclos de mayor a menor
    const ciclosOrdenados = Object.keys(porCiclo).sort((a, b) => b - a);

    let html = '';
    ciclosOrdenados.forEach(ciclo => {
      const alumnos = porCiclo[ciclo];
      const totalEvaluaciones = Object.values(alumnos).reduce((sum, cursos) => sum + cursos.length, 0);
      
      // Calcular promedio general del ciclo
      const todasLasNotas = Object.values(alumnos).flat();
      const promedioCiclo = (todasLasNotas.reduce((sum, e) => sum + parseFloat(e.nota), 0) / todasLasNotas.length).toFixed(2);
      
      // Encabezado del ciclo
      html += `
        <tr class="table-primary">
          <td colspan="7" class="fw-bold fs-5 py-3">
            📘 CICLO ${ciclo} 
            <span class="badge bg-primary ms-2">${totalEvaluaciones} evaluaciones</span>
            <span class="badge bg-info ms-2">Promedio: ${promedioCiclo}</span>
          </td>
        </tr>
      `;

      // Por cada alumno en el ciclo
      Object.keys(alumnos).sort().forEach(alumno => {
        const evaluaciones = alumnos[alumno];
        
        // Calcular promedio del alumno
        const promedioAlumno = (evaluaciones.reduce((sum, e) => sum + parseFloat(e.nota), 0) / evaluaciones.length).toFixed(2);
        const aprobados = evaluaciones.filter(e => e.aprobado).length;
        const desaprobados = evaluaciones.length - aprobados;
        
        // Encabezado del alumno
        html += `
          <tr class="table-light">
            <td colspan="7" class="fw-bold py-2 ps-4">
              👤 ${alumno} 
              <span class="badge bg-secondary ms-2">${evaluaciones.length} cursos</span>
              <span class="badge bg-info ms-2">Promedio: ${promedioAlumno}</span>
              <span class="badge bg-success ms-2">✓ ${aprobados}</span>
              <span class="badge bg-danger ms-2">✗ ${desaprobados}</span>
            </td>
          </tr>
        `;

        // Evaluaciones del alumno
        evaluaciones.forEach(e => {
          const badgeEstado = e.aprobado ? 'success' : 'danger';
          const textoEstado = e.aprobado ? 'APROBADO' : 'DESAPROBADO';
          
          html += `
            <tr class="align-middle">
              <td class="ps-5">${e.id}</td>
              <td class="text-start ps-5">${e.alumno}</td>
              <td class="text-start">${e.codigo} - ${e.curso}</td>
              <td><span class="badge bg-primary">${e.ciclo_matricula}</span></td>
              <td class="fw-bold ${e.aprobado ? 'text-success' : 'text-danger'}">${parseFloat(e.nota).toFixed(2)}</td>
              <td><span class="badge bg-${badgeEstado}">${textoEstado}</span></td>
              <td>
                <button class="btn btn-sm btn-warning" onclick="abrirEditar(${e.id})" title="Editar">
                  ✏️
                </button>
                <button class="btn btn-sm btn-danger" onclick="eliminarEvaluacion(${e.id})" title="Eliminar">
                  🗑️
                </button>
              </td>
            </tr>
          `;
        });
      });
    });

    tbody.innerHTML = html;
  } catch (err) { 
    console.error(err);
    tbody.innerHTML = '<tr><td colspan="7" class="text-center text-danger">❌ Error al cargar</td></tr>';
  }
}

// ==========================================
//  CARGAR MATRÍCULAS PENDIENTES
// ==========================================
async function cargarMatriculasPendientes() {
    try {
        const res = await fetch(`${API}/pendientes`);
        const data = await res.json();
        
        if(!data.length) {
            selectMatricula.innerHTML = '<option value="">No hay matrículas pendientes de evaluar</option>';
            return;
        }

        // Agrupar por ciclo
        const porCiclo = {};
        data.forEach(m => {
            const ciclo = m.ciclo_matricula;
            if(!porCiclo[ciclo]) porCiclo[ciclo] = [];
            porCiclo[ciclo].push(m);
        });

        // Crear options agrupados
        let html = '<option value="">-- Seleccione una matrícula --</option>';
        
        Object.keys(porCiclo).sort((a, b) => b - a).forEach(ciclo => {
            html += `<optgroup label="📘 CICLO ${ciclo}">`;
            porCiclo[ciclo].forEach(m => {
                const arrastre = m.ciclo_original !== m.ciclo_matricula ? ` (Arrastre Ciclo ${m.ciclo_original})` : '';
                html += `<option value="${m.id_matricula}">${m.alumno} - ${m.codigo} ${m.curso}${arrastre}</option>`;
            });
            html += '</optgroup>';
        });

        selectMatricula.innerHTML = html;
        
    } catch(err) {
        console.error(err);
        selectMatricula.innerHTML = '<option value="">Error al cargar</option>';
    }
}

// ==========================================
//  PREVIEW ESTADO AL CAMBIAR NOTA
// ==========================================
inputNota.addEventListener("input", (e) => {
    const nota = parseFloat(e.target.value);
    
    if(isNaN(nota) || nota < 0 || nota > 20) {
        previewEstado.classList.add("d-none");
        return;
    }

    const aprobado = nota >= 10.5;
    previewEstado.classList.remove("d-none");
    
    if(aprobado) {
        previewEstado.className = "alert alert-success";
        textoEstado.innerHTML = `Nota: <strong>${nota.toFixed(2)}</strong> - ✅ <strong>APROBADO</strong>`;
    } else {
        previewEstado.className = "alert alert-danger";
        textoEstado.innerHTML = `Nota: <strong>${nota.toFixed(2)}</strong> - ❌ <strong>DESAPROBADO</strong>`;
    }
});

// ==========================================
//  ABRIR MODAL NUEVA EVALUACIÓN
// ==========================================
document.getElementById("btnNuevaEvaluacion").addEventListener("click", async () => {
    evaluacionIdEditar = null;
    tituloModal.textContent = "📝 Nueva Evaluación";
    form.reset();
    divSelectMatricula.style.display = "block";
    
    // ✅ SOLUCIÓN: Restaurar el atributo required cuando está visible
    selectMatricula.setAttribute('required', 'required');
    
    previewEstado.classList.add("d-none");
    
    await cargarMatriculasPendientes();
    modal.show();
});

// ==========================================
//  ABRIR MODAL EDITAR (CORREGIDO ✅)
// ==========================================
window.abrirEditar = async (id) => {
    evaluacionIdEditar = id;
    tituloModal.textContent = "✏️ Editar Evaluación";
    
    try {
        // ✅ CORREGIDO: URL correcta sin ../
        const res = await fetch(`${API}/${id}`);
        
        if(!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.error || "No se pudo cargar la evaluación");
        }
        
        const data = await res.json();
        
        // Ocultar select de matrícula (no se puede cambiar)
        divSelectMatricula.style.display = "none";
        
        // ✅ SOLUCIÓN: Quitar el atributo required cuando está oculto
        selectMatricula.removeAttribute('required');
        
        // Cargar nota
        inputNota.value = data.nota;
        inputNota.dispatchEvent(new Event('input')); // Trigger preview
        
        modal.show();
    } catch(err) {
        console.error("Error al cargar evaluación:", err);
        alert("❌ Error al cargar evaluación: " + err.message);
    }
};

// ==========================================
//  GUARDAR EVALUACIÓN
// ==========================================
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const nota = parseFloat(inputNota.value);
    
    if(isNaN(nota) || nota < 0 || nota > 20) {
        alert("⚠️ La nota debe estar entre 0 y 20");
        return;
    }

    const payload = { nota };
    
    if(!evaluacionIdEditar) {
        const matriculaId = selectMatricula.value;
        if(!matriculaId) {
            alert("⚠️ Seleccione una matrícula");
            return;
        }
        payload.id_matricula = matriculaId;
    }

    const url = evaluacionIdEditar ? `${API}/${evaluacionIdEditar}` : API;
    const method = evaluacionIdEditar ? "PUT" : "POST";

    try {
        const res = await fetch(url, {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if(!res.ok) {
            alert("❌ " + (data.error || "Error al guardar"));
            return;
        }

        const estado = nota >= 10.5 ? "APROBADO ✅" : "DESAPROBADO ❌";
        alert(`✅ ${data.mensaje}\nNota: ${nota.toFixed(2)}\nEstado: ${estado}`);
        
        modal.hide();
        cargarEvaluaciones();

    } catch (err) {
        console.error("Error al guardar:", err);
        alert("❌ Error de conexión al guardar");
    }
});

// ==========================================
//  ELIMINAR EVALUACIÓN
// ==========================================
window.eliminarEvaluacion = async (id) => {
    if(!confirm("⚠️ ¿Está seguro de eliminar esta evaluación?\nLa matrícula volverá a estado MATRICULADO.")) return;
    
    try {
        const res = await fetch(`${API}/${id}`, { method: "DELETE" });
        const data = await res.json();
        
        if(res.ok) {
            alert("✅ " + data.mensaje);
            cargarEvaluaciones();
        } else {
            alert("❌ " + (data.error || "Error al eliminar"));
        }
    } catch(err) { 
        console.error("Error al eliminar:", err);
        alert("❌ Error de conexión al eliminar"); 
    }
};

// ==========================================
//  CARGAR AL INICIO
// ==========================================
cargarEvaluaciones();