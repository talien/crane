(function(){

angular.module('crane')

.controller('ContainerController', ContainerController);

ContainerController.$inject = ['$scope', '$http', '$modal'];


function ContainerController($scope, $http, $modal) {
  $scope.add_container = { 'container': {}, 'template':{} };
  
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

  $scope.search_dialog = search_dialog;
  $scope.load_containers = load_containers;
  $scope.load_hosts = load_hosts;
  $scope.load_templates = load_templates;
  $scope.remove_container = remove_container;
  $scope.start_deploy = start_deploy;
  $scope.cancel_deploy = cancel_deploy;
  $scope.start_container = start_container;
  $scope.stop_container = stop_container;
  $scope.deploy_container = deploy_container;
  $scope.container_details = container_details;
  $scope.container_logs = container_logs;

  function search_dialog() {
    var modalInstance = $modal.open({
      templateUrl: 'frontend/imagesearch.jade',
      controller: 'ImageSearchControl',
      size: 'lg',
      resolve: {
        image: function () {
          return $scope.add_container.container.image;
        }
      }
    });

    modalInstance.result.then(function (selectedItem) {
      $scope.add_container.container.image = selectedItem;
    })
  }

  function load_containers() {
    $scope.loading = true;
    $http.get("/container").success(function(data, status) {
      $scope.containers = data.result;
      $scope.loading = false;
    }).error(function(data, status) {
      $scope.loading = false;
    }) ;
  }

  function load_hosts() {
    $http.get("/host").success(function(data, status) {
      $scope.hosts = data.result;
    });
  }

  function load_templates() {
      $http.get("/template").success(function(data) {
          $scope.templates = data.result;
      });
  }

  function remove_container(container) {
    $http.delete("/host/" + String(container.hostid) + "/container/" + String(container.id));
    $scope.load_containers();
  }

  function start_deploy() {
    $scope.add_container.status = 'active';
  }

  function cancel_deploy() {
    $scope.add_container.status = 'inactive';
  }

  function start_container(container) {
    container.starting = true;
    $http.post("/host/" + String(container.hostid) + "/container/" + String(container.id) + "/start" ).success(function(data, status) {
      container.starting = false;
      $scope.load_containers();
    });
  }

  function stop_container(container) {
    container.stopping = true;
    $http.post("/host/" + String(container.hostid) + "/container/" + String(container.id) + "/stop" ).success(function(data, status) {
       container.stopping = false;
       $scope.load_containers();
    });
  }

  function deploy_container() {
    $scope.add_container.status = 'deploying';
    if ($scope.deployment_type == 'Raw') {
      data = { 'deploy' : 'raw', 'container' : $scope.add_container.container };
    } else {
      data = { 'deploy' : 'template', 'template' : $scope.add_container.selected_template, 'parameters' : $scope.add_container.template };
    }

    $http.post("/host/" + String($scope.add_container.container.host) + "/container", data).success(function(data) {
      $scope.add_container.status = 'finished';
      if (data.status == "error") {
        $scope.add_container.finish_error = true;
        $scope.add_container.output = data;
      } else {
        $scope.add_container.finish_error = false;
      }
      $scope.load_containers();
    }).error(function(data) {
      $scope.add_container.status = 'finished';
      $scope.add_container.output = { "error" : data };
      $scope.add_container.finish_error = false;
    });
  }

  function container_details(container) {
    if (container.logs) {
      container.logs.active = false;
    }
    if (container.details && container.details.active) {
      container.details.active = false;
    } else {
      $http.get("/host/" + String(container.hostid) + "/container/" + String(container.id) ).success(function(data) {
        container.details = {};
        container.details.data = data.result;
        container.details.active = true;
      });
    }
  }

  function container_logs(container) {
    if (container.details) {
      container.details.active = false;
    }
    if (container.logs && container.logs.active) {
      container.logs.active = false;
    } else {
      $http.get("/host/" + String(container.hostid) + "/container/" + String(container.id) + "/lastlog").success(function(data) {
        container.logs = {};
        container.logs.data = data.result;
        container.logs.active = true;
      });
    }
  }

  $scope.load_hosts();
  $scope.load_containers();
  $scope.load_templates();
}

})();
