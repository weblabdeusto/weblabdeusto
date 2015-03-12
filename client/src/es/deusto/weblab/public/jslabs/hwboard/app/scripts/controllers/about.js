'use strict';

/**
 * @ngdoc function
 * @name hwboardApp.controller:AboutCtrl
 * @description
 * # AboutCtrl
 * Controller of the hwboardApp
 */
angular.module('hwboardApp')
  .controller('AboutCtrl', function ($scope) {
    $scope.awesomeThings = [
      'HTML5 Boilerplate',
      'AngularJS',
      'Karma'
    ];
  });
