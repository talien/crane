var crane = angular.module('crane');

crane.controller('ContainerControl', function ($scope, $http) {
  $scope.restart_policies = [
    'no',
    'on-failure:5',
    'always'
  ];

  $scope.deployment_types = [
    'Raw',
    'Template'
  ]

  $scope.deployment_type = 'Raw';

  $scope.load_containers = function() {
    $scope.loading = true;
    $http.get("/container").success(function(data, status) {
      $scope.containers = data.result;
      $scope.loading = false;
    }).error(function(data, status) {
      $scope.loading = false;
    }) ;
  }

  $scope.load_hosts = function() {
    $http.get("/host").success(function(data, status) {
      $scope.hosts = data.result;
    });
  }

  $scope.load_hosts();

  $scope.load_containers();

  $scope.load_templates = function() {
      $http.get("/template").success(function(data) {
          $scope.templates = data.result;
      });
  };

  $scope.load_templates();

  $scope.remove_container = function(container) {
    $http.delete("/host/" + String(container.hostid) + "/container/" + String(container.id));
    $scope.load_containers();
  }

  $scope.start_deploy = function() {
    $scope.add_container.status = 'active';
  }

  $scope.cancel_deploy = function ()
  {
    $scope.add_container.status = 'inactive';
  }

  $scope.start_container = function(container) {
    container.starting = true;
    $http.post("/host/" + String(container.hostid) + "/container/" + String(container.id) + "/start" ).success(function(data, status) {
      container.starting = false;
      $scope.load_containers();
    });
  }

  $scope.stop_container = function(container) {
    container.stopping = true;
    $http.post("/host/" + String(container.hostid) + "/container/" + String(container.id) + "/stop" ).success(function(data, status) {
       container.stopping = false;
       $scope.load_containers();
    });
  }

  $scope.deploy_container = function() {
    $scope.add_container.status = 'deploying';
    if ($scope.deployment_type == 'Raw')
     {
       data = { 'deploy' : 'raw', 'container' : $scope.add_container.container };
     }
    else
     {
       data = { 'deploy' : 'template', 'template' : $scope.add_container.selected_template, 'parameters' : $scope.add_container.template };
     }
    $http.post("/host/" + String($scope.add_container.container.host) + "/container", data).success(function(data) {
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

  $scope.add_container = { 'container': {}, 'template':{} };

 });
