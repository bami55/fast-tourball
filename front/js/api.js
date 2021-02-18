const endpoint = 'https://8vmse5.deta.dev';

async function apiGetData(url, params) {
  let requestUrl = endpoint + url;
  if (params) {
    const queryParams = new URLSearchParams(params);
    requestUrl += `?${queryParams}`;
  }
  const response = await fetch(requestUrl);
  return response.json();
}

async function apiPostData(url, data = {}) {
  const requestUrl = endpoint + url;
  const response = await fetch(requestUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  return response.json();
}
