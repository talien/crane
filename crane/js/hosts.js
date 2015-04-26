(function(){

angular.module('crane')

.controller('HostController', HostController);

HostController.$inject = ['$scope', '$http'];

function Host(name, host, username, sshkey, password) {
  this.name = name;
  this.host = host;
  this.username = username;
  this.sshkey = sshkey;
  this.password = password;
}

function HostController($scope, $http) {
  $scope.add_host = { 'active':false, 'host': new Host() };

  $scope.load_hosts = load_hosts;
  $scope.remove_host = remove_host;
  $scope.edit_host = edit_host;
  $scope.host_details = host_details;
  $scope.add_new_host = add_new_host;
  $scope.save_new_host = save_new_host;

  function load_hosts() {
    $http.get("/host").success(function(data, status) {
      $scope.hosts = data.result;
    });
  }

  function remove_host(host) {
    $http.delete("/host/" + String(host.id));
    $scope.load_hosts();
  }

  function edit_host(host) {
    $scope.add_host.active = true;
    $scope.add_host.host = host;
  }

  function host_details(host) {
    if (host.details && host.details.active) {
      host.details.active = false;
    } else {
      $http.get("/host/" + String(host.id)).success(function(data) {
         host.details = {};
         host.details.info = data.result;
         host.details.active = true;
      });
    }
  }

  function add_new_host($event) {
    $scope.add_host.active = true;
  }

  function save_new_host($event) {
    if ($scope.add_host.host.id) {
      $http.post("/host/" + String($scope.add_host.host.id), $scope.add_host.host);
    } else {
      $http.post("/host", $scope.add_host.host);
    }
    $scope.load_hosts();
    $scope.add_host.active = false;
  }

  $scope.load_hosts();
}

})();
