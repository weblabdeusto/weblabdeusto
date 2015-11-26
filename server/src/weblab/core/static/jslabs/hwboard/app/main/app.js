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
        'angular.vertilize',
        'ui.bootstrap',
        'ui.bootstrap.modal'
    ])
    .run( function($rootScope) {
        try {
            $rootScope.VIRTUALMODEL = weblab.config.virtualmodel;
        } catch(ex) {
            console.log("VirtualModel blank because 'virtualmodel' client property is not defined");
            $rootScope.VIRTUALMODEL = "";getProperty("virtualmodel");
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
