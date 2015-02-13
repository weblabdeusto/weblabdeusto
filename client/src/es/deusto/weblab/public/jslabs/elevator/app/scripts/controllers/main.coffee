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

    # Create basic parameters for the whole experiment
    $scope.experiment = {}
    $scope.experiment.status = 'ready'


    $scope.shouldShowStatus = ->
      return $scope.experiment.status == 'programming'
