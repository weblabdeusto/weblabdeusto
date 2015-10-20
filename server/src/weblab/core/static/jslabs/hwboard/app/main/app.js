'use strict';

/**
 * @ngdoc overview
 * @name hwboardApp
 * @description
 *
 * Main module of the application.
 */
angular
    .module('hwboard', [
        'ngAnimate',
        'ngCookies',
        'ngResource',
        'ngRoute',
        'ngSanitize',
        'ngTouch',
        'ui.slider',
        'angular.vertilize'
    ])
    .run( function($rootScope) {
        try {
            $rootScope.VIRTUALMODEL = "watertank"; // hard-coded for now. getProperty is currently not supported.
            // $rootScope.VIRTUALMODEL = weblab.getProperty("virtualmodel");
        } catch(ex) {
            console.log("VirtualModel blank because 'virtualmodel' client property is not defined");
            $rootScope.VIRTUALMODEL = "";
        }
    })
    .config(function ($routeProvider) {
        $routeProvider
            .when('/', {
                templateUrl: 'main/main.html',
                controller: 'MainController'
            })
            .when('/about', {
                templateUrl: 'main/about.html',
                controller: 'AboutController'
            })
            .otherwise({
                redirectTo: '/'
            });
    });
