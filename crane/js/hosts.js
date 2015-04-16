var crane = angular.module('crane');

function Host(name, host, username, sshkey, password)
{
  this.name = name;
  this.host = host;
  this.username = username;
  this.sshkey = sshkey;
  this.password = password;
}

crane.controller('HostControl', function($scope, $http) {
  $scope.load_hosts = function() {
    $http.get("/host").success(function(data, status) {
      $scope.hosts = data.result;
    });
  }

  $scope.load_hosts();

  $scope.remove_host = function(host) {
    $http.delete("/host/" + String(host.id));
    $scope.load_hosts();

  }

  $scope.host_details = function(host) {
    if (host.details && host.details.active) { host.details.active = false; }
    else
    {
      $http.get("/host/" + String(host.id)).success(function(data) {
         host.details = {};
         host.details.info = data.result;
         host.details.active = true;
      });
    }

  }

  $scope.add_new_host = function($event) {
    $scope.add_host.active = true;
  }

  $scope.add_host = { 'active':false, 'host': new Host() };

  $scope.save_new_host = function($event) {
    $http.post("/host", $scope.add_host.host)
    $scope.load_hosts()
    $scope.add_host.active = false;
  }
});
