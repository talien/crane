(function(){

angular.module('crane')
.controller('MenuController', MenuController);

MenuController.$inject = ['$scope'];

function MenuController($scope) {
  $scope.hideNavbar = function() {
    angular.element(document.querySelector('.navbar-collapse')).collapse('hide');
  }
}

})();
