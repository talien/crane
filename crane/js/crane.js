var crane = angular.module('crane', ['ngRoute','ui.bootstrap'], function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});

crane.config(function($routeProvider){
  $routeProvider.when("/hosts",
    {
      templateUrl: "/frontend/hosts.jade",
      controller: "HostControl"
    }).when("/containers",
    {
      templateUrl: "/frontend/containers.jade",
      controller: "ContainerControl"
    }).when("/templates",
    {
      templateUrl: "/frontend/templates.jade",
      controller: "TemplatesControl"
    }).when("/registry",
    {
      templateUrl: "/frontend/registry.jade",
      controller: "RegistryControl"
    });
});
