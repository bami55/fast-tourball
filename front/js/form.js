const team1 = document.getElementById('team1');
const team2 = document.getElementById('team2');

// 初期表示
const createTeamSelectOption = (team) => {
  const option = document.createElement('option');
  option.text = team.name;
  option.value = team.id;
  return option;
}
const setTeams = async () => {
  const res = await apiGetData('/teams');
  if (res.teams) {
    res.teams.forEach(team => {
      team1.appendChild(createTeamSelectOption(team));
      team2.appendChild(createTeamSelectOption(team));
    });
    selectInitTeam();
  }
}
const selectInitTeam = async () => {
  const res = await apiGetData('/streaming_match');
  if (res.teams) {
    const streaming_team1 = res.teams.find(t => t.position == 1);
    const streaming_team2 = res.teams.find(t => t.position == 2);
    if (streaming_team1) team1.value = streaming_team1.team_id;
    if (streaming_team2) team2.value = streaming_team2.team_id;
  }
}
setTeams();

// 保存
const url = '/streaming_match';
document.getElementById('save').addEventListener('click', () => {
  const data = [{
      position: 1,
      id: team1.value,
    },
    {
      position: 2,
      id: team2.value,
    }
  ];
  apiPostData(url, data)
    .then(data => {
      if (data.status === 'success') {
        alert('保存しました！');
        location.reload();
      } else {
        alert('保存に失敗しました！');
      }
    });
});