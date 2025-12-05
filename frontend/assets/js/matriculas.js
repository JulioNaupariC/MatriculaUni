const API = "http://127.0.0.1:5000/api/matriculas";
const API_ALUMNOS = "http://127.0.0.1:5000/api/alumnos";

const tbody = document.getElementById("tbodyMatriculas");
const modalEl = document.getElementById("modalMatricula");
const modal = new bootstrap.Modal(modalEl);
const form = document.getElementById("formMatricula");

// Elementos del formulario
const selectAlumno = document.getElementById("selectAlumno");
const contadorCursos = document.getElementById("contadorCursos");
const cursosSeleccionados = document.getElementById("cursosSeleccionados");
const progressBar = document.getElementById("progressBar");
const seccionJalados = document.getElementById("seccionJalados");
const listaJalados = document.getElementById("listaJalados");
const seccionDisponibles = document.getElementById("seccionDisponibles");
const listaDisponibles = document.getElementById("listaDisponibles");
const cicloActual = document.getElementById("cicloActual");
const maxDisponibles = document.getElementById("maxDisponibles");
const mensajeSinCursos = document.getElementById("mensajeSinCursos");
const btnGuardar = document.getElementById("btnGuardarMatricula");
const btnTexto = document.getElementById("btnTexto");
const btnSpinner = document.getElementById("btnSpinner");

let cursosJaladosIds = [];
let cursosDisponiblesData = [];

// ==========================================
//  LISTAR MATRÍCULAS AGRUPADAS: CICLO → ALUMNO → CURSOS
// ==========================================
async function cargarMatriculas() {
  tbody.innerHTML = '<tr><td colspan="8" class="text-center">Cargando...</td></tr>';
  try {
    const res = await fetch(API);
    const data = await res.json();
    
    if(!data.length) {
      tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No hay matrículas registradas</td></tr>';
      return;
    }

    // Agrupar por ciclo_matricula → alumno
    const porCiclo = {};
    data.forEach(m => {
      const ciclo = m.ciclo_matricula;
      const alumno = m.alumno;
      
      if(!porCiclo[ciclo]) porCiclo[ciclo] = {};
      if(!porCiclo[ciclo][alumno]) porCiclo[ciclo][alumno] = [];
      
      porCiclo[ciclo][alumno].push(m);
    });

    // Ordenar ciclos de mayor a menor
    const ciclosOrdenados = Object.keys(porCiclo).sort((a, b) => b - a);

    let html = '';
    ciclosOrdenados.forEach(ciclo => {
      const alumnos = porCiclo[ciclo];
      const totalMatriculas = Object.values(alumnos).reduce((sum, cursos) => sum + cursos.length, 0);
      
      // Encabezado del ciclo
      html += `
        <tr class="table-primary">
          <td colspan="8" class="fw-bold fs-5 py-3">
            📘 CICLO ${ciclo} 
            <span class="badge bg-primary ms-2">${totalMatriculas} matrículas</span>
          </td>
        </tr>
      `;

      // Por cada alumno en el ciclo
      Object.keys(alumnos).sort().forEach(alumno => {
        const cursos = alumnos[alumno];
        
        // Encabezado del alumno
        html += `
          <tr class="table-light">
            <td colspan="8" class="fw-bold py-2 ps-4">
              👤 ${alumno} 
              <span class="badge bg-secondary ms-2">${cursos.length} cursos</span>
            </td>
          </tr>
        `;

        // Cursos del alumno
        cursos.forEach(m => {
          const esArrastre = m.ciclo_original !== m.ciclo_matricula;
          const badgeArrastre = esArrastre ? `<span class="badge bg-warning text-dark">Arrastre Ciclo ${m.ciclo_original}</span>` : '';
          
          html += `
            <tr class="align-middle">
              <td class="ps-5">${m.id}</td>
              <td class="text-start ps-5">${m.alumno}</td>
              <td class="text-start">${m.codigo} - ${m.curso} ${badgeArrastre}</td>
              <td><span class="badge bg-info">${m.ciclo_original}</span></td>
              <td><span class="badge bg-primary">${m.ciclo_matricula}</span></td>
              <td><span class="badge ${m.intento > 1 ? 'bg-warning text-dark' : 'bg-secondary'}">${m.intento}°</span></td>
              <td><span class="badge bg-${getColor(m.estado)}">${m.estado}</span></td>
              <td>
                <button class="btn btn-sm btn-danger" onclick="eliminarMatricula(${m.id})" title="Eliminar">
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
    tbody.innerHTML = '<tr><td colspan="8" class="text-center text-danger">❌ Error al cargar</td></tr>';
  }
}

function getColor(estado) {
    if(estado === 'APROBADO') return 'success';
    if(estado === 'DESAPROBADO') return 'danger';
    return 'primary'; 
}

// ==========================================
//  CARGAR ALUMNOS
// ==========================================
async function cargarAlumnosCombo() {
    try {
        const res = await fetch(API_ALUMNOS);
        const data = await res.json();
        selectAlumno.innerHTML = '<option value="">-- Seleccione un alumno --</option>' + 
            data.map(a => `
                <option value="${a.id}">
                    ${a.apellido} ${a.nombre} - Ciclo ${a.ciclo_actual}
                </option>
            `).join("");
    } catch(err) {
        console.error(err);
        selectAlumno.innerHTML = '<option value="">❌ Error al cargar</option>';
    }
}

// ==========================================
//  CARGAR CURSOS DISPONIBLES
// ==========================================
async function cargarCursosDisponibles(alumnoId) {
    // Resetear todo
    contadorCursos.classList.add("d-none");
    seccionJalados.classList.add("d-none");
    seccionDisponibles.classList.add("d-none");
    mensajeSinCursos.classList.add("d-none");
    listaJalados.innerHTML = "";
    listaDisponibles.innerHTML = "";
    btnGuardar.disabled = true;
    cursosJaladosIds = [];
    cursosDisponiblesData = [];

    if(!alumnoId) return;

    try {
        const res = await fetch(`${API}/cursos-disponibles/${alumnoId}`);
        const data = await res.json();

        if(!res.ok) {
            alert(data.error || "Error al obtener cursos");
            return;
        }

        // Mostrar contador
        contadorCursos.classList.remove("d-none");
        cicloActual.textContent = data.ciclo_actual;
        maxDisponibles.textContent = data.cursos_disponibles_max;

        // CURSOS JALADOS (Obligatorios)
        if(data.cursos_jalados.length > 0) {
            seccionJalados.classList.remove("d-none");
            cursosJaladosIds = data.cursos_jalados.map(c => c.id);
            
            listaJalados.innerHTML = data.cursos_jalados.map(c => `
                <div class="form-check p-3 rounded border curso-obligatorio">
                    <input class="form-check-input checkbox-obligatorio" type="checkbox" 
                           value="${c.id}" id="jalado_${c.id}" checked disabled>
                    <label class="form-check-label w-100" for="jalado_${c.id}">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong>${c.codigo}</strong> - ${c.nombre}
                                <span class="badge bg-danger ms-2">Obligatorio</span>
                                <span class="badge bg-secondary">${c.creditos} créd.</span>
                            </div>
                            <div class="text-end small text-muted">
                                Ciclo ${c.ciclo_original} | Intento ${c.ultimo_intento + 1}° | Última nota: ${c.ultima_nota}
                            </div>
                        </div>
                    </label>
                </div>
            `).join("");
        }

        // CURSOS DISPONIBLES (Opcionales)
        if(data.cursos_disponibles.length > 0) {
            seccionDisponibles.classList.remove("d-none");
            cursosDisponiblesData = data.cursos_disponibles;
            
            listaDisponibles.innerHTML = data.cursos_disponibles.map(c => `
                <div class="form-check p-3 rounded border curso-opcional">
                    <input class="form-check-input curso-checkbox" type="checkbox" 
                           value="${c.id}" id="disp_${c.id}" onchange="actualizarContador()">
                    <label class="form-check-label w-100" for="disp_${c.id}">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong>${c.codigo}</strong> - ${c.nombre}
                                <span class="badge bg-success ms-2">Disponible</span>
                                <span class="badge bg-secondary">${c.creditos} créd.</span>
                            </div>
                            <div class="text-end small text-muted">
                                Ciclo ${c.ciclo_original}
                            </div>
                        </div>
                    </label>
                </div>
            `).join("");
        }

        // Actualizar contador inicial
        actualizarContador();

        // Si no hay cursos disponibles
        if(data.cursos_jalados.length === 0 && data.cursos_disponibles.length === 0) {
            mensajeSinCursos.classList.remove("d-none");
        }

    } catch(err) {
        console.error(err);
        alert("Error al cargar cursos disponibles");
    }
}

// ==========================================
//  ACTUALIZAR CONTADOR
// ==========================================
function actualizarContador() {
    const checkboxes = document.querySelectorAll('.curso-checkbox:checked');
    const totalSeleccionados = cursosJaladosIds.length + checkboxes.length;
    
    cursosSeleccionados.textContent = totalSeleccionados;
    
    // Actualizar barra de progreso
    const porcentaje = (totalSeleccionados / 6) * 100;
    progressBar.style.width = porcentaje + '%';
    
    if(totalSeleccionados >= 6) {
        progressBar.classList.remove('bg-primary');
        progressBar.classList.add('bg-success');
    } else {
        progressBar.classList.remove('bg-success');
        progressBar.classList.add('bg-primary');
    }
    
    // Deshabilitar checkboxes si ya tiene 6
    const todosCheckboxes = document.querySelectorAll('.curso-checkbox');
    todosCheckboxes.forEach(cb => {
        if(!cb.checked && totalSeleccionados >= 6) {
            cb.disabled = true;
        } else {
            cb.disabled = false;
        }
    });
    
    // Habilitar botón guardar si tiene al menos 1 curso
    btnGuardar.disabled = totalSeleccionados === 0;
}

// ==========================================
//  ABRIR MODAL
// ==========================================
document.getElementById("btnNuevaMatricula").addEventListener("click", async () => {
    form.reset();
    await cargarAlumnosCombo();
    modal.show();
});

// ==========================================
//  EVENTO: CAMBIO DE ALUMNO
// ==========================================
selectAlumno.addEventListener("change", (e) => {
    cargarCursosDisponibles(e.target.value);
});

// ==========================================
//  GUARDAR MATRÍCULA
// ==========================================
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const alumnoId = selectAlumno.value;
    if(!alumnoId) {
        alert("⚠️ Seleccione un alumno");
        return;
    }

    // Obtener cursos seleccionados
    const checkboxes = document.querySelectorAll('.curso-checkbox:checked');
    const cursosOpcionales = Array.from(checkboxes).map(cb => parseInt(cb.value));
    const todosCursos = [...cursosJaladosIds, ...cursosOpcionales];

    if(todosCursos.length === 0) {
        alert("⚠️ Debe seleccionar al menos un curso");
        return;
    }

    if(todosCursos.length > 6) {
        alert("⚠️ No puede matricularse en más de 6 cursos");
        return;
    }

    // Confirmación
    const nombreAlumno = selectAlumno.options[selectAlumno.selectedIndex].text;
    if(!confirm(`¿Confirma matricular a ${nombreAlumno} en ${todosCursos.length} cursos?`)) {
        return;
    }

    // Deshabilitar botón
    btnGuardar.disabled = true;
    btnTexto.classList.add("d-none");
    btnSpinner.classList.remove("d-none");

    try {
        const res = await fetch(`${API}/flexible`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                id_alumno: alumnoId,
                cursos: todosCursos
            })
        });

        const data = await res.json();

        if(!res.ok) {
            alert("❌ " + (data.error || "Error al matricular"));
            return;
        }

        // Mensaje detallado
        let mensaje = `${data.mensaje}\n\n`;

        // Verificar que exista el array de cursos matriculados
        if (data.cursos_matriculados && data.cursos_matriculados.length > 0) {
            mensaje += `Detalle de cursos:\n`;
            data.cursos_matriculados.forEach((c, idx) => {
                const arrastre = c.es_arrastre ? ` (Arrastre del Ciclo ${c.ciclo_original})` : '';
                mensaje += `${idx + 1}. ${c.codigo} - ${c.nombre}${arrastre} - Intento ${c.intento}°\n`;
            });
        }

        // Mostrar cursos rechazados si los hay
        if (data.cursos_rechazados && data.cursos_rechazados.length > 0) {
            mensaje += `\n⚠️ Cursos rechazados:\n`;
            data.cursos_rechazados.forEach((c, idx) => {
                mensaje += `${idx + 1}. ${c.codigo || 'Curso'} - ${c.nombre || ''}: ${c.motivo}\n`;
            });
        }
        
        alert(mensaje);
        
        modal.hide();
        cargarMatriculas();

    } catch (err) {
        console.error(err);
        alert("❌ Error de conexión");
    } finally {
        btnGuardar.disabled = false;
        btnTexto.classList.remove("d-none");
        btnSpinner.classList.add("d-none");
    }
});

// ==========================================
//  ELIMINAR MATRÍCULA
// ==========================================
window.eliminarMatricula = async (id) => {
    if(!confirm("⚠️ ¿Está seguro de eliminar esta matrícula?")) return;
    
    try {
        const res = await fetch(`${API}/${id}`, { method: "DELETE" });
        
        if(res.ok) {
            alert("✅ Matrícula eliminada");
            cargarMatriculas();
        } else {
            alert("❌ Error al eliminar");
        }
    } catch(e) { 
        alert("❌ Error de conexión"); 
    }
};

// ==========================================
//  CARGAR AL INICIO
// ==========================================
cargarMatriculas();
