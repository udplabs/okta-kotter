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

function showAlert(style, message) {
  var template = `
<div class="alert alert-${style} alert-dismissible fade show" role="alert">
  ${message}
  <button type="button" class="close" data-dismiss="alert" aria-label="Close">
    <span aria-hidden="true">&times;</span>
  </button>
</div>
  `;
  var elem = document.getElementById('alert');
  elem.innerHTML = template;
}
