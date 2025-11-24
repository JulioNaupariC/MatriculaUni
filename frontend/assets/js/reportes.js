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
  const select = document.getElementById("selectAlumnoReporte");
  try {
    const res = await fetch(API_ALUMNOS);
    const alumnos = await res.json();
    
    if (!alumnos.length) {
      select.innerHTML = '<option value="">No hay alumnos registrados</option>';
      return;
    }

    select.innerHTML = '<option value="">-- Seleccione un Alumno --</option>' +
      alumnos.map(a => `<option value="${a.id}">${a.apellido}, ${a.nombre} (DNI: ${a.dni})</option>`).join("");
      
  } catch (err) {
    console.error("Error cargando alumnos:", err);
    select.innerHTML = '<option value="">Error al cargar datos</option>';
  }
}

// ==========================================
//  REPORTE 1: RENDIMIENTO (Lógica Principal)
// ==========================================
async function buscarRendimiento() {
  const alumnoId = document.getElementById("selectAlumnoReporte").value;
  const filtro = document.querySelector('input[name="filtroCiclo"]:checked').value;
  const contenedor = document.getElementById("resultadoRendimiento");

  if (!alumnoId) {
    mostrarAlerta("Por favor, seleccione un alumno.", "warning");
    return;
  }

  contenedor.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary"></div><p class="mt-2">Analizando historial...</p></div>';

  try {
    const url = `${API_REPORTES}/rendimiento_alumno/${alumnoId}?filtro=${filtro}`;
    const res = await fetch(url);
    const data = await res.json();

    if (!res.ok) throw new Error(data.error || "Error al consultar");

    const historial = data.historial_academico;
    
    if (Object.keys(historial).length === 0) {
      contenedor.innerHTML = `
        <div class="alert alert-info text-center">
          El alumno no tiene matrículas registradas para el filtro seleccionado (${filtro}).
        </div>`;
      return;
    }

    let html = '';
    const ciclosOrdenados = Object.keys(historial).sort((a, b) => b - a);

    ciclosOrdenados.forEach(ciclo => {
      const cursos = historial[ciclo];
      
      html += `
        <div class="card mb-4 border-0 shadow-sm">
          <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0 fw-bold">📅 Ciclo Académico ${ciclo}</h5>
            <span class="badge bg-light text-primary">${cursos.length} Cursos</span>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-hover mb-0 align-middle">
                <thead class="table-light">
                  <tr>
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

      html += `</tbody></table></div></div></div>`;
    });

    contenedor.innerHTML = html;

  } catch (err) {
    console.error("Error:", err);
    contenedor.innerHTML = `<div class="alert alert-danger">Error al cargar datos: ${err.message}</div>`;
  }
}

// ==========================================
//  REPORTE 2: ALUMNOS POR CICLO
// ==========================================
async function cargarAlumnosCiclo() {
  const contenedor = document.getElementById("reporteAlumnosCiclo");
  contenedor.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary"></div></div>';

  try {
    const res = await fetch(`${API_REPORTES}/alumnos_ciclo`);
    const data = await res.json();

    if (!data.length) {
      contenedor.innerHTML = '<p class="text-center py-4">No hay datos disponibles.</p>';
      return;
    }

    contenedor.innerHTML = `
      <div class="table-responsive">
        <table class="table table-hover">
          <thead class="table-light">
            <tr><th>Ciclo</th><th class="text-center">Alumnos Matriculados</th><th class="text-center">Total Cursos Inscritos</th></tr>
          </thead>
          <tbody>
            ${data.map(d => `
              <tr>
                <td class="fw-bold">Ciclo ${d.ciclo}</td>
                <td class="text-center fw-bold text-primary">${d.total_alumnos}</td>
                <td class="text-center">${d.total_matriculas}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  } catch (err) {
    contenedor.innerHTML = '<p class="text-danger text-center">Error al cargar reporte.</p>';
  }
}

// ==========================================
//  INICIALIZACIÓN
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
  cargarComboAlumnos();

  // Escuchar cambios de pestaña
  const tabs = document.querySelectorAll('[data-bs-toggle="tab"]');
  tabs.forEach(tab => {
    tab.addEventListener('shown.bs.tab', function(e) {
      const target = e.target.getAttribute('data-bs-target');
      if (target === '#tabCiclos') cargarAlumnosCiclo();
    });
  });
});