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
    .run(function ($rootScope) {

        // Initialize the translations
        var i18n = {
            "en": {
                "advise.unrecognized.termination": "The file you have uploaded has an unrecognized termination (does not seem to be a VHDL or a BITSTREAM file). Please, ensure that you are uploading the right file. If you are indeed uploading the right one, ensure that your file name matches its type.",
                "advise.no.vhdl": "The file you uploaded does not seem to be a VHDL file at all. Maybe it has not been generated properly.",
                "advise.invalid.vhdl": "The file you uploaded seems to be VHDL, but it does not seem to contain the expected input output declarations. If you generated the file, make sure that you generated it to be compatible with WebLab-Deusto",
                "ok": "Ok",
                "activate": "Activate",
                "deactivate": "Deactivate",
                "clock.freq": "Clock frequency",
                "current.freq": "Current frequency: ",
                "status.undefined": "You need to Reserve the experiment before using it. Please, click on the Reserve button below.",
                "status.not.ready": "You will probably want to upload your logic file before interacting with the board.",
                "uploading": "Uploading...",
                "upload": "Upload",
                "no.file": "No file chosen",
                "choose.file": "Choose file",
                "welcome": "Welcome",
                "welcomeMsg": "Welcome! Before sending your program or using the device, you will need to RESERVE the experiment. You can find the Reserve button at the bottom of the page. Please, prepare your program before reserving so that you have more time. Thank you!"
            },
            "es": {
                "advise.unrecognized.termination": "El archivo que has subido tiene una terminación desconocida (no parece ser ni un archivo VHDL ni un archivo BITSTREAM). Por favor, asegurate de que estás subiendo el archivo correcto. Si el archivo es realmente el correcto, asegúrate de que tu nombre de archivo concuerda con su tipo.",
                "advise.no.vhdl": "El archivo que has subido no parece ser realmente un archivo VHDL. Quizás no ha sido generado de la forma correcta.",
                "advise.invalid.vhdl": "El archivo que has subido parece ser VHDL, pero no parece contener las declaraciones de entradas y salidas que se esperan. Por favor, si has auto-generado el archivo, asegúrate de haberlo generado para ser compatible con WebLab-Deusto.",
                "ok": "Aceptar",
                "activate": "Activar",
                "deactivate": "Desactivar",
                "clock.freq": "Frecuencia de reloj",
                "current.freq": "Frecuencia actual: ",
                "status.undefined": "Necesitas RESERVAR el experimento antes de usarlo. Por favor, haz click en el botón de Reservar que se puede encontrar abajo.",
                "status.not.ready": "Probablemente quieras subir tu lógica al servidor antes de interactuar con la placa.",
                "uploading": "Subiendo...",
                "upload": "Subir",
                "no.file": "No se ha elegido archivo",
                "choose.file": "Elige archivo",
                "welcome": "Bienvenido",
                "welcomeMsg": "Bienvenido! Antes de enviar tu programa o utilizar el dispositivo, necesitarás RESERVAR el experimento. Puedes encontrar el botón RESERVAR al final de la página. Por favor, prepara tu programa antes de reservar, para poder así disponer de más tiempo. Gracias!"
            }
        };

        // Load the right translation depending on the locale
        var currentLanguage = "en";
        try {
            var href = "";
            if (parent === window) {
                href = window.location.href;
            } else {
                href = parent.window.location.href;
            }
            if (href.search("locale=eu") > 0) {
                currentLanguage = "eu";
            } else if (href.search("locale=es") > 0) {
                currentLanguage = "es";
            } else if (href.search("locale=nl") > 0) {
                currentLanguage = "nl";
            }  // Other languages
        } catch (Er) {
            // Error, default to English
        }

        window.TRANSLATIONS = i18n[currentLanguage];

        console.log("onConfigLoad callback set");
        weblab.onConfigLoad(function () {
            console.log("onConfigLoad called");
            // Initialize the VM logic
            try {
                $rootScope.VIRTUALMODEL = weblab.config.virtualmodel;
            } catch (ex) {
                console.log("VirtualModel blank because 'virtualmodel' client property is not defined");
                $rootScope.VIRTUALMODEL = "";
            }
        });

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
