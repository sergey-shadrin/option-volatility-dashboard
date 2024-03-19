const pointRadius = 8;
const pointHoverRadius = pointRadius + 4;
const DEFAULT_SETTINGS_MAP = {
    'Volatility': {
        fill: false,
        cubicInterpolationMode: 'monotone',
        tension: 0.2,
        backgroundColor: 'rgba(255, 0, 0, 0.5)',
        borderColor: 'rgb(255, 0, 0, 0.8)'
    },
    'Ask': {
        hidden: true,
        fill: false,
        showLine: false,
        backgroundColor: 'rgba(255, 0, 0, 0.5)',
        borderColor: 'rgb(255, 0, 0)',
        elements: {
            point: {
                radius: pointRadius,
                hoverRadius: pointHoverRadius,
                rotation: 180,
                pointStyle: 'triangle',
            }
        }
    },
    'Bid': {
        hidden: true,
        fill: false,
        showLine: false,
        backgroundColor: 'rgba(0, 160, 0, 0.5)',
        borderColor: 'rgb(0, 160, 0)',
        elements: {
            point: {
                radius: pointRadius,
                hoverRadius: pointHoverRadius,
                pointStyle: 'triangle',
            }
        }
    },
    'Last Price': {
        hidden: true,
        fill: false,
        showLine: false,
        backgroundColor: 'rgba(192, 171, 30, 0.5)',
        borderColor: 'rgb(192, 171, 30)',
        elements: {
            point: {
                radius: pointRadius / 2,
                hoverRadius: pointHoverRadius,
                pointStyle: 'circle',
            }
        }
    }
}


function requestChartData() {
    // Create a new XMLHttpRequest object
    var xhr = new XMLHttpRequest();

    // Configure the request
    xhr.open('GET', '/chart.json', true);

    // Set up the onload function to handle the response
    xhr.onload = function() {
      // Check if the request was successful
      if (xhr.status >= 200 && xhr.status < 300) {
        // Parse the JSON response
        var jsonResponse = JSON.parse(xhr.responseText);

        updateChart(jsonResponse);
      } else {
        // Handle errors
        console.error('Request failed with status code ' + xhr.status);
      }
    };

    // Set up the onerror function to handle errors
    xhr.onerror = function() {
      console.error('Request failed');
    };

    // Send the request
    xhr.send();
}


const verticalLinePlugin = {
  id: 'draw_vertical_line',

  getLinePosition: function(chart, lineX) {
      scaleX = chart.scales.x;
      let firstTick = scaleX.ticks[0];
      let firstTickLabel = firstTick.label;
      let lastTick = scaleX.ticks[scaleX.ticks.length - 1];
      let lastTickLabel = lastTick.label;
      let pixelToLabelValueRatio = scaleX.width / (lastTickLabel - firstTickLabel);
      let linePosition = scaleX.left + (lineX - firstTickLabel) * pixelToLabelValueRatio;

      const meta = chart.getDatasetMeta(0); // first dataset is used to discover X coordinate of a point
      const data = meta.data;
      return linePosition;
  },

  renderVerticalLine: function(chartInstance, lineX) {
      const lineLeftOffset = this.getLinePosition(chartInstance, lineX);
      const scaleY = chartInstance.scales.y;
      const context = chartInstance.ctx;

      // render vertical line
      context.beginPath();
      context.strokeStyle = '#ffff00';
      context.moveTo(lineLeftOffset, scaleY.top);
      context.lineTo(lineLeftOffset, scaleY.bottom);
      context.stroke();

      // write label
      context.fillStyle = "#ffffff";
      context.textAlign = 'center';
      context.fillText(lineX, lineLeftOffset, scaleY.bottom + scaleY.paddingBottom);
  },

  afterDatasetsDraw: function (chart, args, options, cancelable) {
      if (options.lineX) {
          this.renderVerticalLine(chart, options.lineX);
      }
  }
};

function updateChart(chartData) {
    let view_datasets = chartData['view_datasets'];
    if (g_chart.data.datasets.length == 0) {
        // Init datasets
        let labels = chartData['labels'];
        let datasets = [];
        for (let i = 0; i < labels.length; i++) {
            let label = labels[i];
            let view_dataset = view_datasets[i];
            datasets.push(initDataset(label, view_dataset));
        }
        g_chart.data.datasets = datasets;
    } else {
        for (let i = 0; i < view_datasets.length; i++) {
            g_chart.data.datasets[i].data = view_datasets[i];
        }        
    }


    g_chart.data.labels = chartData['strikes'];
    g_chart.options.plugins['draw_vertical_line'].lineX = chartData['last_price'];
    g_chart.update();
}

function initDataset(label, data) {
    let datasetByLabel = getSettingsByLabel(label);
    datasetByLabel.label = label;
    datasetByLabel.data = data;
    return datasetByLabel;
}

function getSettingsByLabel(label) {
    for (let labelSuffix in DEFAULT_SETTINGS_MAP) {
        if (DEFAULT_SETTINGS_MAP.hasOwnProperty(labelSuffix) && label.endsWith(labelSuffix)) {
            let defaultSettings = DEFAULT_SETTINGS_MAP[labelSuffix];
            return Object.assign({}, defaultSettings);
        }
    }
    return {}
}

function initChart() {
    Chart.defaults.color = '#ffffff';
    Chart.register(verticalLinePlugin);

    const ctx = document.getElementById('volatilityChart');
    return new Chart(ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: []
      },
      options: {
        animation: false,
        interaction: {
          intersect: false,
          mode: 'nearest',
          axis: 'x',
        },
        scales: {
            x: {
                grid: {
                    color: '#404040'
                }
            },
            y: {
                grid: {
                    color: '#242424'
                }
            }
        },
        plugins: {
          'draw_vertical_line': {
          },
          legend: {
            labels: {
              usePointStyle: true,
            },
          },
          title: {
            display: true,
            text: 'SiM4',
          },
          tooltip: {
            backgroundColor: 'rgba(107, 107, 107, 0.8)',
            usePointStyle: true,
            position: 'nearest',
            xAlign: 'center',
            yAlign: 'bottom',
          },
        },
      }
    });
}

var g_chart = initChart();
requestChartData();
setInterval(requestChartData, 3000);