const API_BASE = "http://127.0.0.1:5000/api/reportes";

const alertContainer = document.getElementById("alertContainer");

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

// REPORTE 1: ALUMNOS POR CICLO
async function cargarAlumnosPorCiclo() {
  const contenedor = document.getElementById("reporteAlumnosCiclo");
  contenedor.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary"></div></div>';

  try {
    const res = await fetch(`${API_BASE}/alumnos_ciclo`);
    if (!res.ok) throw new Error("Error al cargar reporte");

    const data = await res.json();

    if (!data.length) {
      contenedor.innerHTML = '<p class="text-muted text-center py-4">No hay datos</p>';
      return;
    }

    contenedor.innerHTML = `
      <div class="table-responsive">
        <table class="table table-hover">
          <thead class="table-light">
            <tr><th>Ciclo</th><th class="text-center">Total Alumnos</th><th class="text-center">Total Matrículas</th></tr>
          </thead>
          <tbody>
            ${data.map(item => `
              <tr>
                <td class="fw-bold">Ciclo ${item.ciclo}</td>
                <td class="text-center">${item.total_alumnos}</td>
                <td class="text-center">${item.total_matriculas}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  } catch (err) {
    console.error("Error:", err);
    contenedor.innerHTML = '<p class="text-danger text-center py-4">Error al cargar reporte</p>';
  }
}

// REPORTE 2: CURSOS DEMANDADOS
async function cargarCursosDemandados() {
  const contenedor = document.getElementById("reporteCursosDemandados");
  contenedor.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary"></div></div>';

  try {
    const res = await fetch(`${API_BASE}/cursos_demandados`);
    if (!res.ok) throw new Error("Error");

    const data = await res.json();

    if (!data.length) {
      contenedor.innerHTML = '<p class="text-muted text-center py-4">No hay datos</p>';
      return;
    }

    contenedor.innerHTML = `
      <div class="table-responsive">
        <table class="table table-hover">
          <thead class="table-light">
            <tr><th>Código</th><th>Curso</th><th class="text-center">Ciclo</th><th class="text-center">Créditos</th><th class="text-center">Total Matrículas</th><th class="text-center">Alumnos Únicos</th></tr>
          </thead>
          <tbody>
            ${data.map(item => `
              <tr>
                <td class="fw-bold">${item.codigo}</td>
                <td>${item.curso}</td>
                <td class="text-center">${item.ciclo}</td>
                <td class="text-center">${item.creditos}</td>
                <td class="text-center"><span class="badge bg-primary">${item.total_matriculas}</span></td>
                <td class="text-center">${item.alumnos_unicos}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  } catch (err) {
    console.error("Error:", err);
    contenedor.innerHTML = '<p class="text-danger text-center py-4">Error</p>';
  }
}

// REPORTE 3: RENDIMIENTO
async function cargarRendimiento() {
  const contenedor = document.getElementById("reporteRendimiento");
  contenedor.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary"></div></div>';

  try {
    const res = await fetch(`${API_BASE}/rendimiento`);
    if (!res.ok) throw new Error("Error");

    const data = await res.json();
    const stats = data.estadisticas_generales;
    const cursos = data.rendimiento_por_curso;

    let html = `
      <div class="row mb-4">
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <h6 class="text-muted">Total Evaluaciones</h6>
              <h3 class="fw-bold text-primary">${stats.total_evaluaciones}</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <h6 class="text-muted">Promedio General</h6>
              <h3 class="fw-bold text-info">${parseFloat(stats.promedio_general || 0).toFixed(2)}</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <h6 class="text-muted">Aprobados</h6>
              <h3 class="fw-bold text-success">${stats.total_aprobados}</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <h6 class="text-muted">% Aprobación</h6>
              <h3 class="fw-bold text-success">${parseFloat(stats.porcentaje_aprobacion || 0).toFixed(1)}%</h3>
            </div>
          </div>
        </div>
      </div>

      <h5 class="fw-bold mb-3">Rendimiento por Curso</h5>
      <div class="table-responsive">
        <table class="table table-hover">
          <thead class="table-light">
            <tr><th>Código</th><th>Curso</th><th class="text-center">Evaluaciones</th><th class="text-center">Promedio</th><th class="text-center">Aprobados</th><th class="text-center">Desaprobados</th><th class="text-center">% Aprobación</th></tr>
          </thead>
          <tbody>
    `;

    if (cursos.length === 0) {
      html += '<tr><td colspan="7" class="text-center text-muted py-4">No hay evaluaciones</td></tr>';
    } else {
      cursos.forEach(c => {
        html += `
          <tr>
            <td class="fw-bold">${c.codigo}</td>
            <td>${c.curso}</td>
            <td class="text-center">${c.evaluaciones}</td>
            <td class="text-center">${parseFloat(c.promedio_nota).toFixed(2)}</td>
            <td class="text-center"><span class="badge bg-success">${c.aprobados}</span></td>
            <td class="text-center"><span class="badge bg-danger">${c.desaprobados}</span></td>
            <td class="text-center fw-bold">${parseFloat(c.porcentaje_aprobacion).toFixed(1)}%</td>
          </tr>
        `;
      });
    }

    html += '</tbody></table></div>';
    contenedor.innerHTML = html;

  } catch (err) {
    console.error("Error:", err);
    contenedor.innerHTML = '<p class="text-danger text-center py-4">Error</p>';
  }
}

// REPORTE 4: NOTAS 3 ÚLTIMOS CICLOS
async function cargarNotas3Ciclos() {
  const contenedor = document.getElementById("reporteNotas3Ciclos");
  contenedor.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary"></div></div>';

  try {
    const res = await fetch(`${API_BASE}/notas_3_ultimos_ciclos`);
    if (!res.ok) throw new Error("Error");

    const data = await res.json();

    if (!data.length) {
      contenedor.innerHTML = '<p class="text-muted text-center py-4">No hay datos</p>';
      return;
    }

    contenedor.innerHTML = `
      <div class="table-responsive">
        <table class="table table-hover table-sm">
          <thead class="table-light">
            <tr><th>Ciclo</th><th>Alumno</th><th>Código</th><th>Curso</th><th class="text-center">Nota</th><th class="text-center">Estado</th></tr>
          </thead>
          <tbody>
            ${data.map(n => `
              <tr>
                <td class="fw-bold">Ciclo ${n.ciclo}</td>
                <td>${n.alumno}</td>
                <td>${n.codigo}</td>
                <td>${n.curso}</td>
                <td class="text-center">${n.nota !== null ? parseFloat(n.nota).toFixed(2) : '-'}</td>
                <td class="text-center">
                  ${n.aprobado === 1 
                    ? '<span class="badge bg-success">APROBADO</span>' 
                    : n.aprobado === 0 
                      ? '<span class="badge bg-danger">DESAPROBADO</span>'
                      : '<span class="badge bg-secondary">SIN EVALUAR</span>'}
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  } catch (err) {
    console.error("Error:", err);
    contenedor.innerHTML = '<p class="text-danger text-center py-4">Error</p>';
  }
}

// REPORTE 5: NOTAS ÚLTIMO CICLO
async function cargarNotasUltimoCiclo() {
  const contenedor = document.getElementById("reporteNotasUltimoCiclo");
  contenedor.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary"></div></div>';

  try {
    const res = await fetch(`${API_BASE}/notas_ultimo_ciclo`);
    if (!res.ok) throw new Error("Error");

    const data = await res.json();

    if (!data.notas || !data.notas.length) {
      contenedor.innerHTML = '<p class="text-muted text-center py-4">No hay datos</p>';
      return;
    }

    contenedor.innerHTML = `
      <div class="alert alert-info">
        <strong>Ciclo: ${data.ciclo}</strong> - Total de registros: ${data.notas.length}
      </div>
      <div class="table-responsive">
        <table class="table table-hover table-sm">
          <thead class="table-light">
            <tr><th>Alumno</th><th>DNI</th><th>Código</th><th>Curso</th><th class="text-center">Créditos</th><th class="text-center">Nota</th><th class="text-center">Estado</th></tr>
          </thead>
          <tbody>
            ${data.notas.map(n => `
              <tr>
                <td>${n.alumno}</td>
                <td>${n.dni}</td>
                <td>${n.codigo}</td>
                <td>${n.curso}</td>
                <td class="text-center">${n.creditos}</td>
                <td class="text-center fw-bold">${n.nota !== null ? parseFloat(n.nota).toFixed(2) : '-'}</td>
                <td class="text-center">
                  ${n.aprobado === 1 
                    ? '<span class="badge bg-success">APROBADO</span>' 
                    : n.aprobado === 0 
                      ? '<span class="badge bg-danger">DESAPROBADO</span>'
                      : '<span class="badge bg-secondary">SIN EVALUAR</span>'}
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  } catch (err) {
    console.error("Error:", err);
    contenedor.innerHTML = '<p class="text-danger text-center py-4">Error</p>';
  }
}

// REPORTE 6: NOTAS TODOS LOS CICLOS
async function cargarNotasTodosCiclos() {
  const contenedor = document.getElementById("reporteNotasTodosCiclos");
  contenedor.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary"></div></div>';

  try {
    const res = await fetch(`${API_BASE}/notas_por_ciclo`);
    if (!res.ok) throw new Error("Error");

    const data = await res.json();

    if (!data.por_ciclo || Object.keys(data.por_ciclo).length === 0) {
      contenedor.innerHTML = '<p class="text-muted text-center py-4">No hay datos</p>';
      return;
    }

    let html = `
      <div class="alert alert-info">
        <strong>Total de ciclos:</strong> ${data.total_ciclos} | <strong>Total de registros:</strong> ${data.total_registros}
      </div>
    `;

    for (const [ciclo, notas] of Object.entries(data.por_ciclo)) {
      html += `
        <h6 class="fw-bold mt-4 mb-2">📚 Ciclo ${ciclo} (${notas.length} registros)</h6>
        <div class="table-responsive">
          <table class="table table-hover table-sm">
            <thead class="table-light">
              <tr><th>Alumno</th><th>Código</th><th>Curso</th><th class="text-center">Créditos</th><th class="text-center">Nota</th><th class="text-center">Estado</th></tr>
            </thead>
            <tbody>
              ${notas.map(n => `
                <tr>
                  <td>${n.alumno}</td>
                  <td>${n.codigo}</td>
                  <td>${n.curso}</td>
                  <td class="text-center">${n.creditos}</td>
                  <td class="text-center fw-bold">${n.nota !== null ? parseFloat(n.nota).toFixed(2) : '-'}</td>
                  <td class="text-center"><span class="badge bg-${n.estado === 'APROBADO' ? 'success' : n.estado === 'DESAPROBADO' ? 'danger' : 'secondary'}">${n.estado}</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
    }

    contenedor.innerHTML = html;

  } catch (err) {
    console.error("Error:", err);
    contenedor.innerHTML = '<p class="text-danger text-center py-4">Error</p>';
  }
}

// EVENTOS
document.addEventListener('DOMContentLoaded', function() {
  const tabs = document.querySelectorAll('[data-bs-toggle="tab"]');
  
  tabs.forEach(tab => {
    tab.addEventListener('shown.bs.tab', function(e) {
      const target = e.target.getAttribute('data-bs-target');
      
      if (target === '#tab1') cargarAlumnosPorCiclo();
      else if (target === '#tab2') cargarCursosDemandados();
      else if (target === '#tab3') cargarRendimiento();
      else if (target === '#tab4') cargarNotas3Ciclos();
      else if (target === '#tab5') cargarNotasUltimoCiclo();
      else if (target === '#tab6') cargarNotasTodosCiclos();
    });
  });

  cargarAlumnosPorCiclo();
});