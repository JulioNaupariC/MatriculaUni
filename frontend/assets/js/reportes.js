const API_REPORTES = "http://127.0.0.1:5000/api/reportes";
const API_ALUMNOS = "http://127.0.0.1:5000/api/alumnos";

const alertContainer = document.getElementById("alertContainer");

function mostrarAlerta(msg, tipo = "success") {
  alertContainer.innerHTML = `
    <div class="alert alert-${tipo} alert-dismissible fade show" role="alert">
      ${msg} <button class="btn-close" data-bs-dismiss="alert"></button>
    </div>`;
  setTimeout(() => { alertContainer.innerHTML = ""; }, 5000);
}

// ==========================================
//  CARGAR COMBO ALUMNOS
// ==========================================
async function cargarComboAlumnos() {
  const selects = [
    document.getElementById("selectAlumnoUltimosCiclos"),
    document.getElementById("selectAlumnoUltimoCiclo"),
    document.getElementById("selectAlumnoGeneral")
  ];
  
  try {
    const res = await fetch(API_ALUMNOS);
    const alumnos = await res.json();
    
    if (!alumnos.length) {
      selects.forEach(select => {
        if (select) select.innerHTML = '<option value="">No hay alumnos registrados</option>';
      });
      return;
    }

    const options = '<option value="">-- Seleccione un Alumno --</option>' +
      alumnos.map(a => `<option value="${a.id}">${a.apellido}, ${a.nombre} (DNI: ${a.dni})</option>`).join("");
    
    selects.forEach(select => {
      if (select) select.innerHTML = options;
    });
      
  } catch (err) {
    console.error("Error cargando alumnos:", err);
    selects.forEach(select => {
      if (select) select.innerHTML = '<option value="">Error al cargar datos</option>';
    });
  }
}

// ==========================================
// FUNCIÓN AUXILIAR: RENDERIZAR TABLA DE CURSOS
// ==========================================
function renderizarTablaCursos(cursos, mostrarCiclo = false) {
  let html = `
    <div class="table-responsive">
      <table class="table table-hover mb-0 align-middle">
        <thead class="table-light">
          <tr>
            ${mostrarCiclo ? '<th>Ciclo</th>' : ''}
            <th>Código</th>
            <th>Curso</th>
            <th class="text-center">Créditos</th>
            <th class="text-center">Nota</th>
            <th class="text-center">Estado</th>
            <th class="text-end">Fecha Eval.</th>
          </tr>
        </thead>
        <tbody>
  `;

  cursos.forEach(c => {
    let badgeClass = "secondary";
    let estadoTexto = c.estado_curso;
    let notaTexto = c.nota !== null ? parseFloat(c.nota).toFixed(2) : "-";

    if (estadoTexto === "APROBADO") badgeClass = "success";
    else if (estadoTexto === "DESAPROBADO") badgeClass = "danger";
    else if (estadoTexto === "SIN NOTA") badgeClass = "warning text-dark";

    html += `
      <tr>
        ${mostrarCiclo ? `<td class="fw-bold text-primary">Ciclo ${c.ciclo}</td>` : ''}
        <td class="fw-bold text-muted">${c.codigo}</td>
        <td>${c.curso}</td>
        <td class="text-center">${c.creditos}</td>
        <td class="text-center fw-bold ${estadoTexto === 'APROBADO' ? 'text-success' : 'text-danger'}">
          ${notaTexto}
        </td>
        <td class="text-center">
          <span class="badge bg-${badgeClass}">${estadoTexto}</span>
        </td>
        <td class="text-end small text-muted">
          ${c.fecha_evaluacion ? new Date(c.fecha_evaluacion).toLocaleDateString() : 'Pendiente'}
        </td>
      </tr>`;
  });

  html += `</tbody></table></div>`;
  return html;
}

// ==========================================
// INTERFAZ 1: NOTAS DE LOS 3 ÚLTIMOS CICLOS
// ==========================================
async function verUltimos3Ciclos() {
  const alumnoId = document.getElementById("selectAlumnoUltimosCiclos").value;
  const contenedor = document.getElementById("resultadoUltimos3Ciclos");

  if (!alumnoId) {
    mostrarAlerta("Por favor, seleccione un alumno.", "warning");
    return;
  }

  contenedor.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary"></div><p class="mt-2">Cargando últimos 3 ciclos...</p></div>';

  try {
    const url = `${API_REPORTES}/rendimiento_alumno/${alumnoId}?filtro=ULTIMOS_3`;
    const res = await fetch(url);
    const data = await res.json();

    if (!res.ok) throw new Error(data.error || "Error al consultar");

    const historial = data.historial_academico;
    
    if (Object.keys(historial).length === 0) {
      contenedor.innerHTML = `
        <div class="alert alert-info text-center">
          <i class="bi bi-info-circle me-2"></i>
          El alumno no tiene matrículas registradas en los últimos 3 ciclos.
        </div>`;
      return;
    }

    let html = '<div class="row">';
    const ciclosOrdenados = Object.keys(historial).sort((a, b) => b - a);

    ciclosOrdenados.forEach(ciclo => {
      const cursos = historial[ciclo];
      const aprobados = cursos.filter(c => c.estado_curso === 'APROBADO').length;
      const desaprobados = cursos.filter(c => c.estado_curso === 'DESAPROBADO').length;
      const pendientes = cursos.filter(c => c.estado_curso === 'SIN NOTA').length;
      
      html += `
        <div class="col-12 mb-4">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-primary text-white">
              <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0 fw-bold">📅 Ciclo ${ciclo}</h5>
                <div>
                  <span class="badge bg-success me-1">✓ ${aprobados}</span>
                  <span class="badge bg-danger me-1">✗ ${desaprobados}</span>
                  <span class="badge bg-warning text-dark">⏳ ${pendientes}</span>
                </div>
              </div>
            </div>
            <div class="card-body p-0">
              ${renderizarTablaCursos(cursos, false)}
            </div>
          </div>
        </div>
      `;
    });

    html += '</div>';
    contenedor.innerHTML = html;

  } catch (err) {
    console.error("Error:", err);
    contenedor.innerHTML = `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle me-2"></i>Error al cargar datos: ${err.message}</div>`;
  }
}

// ==========================================
// INTERFAZ 2: NOTAS DEL ÚLTIMO CICLO
// ==========================================
async function verUltimoCiclo() {
  const alumnoId = document.getElementById("selectAlumnoUltimoCiclo").value;
  const contenedor = document.getElementById("resultadoUltimoCiclo");

  if (!alumnoId) {
    mostrarAlerta("Por favor, seleccione un alumno.", "warning");
    return;
  }

  contenedor.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary"></div><p class="mt-2">Cargando último ciclo...</p></div>';

  try {
    const url = `${API_REPORTES}/rendimiento_alumno/${alumnoId}?filtro=ULTIMO`;
    const res = await fetch(url);
    const data = await res.json();

    if (!res.ok) throw new Error(data.error || "Error al consultar");

    const historial = data.historial_academico;
    
    if (Object.keys(historial).length === 0) {
      contenedor.innerHTML = `
        <div class="alert alert-info text-center">
          <i class="bi bi-info-circle me-2"></i>
          El alumno no tiene matrículas registradas en el último ciclo.
        </div>`;
      return;
    }

    const ciclo = Object.keys(historial)[0];
    const cursos = historial[ciclo];
    
    const aprobados = cursos.filter(c => c.estado_curso === 'APROBADO').length;
    const desaprobados = cursos.filter(c => c.estado_curso === 'DESAPROBADO').length;
    const pendientes = cursos.filter(c => c.estado_curso === 'SIN NOTA').length;
    
    const notasAprobadas = cursos
      .filter(c => c.estado_curso === 'APROBADO' && c.nota !== null)
      .map(c => parseFloat(c.nota));
    
    const promedio = notasAprobadas.length > 0 
      ? (notasAprobadas.reduce((a, b) => a + b, 0) / notasAprobadas.length).toFixed(2)
      : '-';

    let html = `
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-primary text-white">
          <h5 class="mb-0 fw-bold">📅 Ciclo Actual: ${ciclo}</h5>
        </div>
        <div class="card-body">
          <div class="row text-center mb-4">
            <div class="col-md-3">
              <div class="p-3 bg-light rounded">
                <h3 class="text-primary mb-0">${cursos.length}</h3>
                <small class="text-muted">Total Cursos</small>
              </div>
            </div>
            <div class="col-md-3">
              <div class="p-3 bg-success bg-opacity-10 rounded">
                <h3 class="text-success mb-0">${aprobados}</h3>
                <small class="text-muted">Aprobados</small>
              </div>
            </div>
            <div class="col-md-3">
              <div class="p-3 bg-danger bg-opacity-10 rounded">
                <h3 class="text-danger mb-0">${desaprobados}</h3>
                <small class="text-muted">Desaprobados</small>
              </div>
            </div>
            <div class="col-md-3">
              <div class="p-3 bg-warning bg-opacity-10 rounded">
                <h3 class="text-warning mb-0">${promedio}</h3>
                <small class="text-muted">Promedio</small>
              </div>
            </div>
          </div>
          ${renderizarTablaCursos(cursos, false)}
        </div>
      </div>
    `;

    contenedor.innerHTML = html;

  } catch (err) {
    console.error("Error:", err);
    contenedor.innerHTML = `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle me-2"></i>Error al cargar datos: ${err.message}</div>`;
  }
}

// ==========================================
// INTERFAZ 3: REPORTE GENERAL (TODOS LOS CURSOS POR CICLO)
// ==========================================
async function verReporteGeneral() {
  const alumnoId = document.getElementById("selectAlumnoGeneral").value;
  const contenedor = document.getElementById("resultadoGeneral");

  if (!alumnoId) {
    mostrarAlerta("Por favor, seleccione un alumno.", "warning");
    return;
  }

  contenedor.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary"></div><p class="mt-2">Generando reporte completo...</p></div>';

  try {
    const url = `${API_REPORTES}/rendimiento_alumno/${alumnoId}?filtro=TODOS`;
    const res = await fetch(url);
    const data = await res.json();

    if (!res.ok) throw new Error(data.error || "Error al consultar");

    const historial = data.historial_academico;
    
    if (Object.keys(historial).length === 0) {
      contenedor.innerHTML = `
        <div class="alert alert-info text-center">
          <i class="bi bi-info-circle me-2"></i>
          El alumno no tiene matrículas registradas.
        </div>`;
      return;
    }

    // Calcular estadísticas globales
    let totalCursos = 0;
    let totalAprobados = 0;
    let totalDesaprobados = 0;
    let totalPendientes = 0;
    let todasNotas = [];

    Object.values(historial).forEach(cursos => {
      totalCursos += cursos.length;
      totalAprobados += cursos.filter(c => c.estado_curso === 'APROBADO').length;
      totalDesaprobados += cursos.filter(c => c.estado_curso === 'DESAPROBADO').length;
      totalPendientes += cursos.filter(c => c.estado_curso === 'SIN NOTA').length;
      
      cursos.forEach(c => {
        if (c.nota !== null) todasNotas.push(parseFloat(c.nota));
      });
    });

    const promedioGeneral = todasNotas.length > 0 
      ? (todasNotas.reduce((a, b) => a + b, 0) / todasNotas.length).toFixed(2)
      : '-';

    let html = `
      <!-- Estadísticas Globales -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-gradient bg-primary text-white">
          <h5 class="mb-0 fw-bold">📊 Resumen Académico General</h5>
        </div>
        <div class="card-body">
          <div class="row text-center">
            <div class="col-md-2">
              <div class="p-3 bg-light rounded">
                <h3 class="text-primary mb-0">${totalCursos}</h3>
                <small class="text-muted">Total Cursos</small>
              </div>
            </div>
            <div class="col-md-2">
              <div class="p-3 bg-success bg-opacity-10 rounded">
                <h3 class="text-success mb-0">${totalAprobados}</h3>
                <small class="text-muted">Aprobados</small>
              </div>
            </div>
            <div class="col-md-2">
              <div class="p-3 bg-danger bg-opacity-10 rounded">
                <h3 class="text-danger mb-0">${totalDesaprobados}</h3>
                <small class="text-muted">Desaprobados</small>
              </div>
            </div>
            <div class="col-md-2">
              <div class="p-3 bg-warning bg-opacity-10 rounded">
                <h3 class="text-warning mb-0">${totalPendientes}</h3>
                <small class="text-muted">Pendientes</small>
              </div>
            </div>
            <div class="col-md-2">
              <div class="p-3 bg-info bg-opacity-10 rounded">
                <h3 class="text-info mb-0">${promedioGeneral}</h3>
                <small class="text-muted">Promedio</small>
              </div>
            </div>
            <div class="col-md-2">
              <div class="p-3 bg-secondary bg-opacity-10 rounded">
                <h3 class="text-secondary mb-0">${Object.keys(historial).length}</h3>
                <small class="text-muted">Ciclos</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Detalle por Ciclo -->
    `;

    const ciclosOrdenados = Object.keys(historial).sort((a, b) => b - a);

    ciclosOrdenados.forEach(ciclo => {
      const cursos = historial[ciclo];
      
      html += `
        <div class="card border-0 shadow-sm mb-3">
          <div class="card-header bg-light">
            <div class="d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-bold">📅 Ciclo ${ciclo}</h6>
              <span class="badge bg-primary">${cursos.length} cursos</span>
            </div>
          </div>
          <div class="card-body p-0">
            ${renderizarTablaCursos(cursos, false)}
          </div>
        </div>
      `;
    });

    contenedor.innerHTML = html;

  } catch (err) {
    console.error("Error:", err);
    contenedor.innerHTML = `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle me-2"></i>Error al cargar datos: ${err.message}</div>`;
  }
}

// ==========================================
//  INICIALIZACIÓN
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
  cargarComboAlumnos();
});