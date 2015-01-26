'use strict'

###*
 # @ngdoc function
 # @name elevatorApp.controller:MainCtrl
 # @description
 # # MainCtrl
 # Controller of the elevatorApp
###
angular.module('elevatorApp')
  .controller 'MainCtrl', ($scope) ->
    $scope.awesomeThings = [
      'HTML5 Boilerplate'
      'AngularJS'
      'Karma'
    ]
