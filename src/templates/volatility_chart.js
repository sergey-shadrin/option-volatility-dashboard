g_chart = null;

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

        console.log(jsonResponse);
        if (g_chart == null)
        {
          initChart(jsonResponse);
        }
        else
        {
          updateChart(jsonResponse);
        }
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

      console.log('line position: ' + linePosition);
      console.log(scaleX.ticks[0]);
      console.log(scaleX.ticks[scaleX.ticks.length - 1])
      console.log(lineX);
      const meta = chart.getDatasetMeta(0); // first dataset is used to discover X coordinate of a point
      const data = meta.data;
      console.log(data);
      return linePosition;
  },

  renderVerticalLine: function(chartInstance, lineX) {
      const lineLeftOffset = this.getLinePosition(chartInstance, lineX);
      console.log(lineLeftOffset);
      console.log(chartInstance.scales);
      const scaleY = chartInstance.scales.y;
      console.log(scaleY);
      const context = chartInstance.ctx;
      console.log(context);

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
Chart.register(verticalLinePlugin);

function updateChart(chartData) {
    let labels = [];
    let stockVolatilities = [];
    let callAskVolatilities = [];
    let callBidVolatilities = [];
    let callLastPriceVolatilities = [];
    let putAskVolatilities = [];
    let putBidVolatilities = [];
    lastPrice = chartData['last_price'];
    strikesData = chartData['strikes'];
    strikesData.map(function(item) {
        labels.push(item['strike']);
        stockVolatilities.push(item['volatility']);
        callAskVolatilities.push(item['call_ask_volatility']);
        callBidVolatilities.push(item['call_bid_volatility']);
        callLastPriceVolatilities.push(item['call_last_price_volatility']);
        putAskVolatilities.push(item['put_ask_volatility']);
        putBidVolatilities.push(item['put_bid_volatility']);
    });

    g_chart.data.labels = labels;
    g_chart.data.datasets[0].data = stockVolatilities;
    g_chart.data.datasets[1].data = callAskVolatilities;
    g_chart.data.datasets[2].data = callBidVolatilities;
    g_chart.data.datasets[3].data = putAskVolatilities;
    g_chart.data.datasets[4].data = putBidVolatilities;
    g_chart.data.datasets[5].data = callLastPriceVolatilities;
    g_chart.options.plugins['draw_vertical_line'].lineX = lastPrice;
    g_chart.update();
}

function initChart(chartData) {
    let labels = [];
    let stockVolatilities = [];
    let callAskVolatilities = [];
    let callBidVolatilities = [];
    let callLastPriceVolatilities = [];
    let putAskVolatilities = [];
    let putBidVolatilities = [];
    lastPrice = chartData['last_price'];
    strikesData = chartData['strikes'];
    strikesData.map(function(item) {
        labels.push(item['strike']);
        stockVolatilities.push(item['volatility']);
        callAskVolatilities.push(item['call_ask_volatility']);
        callBidVolatilities.push(item['call_bid_volatility']);
        callLastPriceVolatilities.push(item['call_last_price_volatility']);
        putAskVolatilities.push(item['put_ask_volatility']);
        putBidVolatilities.push(item['put_bid_volatility']);
    });
    const pointRadius = 8;
    const pointHoverRadius = pointRadius + 1;
    const ctx = document.getElementById('volatilityChart');

    g_chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Volatility',
          data: stockVolatilities,
          fill: false,
          cubicInterpolationMode: 'monotone',
          tension: 0.2,
          borderColor: 'rgb(255, 0, 0)'
        }, {
          label: 'Call Ask',
          data: callAskVolatilities,
          fill: false,
          showLine: false,
          borderColor: 'rgb(255, 0, 0)',
          elements: {
            point: {
                radius: pointRadius,
                hoverRadius: pointHoverRadius,
                rotation: 180,
                backgroundColor: 'rgb(255, 0, 0)',
                pointStyle: 'triangle',
            }
          }
        }, {
          label: 'Call Bid',
          data: callBidVolatilities,
          fill: false,
          showLine: false,
          borderColor: 'rgb(0, 160, 0)',
          elements: {
            point: {
                radius: pointRadius,
                hoverRadius: pointHoverRadius,
                backgroundColor: 'rgb(0, 160, 0)',
                pointStyle: 'triangle',
            }
          }
        }, {
          label: 'Put Ask',
          data: putAskVolatilities,
          fill: false,
          showLine: false,
          borderColor: 'rgb(255, 160, 160)',
          elements: {
            point: {
                radius: pointRadius,
                hoverRadius: pointHoverRadius,
                rotation: 180,
                backgroundColor: 'rgb(255, 160, 160)',
                pointStyle: 'triangle',
            }
          }
        }, {
          label: 'Put Bid',
          data: putBidVolatilities,
          fill: false,
          showLine: false,
          borderColor: 'rgb(0, 255, 0)',
          elements: {
            point: {
                radius: pointRadius,
                hoverRadius: pointHoverRadius,
                backgroundColor: 'rgb(0, 255, 0)',
                pointStyle: 'triangle',
            }
          }
        }, {
          label: 'Call Last Price',
          data: callLastPriceVolatilities,
          fill: false,
          showLine: false,
          borderColor: 'rgb(255, 255, 0)',
          elements: {
            point: {
                radius: pointRadius     / 2,
                hoverRadius: pointHoverRadius,
                backgroundColor: 'rgb(255, 255, 0)',
                pointStyle: 'circle',
            }
          }
        }]
      },
      options: {
        animation: false,
        color: '#ffffff',
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
            lineX: lastPrice,
          }
        },
      },
    });
}

requestChartData();
setInterval(requestChartData, 3000);