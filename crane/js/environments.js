(function(){

angular.module('crane')

.controller('EnvironmentsController', EnvironmentsController);

EnvironmentsController.$inject = ['$scope', '$http', '$modal'];

function EnvironmentsController($scope, $http, $modal) {
  $scope.add_environment = { 'active':false, 'environment' : {} }

  $scope.load_environments = load_environments;
  $scope.start_add_environment = start_add_environment;
  $scope.cancel_add_environment = cancel_add_environment;
  $scope.do_add_environment = do_add_environment;
  $scope.start_add_host = start_add_host;
  $scope.cancel_add_host = cancel_add_host;
  $scope.do_add_host = do_add_host;
  $scope.load_hosts = load_hosts;
  $scope.remove_host = remove_host;
  $scope.remove_environment = remove_environment;

  function load_hosts() {
    $http.get("/host").success(function(data, status) {
      $scope.hosts = data.result;
    });
  }

  function load_environments() {
    $http.get("/environment").success(function(data, status) {
      $scope.environments = data.result;
    });
  }

  function do_add_environment() {
     $http.post("/environment", $scope.add_environment.environment).success(function(data) {
        $scope.load_environments();
     });
     $scope.add_environment.active = false;
  };

  function do_add_host(environment) {
     $http.post("/environment/" + String(environment.id) + "/host", {'id': environment.add_host.id} ).success(function(data) {
        $scope.load_environments();
     });
     environment.add_active = false;
  };

  function start_add_environment() { $scope.add_environment.active = true; };

  function start_add_host(environment) { environment.add_active = true; };

  function cancel_add_environment() { $scope.add_environment.active = false; };

  function cancel_add_host(environment) { environment.add_active = false; };

  function remove_host(environment, host) {
     $http.delete("/environment/" + String(environment.id) + "/host/" + String(host.id)).success(function(data) {
       $scope.load_environments();
     });
  }

  function remove_environment(environment) {
     $http.delete("/environment/" + String(environment.id)).success(function(data) {
       $scope.load_environments();
     });
  }

  $scope.load_environments();
  $scope.load_hosts();
}

})();
