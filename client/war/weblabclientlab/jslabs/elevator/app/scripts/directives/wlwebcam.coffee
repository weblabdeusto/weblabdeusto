'use strict'

###*
 # @ngdoc directive
 # @name elevatorApp.directive:wlWebcam
 # @description
 # # wlWebcam
###
angular.module('elevatorApp')
  .directive('wlWebcam', ($timeout) ->
    templateUrl: 'views/wlwebcam.html',
    restrict: 'E'
    scope:
      src: '@src'
    link: (scope, element, attrs) ->

      scope.startRefreshing = ->
        $timeout( ( ->
          console.log "Refreshing"

          # Append a random number so that it is unique.
          scope.startRefreshing()
          return
        ), 1000 );


      # Really do start refreshing.
      scope.startRefreshing();
  )
