(function(){

angular.module('crane')
.directive('craneAutoComplete', craneAutoComplete)
.controller('TemplatesControl', TemplatesControl);

craneAutoComplete.$inject = ['$timeout'];
TemplatesControl.$inject = ['$scope', '$http', '$modal'];

function craneAutoComplete($timeout) {
  return function(scope, iElement, iAttrs) {
    var prefix = "";
    var suffix = "";
    var deepset = function (obj, str, val) {
      str = str.split(".");
      while (str.length > 1)
        obj = obj[str.shift()];
      return obj[str.shift()] = val;
    };
    iElement.autocomplete({
      source: function(request, response) {
        var res = [];
        var opening = request.term.lastIndexOf("%(");
        var closing = request.term.lastIndexOf(")%");
        for (var i=0; i<scope[iAttrs.uiItems].length; i++) {
          if (opening > closing) {
            prefix = request.term.substring(0,opening+2);
            var leftover = request.term.substring(opening+2);
            var patt = new RegExp("([0-9a-zA-Z_])*");
            var term = patt.exec(leftover)[0];
            suffix = request.term.substring(opening+2+term.length);
            if (scope[iAttrs.uiItems][i].name.indexOf(term) === 0) {
                 res.push(scope[iAttrs.uiItems][i].name);
            }
          }
        }
        response(res);
      },
      select: function(event, ui) {
        value = prefix + ui.item.label + ")%" + suffix;
        deepset(scope,iAttrs.ngModel, value);
        scope.$apply();
        iElement.trigger('input');
        return false;
      }
    });
  };
}

function TemplatesControl($scope, $http, $modal) {
  $scope.parameters = [];

  $scope.load_templates = function() {
     $http.get("/template").success(function(data) {
     $scope.templates = data.result;
   });
  };

  $scope.search_dialog = function() {
    var modalInstance = $modal.open({
      templateUrl: 'frontend/imagesearch.jade',
      controller: 'ImageSearchControl',
      size: 'lg',
      resolve: {
        image: function () {
          return $scope.add_template.deploy.image;
        }
      }
    });

    modalInstance.result.then(function (selectedItem) {
      $scope.add_template.deploy.image = selectedItem;
    });
  };

  $scope.load_templates();

  $scope.start_add_template = function() {
    $scope.add_template = { 'active':true, 'deploy': {} };
    $scope.parameters = [];

    var modalInstance = $modal.open({
      templateUrl: '/frontend/template_edit_modal.jade',
      controller: function($scope, $modalInstance, template, parameters) {
        $scope.add_template = template;
        $scope.parameters = parameters;

        $scope.confirmText = template.id ? 'Edit' : 'Add';

        $scope.add_parameter = function() {
          $scope.parameters.push({});
        };

        $scope.ok = function () {
          $modalInstance.close({
            template : $scope.add_template,
            parameters : $scope.parameters
          });
        };

        $scope.cancel = function () {
          $modalInstance.dismiss('cancel');
        };
      },
      resolve: {
        template: function() {
          return $scope.add_template;
        },
        parameters: function() {
          return $scope.parameters;
        }
      }
    });

    modalInstance.result.then(function (data) {
      $scope.add_template = data.template;
      $scope.parameters = data.parameters;
      $scope.save_template();
    });
  };

  $scope.start_edit_template = function(template) {
    var modalInstance = $modal.open({
      templateUrl: '/frontend/template_edit_modal.jade',
      controller: function($scope, $modalInstance, template, parameters) {
        $scope.add_template = template;
        $scope.parameters = parameters;

        $scope.confirmText = template.id ? 'Edit' : 'Add';

        $scope.add_parameter = function() {
          $scope.parameters.push({});
        };

        $scope.ok = function () {
          $modalInstance.close({
            template : $scope.add_template,
            parameters : $scope.parameters
          });
        };

        $scope.cancel = function () {
          $modalInstance.dismiss('cancel');
        };
      },
      resolve: {
        template: function () {
          return template;
        },
        parameters: function() {
          return template.parameters;
        }
      }
    });

    modalInstance.result.then(function (data) {
      $scope.add_template = data.template;
      $scope.parameters = data.parameters;
      $scope.save_template();
    });
  };

  $scope.delete_template = function(template) {
     $http.delete("/template/" + String(template.id));
     $scope.load_templates();
  };

  $scope.save_template = function() {
    var data = { 'name' : $scope.add_template.name, 'template': { 'parameters': $scope.parameters, 'deploy': $scope.add_template.deploy } };
    var url = '/template';
    if ($scope.add_template.id) {
      url += '/' + $scope.add_template.id;
    }
    $http.post(url,data);
    
    $scope.load_templates();
    $scope.add_template.active = false;
  };

  $scope.cancel_add_template = function() {
     $scope.add_template.active = false;
  };

  $scope.template_details = function(template) {
    if (template.details ) {
      template.details = false;
    } else {
      template.details = true;
    }
  };

}

})();
