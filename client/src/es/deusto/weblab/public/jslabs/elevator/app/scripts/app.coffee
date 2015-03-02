'use strict'

###*
 # @ngdoc overview
 # @name elevatorApp
 # @description
 # # elevatorApp
 #
 # Main module of the application.
###
angular
  .module('elevatorApp', [
#    'ngAnimate',              # Somewhat crazily, if we enable ng-animate ng-show starts applying some kind of animation on its own, which is not desirable.
    'ngResource',
    'ngCookies',
    'ngRoute',
    'ngSanitize',
    'ngTouch',
    'angularFileUpload',
    'ui.bootstrap'
  ])
  .config ($routeProvider) ->
    $routeProvider
      .when '/',
        templateUrl: 'views/main.html'
        controller: 'MainCtrl'
      .when '/about',
        templateUrl: 'views/about.html'
        controller: 'AboutCtrl'
      .otherwise
        redirectTo: '/'

