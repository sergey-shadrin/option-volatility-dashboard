const pointRadius = 8;
const pointHoverRadius = pointRadius + 4;
const DEFAULT_SETTINGS_MAP = {
    'Volatility': {
        fill: false,
        cubicInterpolationMode: 'monotone',
        tension: 0.2,
        elements: {
            point: {
                radius: pointRadius / 2,
                hoverRadius: pointHoverRadius,
            }
        }
    },
    'Ask': {
        hidden: true,
        fill: false,
        showLine: false,
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
        elements: {
            point: {
                radius: pointRadius / 2,
                hoverRadius: pointHoverRadius,
                pointStyle: 'circle',
            }
        }
    }
}

var g_colorSettings = {
    'Volatility': {
        color: {
            r: 255,
            g: 0,
            b: 0,
        },
        colorDelta: {
            r: -64,
            g: 0,
            b: 0,
        },
    },
    'Call Ask': {
        color: {
            r: 255,
            g: 0,
            b: 0,
        },
        colorDelta: {
            r: -64,
            g: 0,
            b: 0,
        },
    },
    'Call Bid': {
        color: {
            r: 0,
            g: 160,
            b: 0,
        },
        colorDelta: {
            r: 0,
            g: -32,
            b: 0,
        },
    },
    'Call Last Price': {
        color: {
            r: 255,
            g: 187,
            b: 0,
        },
        colorDelta: {
            r: -64,
            g: -64,
            b: 0,
        },
    },
    'Put Ask': {
        color: {
            r: 255,
            g: 160,
            b: 160,
        },
        colorDelta: {
            r: -64,
            g: -32,
            b: -32,
        },
    },
    'Put Bid': {
        color: {
            r: 0,
            g: 255,
            b: 0,
        },
        colorDelta: {
            r: 0,
            g: -64,
            b: 0,
        },
    },
    'Put Last Price': {
        color: {
            r: 255,
            g: 255,
            b: 0,
        },
        colorDelta: {
            r: -64,
            g: -64,
            b: 0,
        },
    },
}

const getOrCreateLegendBlock = (chart, id) => {
    const legendContainer = document.getElementById(id);
    let legendBlock = legendContainer.querySelector('div');
  
    if (!legendBlock) {
        legendBlock = document.createElement('div');
        legendBlock.style.display = 'flex';
        legendBlock.style.flexDirection = 'row';
        legendBlock.style.margin = 0;
        legendBlock.style.padding = 0;
    
        legendContainer.appendChild(legendBlock);
    }
  
    return legendBlock;
};

const htmlLegendPlugin = {
    id: 'htmlLegend',
    afterUpdate(chart, args, options) {
        const legendBlock = getOrCreateLegendBlock(chart, options.containerID);

        // Remove old legend items
        while (legendBlock.firstChild) {
            legendBlock.firstChild.remove();
        }

        // Reuse the built-in legendItems generator
        const items = chart.options.plugins.legend.labels.generateLabels(chart);

        let commonLabelPrefix = '';
        let seriesUl = null;
        items.forEach(item => {
            const labelText = item.text;
            const firstSpaceIndex = labelText.indexOf(' ');
            let labelPrefix = labelText.slice(0, firstSpaceIndex);
            const labelSuffix = labelText.slice(firstSpaceIndex + 1);
            
            if (labelPrefix != commonLabelPrefix) {
                commonLabelPrefix = labelPrefix;
                seriesBlock = document.createElement('div');
                seriesBlock.style.margin = 0;
                seriesBlock.style.padding = 0;
                seriesBlock.style.marginLeft = '10px';

                let seriesTitle = document.createElement('h4');
                seriesTitle.style.cursor = 'pointer';
                seriesTitle.style.margin = 0;
                seriesTitle.style.marginBottom = '5px';
                seriesTitle.style.padding = 0;
                const text = document.createTextNode(commonLabelPrefix);
                seriesTitle.appendChild(text);

                seriesBlock.appendChild(seriesTitle);

                let isSeriesVisible = false;
                items.forEach(labelItem => {
                    if (labelItem.text.indexOf(labelPrefix) == 0) {
                        if (!labelItem.hidden) {
                            isSeriesVisible = true;
                        }
                    }
                });
                seriesTitle.style.textDecoration = !isSeriesVisible ? 'line-through' : '';
                seriesTitle.style.color = !isSeriesVisible ? 'gray' : item.fontColor;

                seriesTitle.onclick = () => {
                    //switch visibility to opposite value
                    items.forEach(labelItem => {
                        if (labelItem.text.indexOf(labelPrefix) == 0) {
                            chart.setDatasetVisibility(labelItem.datasetIndex, !isSeriesVisible);
                        }
                    });

                    chart.update();
                };

                seriesUl = document.createElement('ul');
                seriesUl.style.margin = 0;
                seriesUl.style.padding = 0;
                seriesBlock.appendChild(seriesUl);

                legendBlock.appendChild(seriesBlock);
            }

            const li = document.createElement('li');
            li.style.alignItems = 'center';
            li.style.cursor = 'pointer';
            li.style.display = 'flex';
            li.style.flexDirection = 'row';
            li.style.margin = 0;
            li.style.marginBottom = '2px';

            li.onclick = () => {
                chart.setDatasetVisibility(item.datasetIndex, !chart.isDatasetVisible(item.datasetIndex));
                chart.update();
            };

            // Color box
            const boxSpan = document.createElement('span');
            boxSpan.style.background = item.fillStyle;
            boxSpan.style.borderColor = item.strokeStyle;
            boxSpan.style.borderWidth = item.lineWidth + 'px';
            boxSpan.style.display = 'inline-block';
            boxSpan.style.flexShrink = 0;
            boxSpan.style.height = '20px';
            boxSpan.style.marginRight = '10px';
            boxSpan.style.width = '20px';

            // Text
            const textContainer = document.createElement('p');
            textContainer.style.margin = 0;
            textContainer.style.padding = 0;
            textContainer.style.textDecoration = item.hidden ? 'line-through' : '';
            textContainer.style.color = item.hidden ? 'gray' : item.fontColor;

            const text = document.createTextNode(labelSuffix);
            textContainer.appendChild(text);

            li.appendChild(boxSpan);
            li.appendChild(textContainer);
            seriesUl.appendChild(li);
        });
    }
};

function getColorByLabel(label) {
    let colorSettings = getColorSettingsByLabel(label);
    let colorObject = colorSettings.color;
    let colorDelta = colorSettings.colorDelta;
    let colorArr = [colorObject.r, colorObject.g, colorObject.b, 0.8];
    let colorString = 'rgba(' + colorArr.join(', ') + ')';

    const MAX_COLOR = 255;
    for (let colorPart in colorObject) {
        if (colorObject.hasOwnProperty(colorPart)) {
            let newColorPart = colorObject[colorPart] + colorDelta[colorPart];
            if (newColorPart > MAX_COLOR) {
                newColorPart = newColorPart - MAX_COLOR;
            }
            else if (newColorPart < 0) {
                newColorPart = MAX_COLOR + newColorPart;
            }
            colorObject[colorPart] = newColorPart;
        }
    }

    return colorString;
}

function getColorSettingsByLabel(label) {
    for (let labelSuffix in g_colorSettings) {
        if (g_colorSettings.hasOwnProperty(labelSuffix) && label.endsWith(labelSuffix)) {
            return g_colorSettings[labelSuffix];
        }
    }
    return {}
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
    let color = getColorByLabel(label);
    datasetByLabel.backgroundColor = color;
    datasetByLabel.borderColor = color;
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
    Chart.register(htmlLegendPlugin);

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
          mode: 'point',
          axis: 'xy',
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
          'draw_vertical_line': {},
          htmlLegend: {
            // ID of the container to put the legend in
            containerID: 'legend-container',
          },
          legend: {
            display: false,
          },
          tooltip: {
            backgroundColor: 'rgba(107, 107, 107, 0.8)',
            xAlign: 'center',
            yAlign: 'bottom',
            usePointStyle: true
          },
        },
      }
    });
}

var g_chart = initChart();
requestChartData();
setInterval(requestChartData, 3000);