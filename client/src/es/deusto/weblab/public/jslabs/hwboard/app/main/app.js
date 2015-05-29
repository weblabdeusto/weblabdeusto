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
        'ui.slider'
    ])
    .constant(
        "VIRTUALMODEL", "watertank"
    )
    .run( function($rootScope, VIRTUALMODEL) {
        $rootScope.VIRTUALMODEL = VIRTUALMODEL;
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
