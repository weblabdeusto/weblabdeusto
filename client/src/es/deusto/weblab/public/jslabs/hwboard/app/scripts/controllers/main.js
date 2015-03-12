'use strict';

/**
 * @ngdoc function
 * @name hwboardApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the hwboardApp
 */
angular.module('hwboardApp')
  .controller('MainCtrl', function ($scope) {
    $scope.awesomeThings = [
      'HTML5 Boilerplate',
      'AngularJS',
      'Karma'
    ];
  });
