'use strict'

###*
 # @ngdoc function
 # @name elevatorApp.controller:AboutCtrl
 # @description
 # # AboutCtrl
 # Controller of the elevatorApp
###
angular.module('elevatorApp')
  .controller 'AboutCtrl', ($scope) ->
    $scope.awesomeThings = [
      'HTML5 Boilerplate'
      'AngularJS'
      'Karma'
    ]
