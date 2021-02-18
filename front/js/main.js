Chart.defaults.global.defaultFontSize = 16;
Chart.defaults.global.defaultFontFamily = "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif";

const player_chart_bg_colors = [
  'rgba(255, 255, 0, .2)',
  'rgba(0, 255, 255, .2)',
  'rgba(255, 0, 255, .2)',
  'rgba(0, 255, 0, .2)',
];
const player_chart_border_colors = [
  'rgb(255, 255, 0)',
  'rgb(0, 255, 255)',
  'rgb(255, 0, 255)',
  'rgb(0, 255, 0)',
];

const getScore = async () => {
  const getTeams = apiGetData('/streaming_match');
  const getScores = apiGetData('/scores_all');
  const [resTeams, resScores] = await Promise.all([getTeams, getScores]);
  if (!resTeams.teams || !resScores.scores) return;

  const team1 = resTeams.teams.find(t => t.position == 1);
  const team2 = resTeams.teams.find(t => t.position == 2);
  const team1Scores = resScores.scores.filter(x => x.team_id == team1.team_id);
  const team2Scores = resScores.scores.filter(x => x.team_id == team2.team_id);

  const chartData = {
    team1: {
      name: team1.team_name,
      scores: team1Scores,
    },
    team2: {
      name: team2.team_name,
      scores: team2Scores,
    }
  };
  createChart(chartData);
}

const ctx1 = document.getElementById('chart1');
const ctx2 = document.getElementById('chart2');

const createChartOptions = (teamName) => {
  return {
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
      text: teamName,
    },
  };
}

const createChartDataset = (score, index) => {
  return {
    label: score.player_name,
    fontSize: 24,
    backgroundColor: player_chart_bg_colors[index],
    borderColor: player_chart_border_colors[index],
    borderWidth: 3,
    pointRadius: 0,
    data: [
      score.goals_parameter,
      score.shots_parameter,
      score.assists_parameter,
      score.saves_parameter,
      score.demos_parameter,
    ]
  };
}

const createChart = (chartData) => {
  const labels = ['Goals', 'Shots', 'Assists', 'Saves', 'Demos'];
  const team1Options = createChartOptions(chartData.team1.name);
  const team2Options = createChartOptions(chartData.team2.name);

  const team1Scores = chartData.team1.scores;
  const team2Scores = chartData.team2.scores;

  const team1Datasets = [];
  const team2Datasets = [];
  team1Scores.forEach((score, index) => {
    const dataset = createChartDataset(score, index);
    team1Datasets.push(dataset);
  });
  team2Scores.forEach((score, index) => {
    const dataset = createChartDataset(score, index);
    team2Datasets.push(dataset);
  });

  const chart1 = new Chart(ctx1, {
    type: 'radar',
    data: {
      labels: labels,
      datasets: team1Datasets,
    },
    options: team1Options
  });
  const chart2 = new Chart(ctx2, {
    type: 'radar',
    data: {
      labels: labels,
      datasets: team2Datasets,
    },
    options: team2Options
  });
};

getScore();