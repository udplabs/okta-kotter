function ajax(url, method, data, callback, accessToken) {
  var req = new XMLHttpRequest();
  req.open(method, url, true);
  if (accessToken) {
    req.setRequestHeader('Authorization', 'Bearer ' + accessToken);
  }
  req.onreadystatechange = function () {
    if (req.readyState != 4) return;
    if (req.status != 200) {
      resp = {
        status: 'error',
        data: null,
        error: {
          status: req.status,
          description: req.statusText
        }
      }
    } else {
      resp = {
        status: 'ok',
        data: JSON.parse(req.responseText),
        error: null
      }
    }
    callback(resp);
  };
  req.send(data);
}
