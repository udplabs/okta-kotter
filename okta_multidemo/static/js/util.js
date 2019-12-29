function ajax(url, method, data, accessToken, callback) {
  var req = new XMLHttpRequest();
  req.open(method, url, true);
  req.setRequestHeader('Authorization', 'Bearer ' + accessToken);
  req.onreadystatechange = function () {
    if (req.readyState != 4 || req.status != 200) return;
    var resp = JSON.parse(req.responseText);
    callback(resp);
  };
  req.send(data);
}
