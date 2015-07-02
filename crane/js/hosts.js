(function(){

angular.module('crane')

.controller('HostController', HostController);

HostController.$inject = ['$scope', '$http', '$modal'];

function Host(name, host, username, sshkey, password) {
  this.name = name;
  this.host = host;
  this.username = username;
  this.sshkey = sshkey;
  this.password = password;
}

function cloneHost(from, to) {
  to.id = from.id;
  to.name = from.name;
  to.host = from.host;
  to.username = from.username;
  to.sshkey = from.sshkey;
  to.password = from.password;

  return to;
}

function HostController($scope, $http, $modal) {
  $scope.add_host = { 'host': new Host() };

  $scope.load_hosts = load_hosts;
  $scope.remove_host = remove_host;
  $scope.edit_host = edit_host;
  $scope.host_details = host_details;
  $scope.add_new_host = add_new_host;
  $scope.save_new_host = save_new_host;

  function load_hosts() {
    $http.get("/host").success(function(data, status) {
      $scope.hosts = data.result;
    });
  }

  function remove_host(host) {
    $http.delete("/host/" + String(host.id));
    $scope.load_hosts();
  }

  function edit_host(hostItem) {

    var modalInstance = $modal.open({
      templateUrl: '/frontend/host_edit_modal.jade',
      controller: function($scope, $modalInstance, host) {
        $scope.host = cloneHost(host, {});

        $scope.confirmText = host.id ? 'Edit' : 'Add';

        $scope.ok = function () {
          $modalInstance.close(cloneHost($scope.host, host));
        };

        $scope.cancel = function () {
          $modalInstance.dismiss('cancel');
        };
      },
      resolve: {
        host: function () {
          return hostItem;
        }
      }
    });

    modalInstance.result.then(function (hostRet) {
      $scope.add_host.host = hostRet;
      save_new_host();
    });
  }

  function host_details(host) {
    if (host.details && host.details.active) {
    } else {
      $http.get("/host/" + String(host.id)).success(function(data) {
         host.details = {};
         host.details.info = data.result;
      });
    }
  }

  function add_new_host(hostItem) {
    $scope.edit_host(new Host());
  };

  

  function save_new_host($event) {
    if ($scope.add_host.host.id) {
      $http.post("/host/" + String($scope.add_host.host.id), $scope.add_host.host);
    } else {
      $http.post("/host", $scope.add_host.host);
    }
    $scope.load_hosts();
  }

  $scope.load_hosts();
}

})();
