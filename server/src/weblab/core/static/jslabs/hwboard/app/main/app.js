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

        // Initialize the translations
        var i18n = {
            "en": {
                "uploading": "Uploading...",
                "upload": "Upload",
                "no.file": "No file chosen",
                "choose.file": "Choose file",
                "welcome": "Welcome",
                "welcomeMsg": "Welcome! Before sending your program or using the device, you will need to RESERVE the experiment. You can find the Reserve button at the bottom of the page. Please, prepare your program before reserving so that you have more time. Thank you!"
            },
            "es": {
                "uploading": "Subiendo...",
                "upload": "Subir",
                "no.file": "No se ha elegido archivo",
                "choose.file": "Elige archivo",
                "welcome": "Bienvenido",
                "welcomeMsg": "Bienvenido! Antes de enviar tu programa o utilizar el dispositivo, necesitarás RESERVAR el experimento. Puedes encontrar el botón RESERVAR al final de la página. Por favor, prepara tu programa antes de reservar, para poder así disponer de más tiempo. Gracias!"
            }
        };

        window.TRANSLATIONS = i18n["en"];

        // Initialize the VM logic
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
