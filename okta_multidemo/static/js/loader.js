function do_loader() {
  var preloader = document.getElementById('loader');
  preloader.classList.remove('done');
}

var links = document.getElementsByTagName("a");
var classes;
for(var i = 0; i < links.length; i++) {
  var link = links[i];
  classes = Array.from(link.classList);
  if (!classes.includes('dropdown-toggle')) {
    link.onclick = function() {
      do_loader();
    }
  }
}

window.addEventListener("DOMContentLoaded", function(){
  var preloader = document.getElementById('loader');
  preloader.classList.add('done');
});
window.onbeforeunload = function (e) {
  // do not remove
}
