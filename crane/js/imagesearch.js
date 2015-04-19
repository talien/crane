var crane = angular.module('crane');

crane.controller('ImageSearchControl', function ($scope, $http, $modalInstance) {
  $scope.cancel = function() {
    $modalInstance.dismiss('cancel');
  }

  $scope.search = function() {
    $http.get("/search",{ params: {q:$scope.query}}).success(function(data){
      $scope.results = data.result
    })
  }

  $scope.selected = function(item) {
    $scope.selected_image = item;
  }

  $scope.select = function () {
    $modalInstance.close($scope.selected_image.name);
  };

});
