// Chart.js Manager for Sicredi Task Monitor (Official Sicredi Palette & Dual Theme)
let timeSeriesChart = null;
let healthDoughnutChart = null;
let actionsBarChart = null;
let nodosBarChart = null;

// Cache last data to re-render seamlessly when switching theme
let lastTimeSeriesData = [];
let lastHealthData = { sucesso: 0, repassado: 0, erro: 0 };
let lastActionsData = [];
let lastNodosData = [];

let isDarkMode = false;

// Sicredi official color palettes (Light & Dark)
function getThemeColors() {
  if (isDarkMode) {
    return {
      green: '#48BD14',
      greenDark: '#62CF30',
      red: '#FF4D79',
      yellow: '#FBBF24',
      blue: '#38BDF8',
      text: '#9EADA0',
      grid: 'rgba(255, 255, 255, 0.08)',
      tooltipBg: '#141D14',
      doughnutBorder: '#141D14'
    };
  }
  return {
    green: '#3FA110',
    greenDark: '#146E37',
    red: '#ED5A6C',
    yellow: '#FFCD00',
    blue: '#0284C7',
    text: '#5A645A',
    grid: '#EAEFEA',
    tooltipBg: '#323C32',
    doughnutBorder: '#FFFFFF'
  };
}

function getCommonOptions() {
  const colors = getThemeColors();
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: colors.text,
          font: { family: 'Nunito', size: 12, weight: 'bold' },
          padding: 14
        }
      },
      tooltip: {
        backgroundColor: colors.tooltipBg,
        titleColor: '#FFFFFF',
        titleFont: { family: 'Exo 2', size: 12, weight: 'bold' },
        bodyColor: '#FFFFFF',
        bodyFont: { family: 'Nunito', size: 12 },
        borderColor: colors.green,
        borderWidth: 1,
        padding: 10,
        boxPadding: 4,
        usePointStyle: true
      }
    },
    scales: {
      x: {
        grid: { color: colors.grid },
        ticks: { color: colors.text, font: { family: 'Nunito', size: 11, weight: '600' } }
      },
      y: {
        beginAtZero: true,
        grid: { color: colors.grid },
        ticks: { color: colors.text, font: { family: 'Nunito', size: 11, weight: '600' } }
      }
    }
  };
}

export function setChartTheme(dark) {
  isDarkMode = dark;
  // Re-render all active charts with new theme colors
  if (lastTimeSeriesData.length) updateTimeSeriesChart(lastTimeSeriesData);
  if (lastHealthData.sucesso || lastHealthData.repassado || lastHealthData.erro) {
    updateHealthDoughnut(lastHealthData.sucesso, lastHealthData.repassado, lastHealthData.erro);
  }
  if (lastActionsData.length) updateActionsChart(lastActionsData);
  if (lastNodosData.length) updateNodosChart(lastNodosData);
}

export function updateTimeSeriesChart(data) {
  lastTimeSeriesData = data;
  const ctx = document.getElementById('timeSeriesCanvas');
  if (!ctx) return;

  const colors = getThemeColors();
  const labels = data.map(d => d.period);
  const sucessos = data.map(d => d.sucesso);
  const repassados = data.map(d => d.repassado || 0);
  const erros = data.map(d => d.erro);

  if (timeSeriesChart) {
    timeSeriesChart.destroy();
  }

  timeSeriesChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Sucessos',
          data: sucessos,
          backgroundColor: colors.green,
          borderRadius: 4,
          stack: 'combined'
        },
        {
          label: 'Repassados / Fluid',
          data: repassados,
          backgroundColor: colors.blue,
          borderRadius: 4,
          stack: 'combined'
        },
        {
          label: 'Falhas / Erros',
          data: erros,
          backgroundColor: colors.red,
          borderRadius: 4,
          stack: 'combined'
        }
      ]
    },
    options: {
      ...getCommonOptions(),
      interaction: {
        mode: 'index',
        intersect: false
      }
    }
  });
}

export function updateHealthDoughnut(sucesso, repassado, erro) {
  const rep = repassado || 0;
  lastHealthData = { sucesso, repassado: rep, erro };
  const ctx = document.getElementById('healthDoughnutCanvas');
  if (!ctx) return;

  const colors = getThemeColors();
  if (healthDoughnutChart) {
    healthDoughnutChart.destroy();
  }

  const total = sucesso + rep + erro;
  const taxa = total > 0 ? (((sucesso + rep) / total) * 100).toFixed(1) : 0;

  healthDoughnutChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Sucesso Direto', 'Repassado / Fluid', 'Falhas / Erros'],
      datasets: [
        {
          data: [sucesso, rep, erro],
          backgroundColor: [colors.green, colors.blue, colors.red],
          borderWidth: 2,
          borderColor: colors.doughnutBorder,
          hoverOffset: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '74%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: colors.text,
            font: { family: 'Nunito', size: 12, weight: 'bold' },
            padding: 12
          }
        },
        tooltip: {
          backgroundColor: colors.tooltipBg,
          padding: 10
        }
      }
    }
  });

  const centerLabel = document.getElementById('healthDoughnutPercent');
  if (centerLabel) {
    centerLabel.innerText = `${taxa}%`;
  }
}

export function updateActionsChart(byAcao) {
  lastActionsData = byAcao;
  const ctx = document.getElementById('actionsCanvas');
  if (!ctx) return;

  const colors = getThemeColors();
  if (actionsBarChart) {
    actionsBarChart.destroy();
  }

  const labels = byAcao.map(a => a._id || 'N/A');
  const counts = byAcao.map(a => a.total);

  actionsBarChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Volume de Execuções',
          data: counts,
          backgroundColor: colors.greenDark,
          borderRadius: 4
        }
      ]
    },
    options: {
      ...getCommonOptions(),
      indexAxis: 'y', // barra horizontal
      plugins: {
        legend: { display: false }
      }
    }
  });
}

export function updateNodosChart(byNodo) {
  lastNodosData = byNodo;
  const ctx = document.getElementById('nodosCanvas');
  if (!ctx) return;

  const colors = getThemeColors();
  if (nodosBarChart) {
    nodosBarChart.destroy();
  }

  const labels = byNodo.map(n => `Nodo ${n._id}`);
  const counts = byNodo.map(n => n.total);

  nodosBarChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Execuções por Nodo',
          data: counts,
          backgroundColor: colors.blue,
          borderRadius: 4
        }
      ]
    },
    options: {
      ...getCommonOptions(),
      plugins: {
        legend: { display: false }
      }
    }
  });
}
