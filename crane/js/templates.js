var crane = angular.module('crane');

crane.directive('craneAutoComplete', function($timeout) {
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
                var res = new Array()
                var opening = request.term.lastIndexOf("%(");
                var closing = request.term.lastIndexOf(")%");
                for (var i=0; i<scope[iAttrs.uiItems].length; i++) {
                    if (opening > closing)
                    {
                      prefix = request.term.substring(0,opening+2);
                      var leftover = request.term.substring(opening+2);
                      var patt = new RegExp("([0-9a-zA-Z_])*");
                      var term = patt.exec(leftover)[0];
                      suffix = request.term.substring(opening+2+term.length);
                      if (scope[iAttrs.uiItems][i].name.indexOf(term) == 0) {
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
                /*$timeout(function() {
                  iElement.trigger('input');
                }, 0);*/
                iElement.trigger('input');
                return false;
            }
        });
    };
});

crane.controller('TemplatesControl', function ($scope, $http) {
  $scope.parameters = [];

  $scope.load_templates = function() {
     $http.get("/template").success(function(data) {
     $scope.templates = data.result;
   });
  };

  $scope.load_templates();

  $scope.start_add_template = function() {
     $scope.add_template = { 'active':true, 'deploy': {} };
  };

  $scope.add_parameter = function() {
     $scope.parameters.push({});
  };

  $scope.delete_template = function(template) {
     $http.delete("/template/" + String(template.id));
     $scope.load_templates();
  };

  $scope.save_template = function() {
     data = { 'name' : $scope.add_template.name, 'template': { 'parameters': $scope.parameters, 'deploy': $scope.add_template.deploy } };
     $http.post("/template",data);
     $scope.load_templates();
     $scope.add_template.active = false;
  };

});
