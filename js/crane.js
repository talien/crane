var crane = angular.module('craneApp', [], function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});

crane.config(function($routeProvider){
  $routeProvider.when("/hosts",
    {
      templateUrl: "/templates/hosts.jade",
      controller: "CraneControl"
    }).when("/containers",
    {
      templateUrl: "/templates/containers.jade",
      controller: "CraneControl"
    });
});

function Host(name, host, username, sshkey, password)
{
  this.name = name;
  this.host = host;
  this.username = username;
  this.sshkey = sshkey;
  this.password = password;
}

crane.controller('CraneControl', function ($scope, $http) {
  $scope.restart_policies = [
    'no',
    'on-failure:5',
    'always'
  ];

  $scope.load_hosts = function() {
    $http.get("/host").success(function(data, status) {
      $scope.hosts = data.result;
    });
  }

  $scope.load_containers = function() {
    $http.get("/container").success(function(data, status) {
      $scope.containers = data.result;
    });
  }

  $scope.load_hosts();

  $scope.load_containers();

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

  $scope.remove_container = function(container) {
    $http.delete("/host/" + String(container.hostid) + "/container/" + String(container.id));
    $scope.load_containers();
  }
 
  $scope.add_new_host = function($event) {
    $scope.add_host.active = true;
  }

  $scope.start_deploy = function() {
    $scope.add_container.status = 'active';
  }

  $scope.start_container = function(container) {
    $http.post("/host/" + String(container.hostid) + "/container/" + String(container.id) + "/start" );
    $scope.load_containers();
  }

  $scope.stop_container = function(container) {
    $http.post("/host/" + String(container.hostid) + "/container/" + String(container.id) + "/stop" );
    $scope.load_containers();
  }

  $scope.deploy_container = function() {
    $scope.add_container.status = 'deploying';
    $http.post("/host/" + String($scope.add_container.container.host) + "/container", $scope.add_container.container).success(function(data) {
       $scope.add_container.status = 'finished';
       $scope.add_container.output = data;
       $scope.load_containers();
    }).error(function(data) {
       $scope.add_container.status = 'finished';
       $scope.add_container.output = "Error happened:" + data;
    });
  }

  $scope.container_details = function(container) {
    if (container.logs) { container.logs.active = false; }
    if (container.details && container.details.active) { container.details.active = false; }
    else
    {
      $http.get("/host/" + String(container.hostid) + "/container/" + String(container.id) ).success(function(data) {
         container.details = {};
         container.details.data = data.result;
         container.details.active = true;
      });
    }
  }
  
  $scope.container_logs = function(container) {
    if (container.details) { container.details.active = false; }
    if (container.logs && container.logs.active) { container.logs.active = false; }
    else
    {
      $http.get("/host/" + String(container.hostid) + "/container/" + String(container.id) + "/lastlog").success(function(data) {
         container.logs = {};
         container.logs.data = data.result;
         container.logs.active = true;
      });
    }
  }

  $scope.add_host = { 'active':false, 'host': new Host() };

  $scope.add_container = { 'active':false, 'container': {} };

  $scope.save_new_host = function($event) {
    $http.post("/host", $scope.add_host.host)
    $scope.load_hosts()
    $scope.add_host.active = false;
  }
});
