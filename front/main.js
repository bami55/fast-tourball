Chart.defaults.global.defaultFontSize = 16;
Chart.defaults.global.defaultFontFamily = "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif";

const ctx1 = document.getElementById('chart1');
const ctx2 = document.getElementById('chart2');

const options = {
  legend: {
    labels: {
      fontColor: '#fff',
    }
  },
  scale: {
    angleLines: {
      display: false
    },
    gridLines: {
      color: 'rgba(71, 245, 231, .5)',
    },
    ticks: {
      suggestedMin: 0,
      suggestedMax: 30,
      display: false,
    },
    pointLabels: {
      fontSize: 24,
      fontColor: '#fff',
    },
  },
  title: {
    display: true,
    fontSize: 36,
    fontColor: '#fff',
    text: 'あしたはあしたのゆめをみて',
  },
};

const data = {
  labels: ['Goals', 'Shots', 'Assists', 'Saves', 'Demos'],
  datasets: [{
      label: 'OLPiX',
      backgroundColor: 'rgba(255, 255, 0, .2)',
      borderColor: 'rgb(255, 255, 0)',
      borderWidth: 1,
      pointRadius: 0,
      data: [8, 10, 4, 2, 30]
    },
    {
      label: 'Shaolon',
      backgroundColor: 'rgba(0, 255, 255, .2)',
      borderColor: 'rgb(0, 255, 255)',
      borderWidth: 1,
      pointRadius: 0,
      data: [24, 32, 8, 5, 18]
    },
    {
      label: 'Burn',
      backgroundColor: 'rgba(255, 0, 255, .2)',
      borderColor: 'rgb(255, 0, 255)',
      borderWidth: 1,
      pointRadius: 0,
      data: [18, 27, 15, 24, 7]
    }
  ]
};

const chart1 = new Chart(ctx1, {
  type: 'radar',
  data: data,
  options: options
});
const chart2 = new Chart(ctx2, {
  type: 'radar',
  data: data,
  options: options
});