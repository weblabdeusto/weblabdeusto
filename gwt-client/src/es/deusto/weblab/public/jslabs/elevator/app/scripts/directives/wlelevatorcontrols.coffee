'use strict'

###*
 # @ngdoc directive
 # @name elevatorApp.directive:wlelevatorcontrols
 # @description
 # Virtual controls for the control box that is within the elevator's cabin.
###
angular.module('elevatorApp')
  .directive('wlElevatorControls', ->
    templateUrl: 'views/wlelevatorcontrols.html',
    restrict: 'E'
    link: (scope, element, attrs) ->

  )
