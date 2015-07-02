(function(){

angular.module('crane')

.controller('EnvironmentsController', EnvironmentsController);

EnvironmentsController.$inject = ['$scope', '$http', '$modal'];

function EnvironmentsController($scope, $http, $modal) {
  $scope.start_add_environment = start_add_environment;
  $scope.start_add_host = start_add_host;
  $scope.remove_host = remove_host;
  $scope.remove_environment = remove_environment;

  function start_add_environment() {
    var modalInstance = $modal.open({
      templateUrl: '/frontend/environment_edit_modal.jade',
      controller: function($scope, $modalInstance) {
        $scope.environment = {};

        $scope.ok = function () {
          $modalInstance.close($scope.environment);
        };

        $scope.cancel = function () {
          $modalInstance.dismiss('cancel');
        };
      }
    });

    modalInstance.result.then(function (envRet) {
      do_add_environment(envRet);
    });
  }

  function do_add_environment(env) {
    $http.post("/environment", env).success(function(data) {
      load_environments();
    });
  }

  function start_add_host(environment) {
    var modalInstance = $modal.open({
      templateUrl: '/frontend/environment_host_modal.jade',
      controller: function($scope, $modalInstance, env, hosts) {
        $scope.environment = env;
        $scope.hosts = hosts;
        $scope.host = '';

        $scope.ok = function () {
          $modalInstance.close({
            'env' : $scope.environment,
            'host' : $scope.host
          });
        };

        $scope.cancel = function () {
          $modalInstance.dismiss('cancel');
        };
      },
      resolve: {
        env: function () {
          return environment;
        },
        hosts: function() {
          return $scope.hosts;
        }
      }
    });

    modalInstance.result.then(function (ret) {
      do_add_host(ret.env, ret.host);
    });
  }

  function do_add_host(environment, host) {
    $http.post("/environment/" + String(environment.id) + "/host", {'id': host.id} ).success(function(data) {
      load_environments();
    });
  }

  function cancel_add_host(environment) { environment.add_active = false; }

  function remove_host(environment, host) {
    $http.delete("/environment/" + String(environment.id) + "/host/" + String(host.id)).success(function(data) {
      load_environments();
    });
  }

  function remove_environment(environment) {
    $http.delete("/environment/" + String(environment.id)).success(function(data) {
      load_environments();
    });
  }

  function load_environments() {
    $http.get("/environment").success(function(data, status) {
      $scope.environments = data.result;
    });
  }

  function load_hosts() {
    $http.get("/host").success(function(data, status) {
      $scope.hosts = data.result;
    });
  }

  load_environments();
  load_hosts();
}

})();
