function locate(callback, errorCallback) {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      function(position) {
        if (callback) callback();
      },
      function(error) {
        if (errorCallback) errorCallback();
      },
      {
        enableHighAccuracy: true,
        timeout: 30000,
        maximumAge: 0
      }
    );
  } else {
    if (errorCallback) errorCallback();
  }
}

function information() {
  var params = new URLSearchParams(window.location.search);
  if (params.has('redirect')) {
    document.getElementById('redirect').value = params.get('redirect');
  }
}
