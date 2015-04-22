var crane = angular.module("crane")

crane.controller("RepositoryControl", function($scope, $http, $routeParams) {
  $scope.repository = $routeParams.reponame.replace("--","/")
  $scope.registry_id = $routeParams.registry_id

  $scope.load_tags = function() {
    $http.get("/registry/" + String($scope.registry_id) + "/repository/" + String($scope.repository) + "/tags").success(function(data){
      $scope.tags = data.result
    })
  }

  $scope.detailed = function(tag) {
    if (tag.details && tag.details.active) { tag.details.active = false; }
    else
    {
      $http.get("/registry/" + String($scope.registry_id) + "/repository/" + String($scope.repository) + "/image/" + String(tag.name) ).success(function(data) {
         tag.details = {};
         tag.details.data = data.result;
         tag.details.active = true;
      });
    }
  }

  $scope.human_readable_size = function(size) {
    if (size > 4* 1024 * 1024)
    {
      return String(Math.round(size / (1024 * 1024))) + " Mb"
    }
    if (size > 4 * 1024)
    {
      return String(Math.round(size / (1024))) + " kb"
    }
    return String(size) + " b"
  }

  $scope.load_tags()
});
