'use strict'

###*
 # @ngdoc directive
 # @name elevatorApp.directive:wlWebcam
 # @description
 # Shows a webcam image and refreshes itself.
###
angular.module('elevatorApp')
  .directive('wlWebcam', ($timeout) ->
    templateUrl: 'views/wlwebcam.html',
    restrict: 'E'
    scope:
      src: '@src'
    link: (scope, element, attrs) ->

      # Listen for image-loaded event, and start
      # a future refresh once caught.
      element.find("img").bind 'load', ->
        scope.refreshSoon()

      # Refresh in some time.
      scope.refreshSoon = ->
        $timeout( ( ->
          scope.doRefresh()
          return
        ), 1000 );

      # Do the actual image refreshing.
      scope.doRefresh = ->
        # Randomly change a number in the rnd parameter so that it always gets downloaded.
        uri = URI(scope.src)
        uri.query(rnd: Math.random() * 100000)
        scope.src = uri.toString()
  )
