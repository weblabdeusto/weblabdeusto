'use strict'

###*
 # @ngdoc directive
 # @name elevatorApp.directive:wlbutton
 # @description
 # # TODO: Not yet implemented.
###
angular.module('elevatorApp')
  .directive('wlbutton', ->
    templateUrl: 'views/wlbutton.html',
    scope:
      'ident': '@ident'
    restrict: 'E'
    link: (scope, element, attrs) ->
      return
  )
