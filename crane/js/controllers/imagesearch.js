var crane = angular.module('crane');

crane.controller('ImageSearchControl', function ($scope, $http, $modalInstance, image) {
  $scope.query = image

  $scope.cancel = function() {
    $modalInstance.dismiss('cancel');
  }

  $scope.search = function() {
    $scope.searching = true;
    $http.get("/search",{ params: {q:$scope.query}}).success(function(data){
      $scope.results = data.result
      $scope.searching = false;
    })
  }

  $scope.selected = function(item) {
    $scope.selected_image = item;
  }

  $scope.select = function () {
    $modalInstance.close($scope.selected_image.name);
  };

  if ($scope.query && $scope.query.length != 0) {
    $scope.search()
  }

});
