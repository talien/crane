(function(){

angular.module("crane")
.controller("RegistryControl", RegistryControl);

RegistryControl.$inject = ['$scope', '$http', '$modal'];

function Registry(name, url, username, password, provider) {
  this.name = name;
  this.url = url;
  this.username = username;
  this.password = password;
  this.provider = provider;
}

function RegistryControl($scope, $http, $modal) {
  var providers = ['dockerhub','private']

  $scope.registries = [];
  $scope.results = [];

  $scope.load_registries = function() {
    $http.get("/registry").success(function(data){
       $scope.registries = data.result;
    });
  };

  $scope.load_registries();

  $scope.add_registry = new Registry();

  $scope.start_add_registry = function() {
    var modalInstance = $modal.open({
      templateUrl: 'frontend/registry_edit_modal.jade',
      controller: function($scope, $modalInstance, registry, providers) {
        $scope.add_registry = registry;
        $scope.providers = providers;

        $scope.ok = ok;
        $scope.cancel = cancel;

        function ok() {
          $modalInstance.close($scope.add_registry);
        }

        function cancel() {
          $modalInstance.dismiss('cancel');
        }
      },
      resolve: {
        registry: function () {
          return new Registry();
        },
        providers: function() {
          return providers;
        }
      }
    });

    modalInstance.result.then(function (registry) {
      $scope.add_registry = registry;
      $scope.do_add_registry();
    });
  };

  $scope.start_edit_registry = function(registry) {
    var modalInstance = $modal.open({
      templateUrl: 'frontend/registry_edit_modal.jade',
      controller: function($scope, $modalInstance, registry, providers) {
        $scope.add_registry = registry;
        $scope.providers = providers;

        $scope.ok = ok;
        $scope.cancel = cancel;

        function ok() {
          $modalInstance.close($scope.add_registry);
        }

        function cancel() {
          $modalInstance.dismiss('cancel');
        }
      },
      resolve: {
        registry: function () {
          return registry;
        },
        providers: function() {
          return providers;
        }
      }
    });

    modalInstance.result.then(function (registry) {
      $scope.add_registry = registry;
      $scope.do_add_registry();
    });
  };

  $scope.do_add_registry = function() {
    var url = '/registry';
    if ($scope.add_registry.id) {
      url += '/' + $scope.add_registry.id;
    }
     $http.post(url, $scope.add_registry).success(function(data) {
        $scope.load_registries();
     });
  };

  $scope.remove_registry = function(registry) {
    $http.delete("/registry/" + String(registry.id)).success(function(){
        $scope.load_registries();
    });
  }

  $scope.search = function() {
    $scope.searching = true;
    $http.get("/search",{ params: {q:$scope.query}}).success(function(data){
        $scope.results = data.result
        $scope.searching = false;
    })
  }

  $scope.safe_repository_name = function(repository) {
    return repository.name.replace("/","--")
  }

}
  
})();
