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

function cb(resp) {
  if (resp.error) {
    showAlert('danger', 'An error occurred: ' + resp.error.description);
  }
  console.log(resp);
}

function itemAction(id, apiUrl, userId) {
  var elem = document.getElementById('itemCt-'+id);
  var ct = parseInt(elem.innerText);
  var newCt = ct - 1;
  elem.innerText = newCt;
  var btn = document.getElementById('btn-'+id);
  btn.disabled = true;
  btn.setAttribute("class", "btn btn-secondary btn-sm");
  btn.innerHTML = '<span><i class="fa fa-hourglass"></i> Pending</span>';
  var accessToken = document.cookie.replace(/(?:(?:^|.*;\s*)access_token\s*\=\s*([^;]*).*$)|^.*$/, "$1");
  data = JSON.stringify({
    userId: userId,
    itemId: id,
    ct: 1
  });
  var result = ajax(apiUrl + '/orders', 'POST', data, cb, accessToken);
}
