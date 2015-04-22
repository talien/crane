var crane = angular.module("crane");

crane.controller("RegistryControl", function($scope, $http) {

  $scope.providers = ['dockerhub','private']

  $scope.results = [];

  $scope.load_registries = function() {
    $http.get("/registry").success(function(data){
       $scope.registries = data.result;
    });
  };

  $scope.load_registries();

  $scope.add_registry = { 'active':false, 'registry' : {} }

  $scope.start_add_registry = function() { $scope.add_registry.active = true; };

  $scope.cancel_add_registry = function() { $scope.add_registry.active = false; };

  $scope.do_add_registry = function() {
     $http.post("/registry", $scope.add_registry.registry).success(function(data) {
        $scope.load_registries();
     });
     $scope.add_registry.active = false;
  };

  $scope.remove_registry = function(registry) {
    $http.delete("/registry/" + String(registry.id)).success(function(){
        $scope.load_registries();
    });
  }

  $scope.search = function() {
    $http.get("/search",{ params: {q:$scope.query}}).success(function(data){
        $scope.results = data.result
    })
  }

  $scope.safe_repository_name = function(repository) {
    return repository.name.replace("/","--")
  }

});
