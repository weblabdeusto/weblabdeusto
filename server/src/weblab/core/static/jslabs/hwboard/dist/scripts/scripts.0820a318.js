"use strict";function MainController(a,b,c,d,e,f,g){function h(){a.modals.reserveModal.dismiss()}function i(a,c){var d=!0;if(c.canClose||(d="static"),void 0!==b.BOOLEWEB_EXTERNAL)var f=e.open({animation:!0,templateUrl:"reserve_modal.controller.html",controller:"ReserveModalController",size:a,resolve:{params:c},backdrop:d});else var f=e.open({animation:!0,templateUrl:"modal.controller.html",controller:"ModalController",size:a,resolve:{params:c},backdrop:d});return f}function j(){function b(b){var c=f.result,e=$("#file")[0].files[0].name,h=c,i=g.evalFile(h,e),j=e.split(".").pop();return"ok"!=i.result?(alert(i.message),void(a.uploading=!1)):(d.debug("File has been read client-side."),void weblab.sendFile(c,j).done(k).fail(l))}d.debug("Trying to read file"),a.uploading=!0;try{var c=$("#file")[0],e=c.files[0],f=new FileReader;window.gFileReader=f,f.onload=b,f.readAsBinaryString(e)}catch(h){a.uploading=!1;var i="There was an error while trying to read your file. Please, ensure that it is valid.";d.error(i),d.error(h),alert(i)}}function k(b){d.debug("FILE SENT: "+b),a.uploading=!1}function l(b){d.debug("FILE SENDING ERROR: "+b),a.uploading=!1,alert("The server reported an error with your file. Please, ensure that you sent a valid file and try again.")}function m(c){if(d.debug("Status update: "+c),c!=a.status){if("ready"==c){var e=sprintf("VIRTUALWORLD_MODEL %s",b.VIRTUALMODEL);weblab.sendCommand(e).done(q).fail(r)}a.status=c,a.$apply()}}function n(a){d.debug("Led update: "+a)}function o(b){d.debug("Virtualmodel update: "+b),a.$broadcast("virtualmodel-status-report",b)}function p(c,d){a.modals.reserveModal.close("Reserve done"),t(c),statusUpdater.start(),ledUpdater.start(),virtualmodelUpdater.start(),a.webcamUrl=d.webcam;var e=sprintf("VIRTUALWORLD_MODEL %s",b.VIRTUALMODEL);weblab.sendCommand(e).done(q).fail(r)}function q(a){d.debug("VirtualModel set: "+a)}function r(a){d.debug("VirtualModel set failure: "+a)}function s(){statusUpdater.stop(),a.time=0}function t(b){d.debug("TIME IS: "+b),a.time=b}window.$rootScope=b,statusUpdater=c.get("statusUpdater"),statusUpdater.setOnStatusUpdate(m),ledUpdater=c.get("ledUpdater"),ledUpdater.setOnLedUpdate(n),virtualmodelUpdater=c.get("virtualmodelUpdater"),virtualmodelUpdater.setOnVirtualmodelUpdate(o),d.debug("HW board experiment main controller"),weblab.onStart(p),weblab.onFinish(s),a.time=0,a.uploading=!1,a.modals={},a.webcamUrl="images/video.png",a.doFileUpload=j,a.openModal=i,window.debug=h,void 0!==b.BOOLEWEB_EXTERNAL?a.modals.reserveModal=i(1e3,{title:f("translate")("welcome"),message:f("translate")("welcomeMsg"),openBooleMessage:f("translate")("openBooleMessage"),startCreatingMessage:f("translate")("startCreatingMessage"),booleLink:b.BOOLEWEB_EXTERNAL,canClose:!1}):a.modals.reserveModal=i(1e3,{title:f("translate")("welcome"),message:f("translate")("welcomeMsg"),canClose:!1})}function WebcamController(a,b){function c(){f(function(){d()},100)}function d(){var b=URI(a.src);b.query({rnd:1e5*Math.random()}),a.src=b.toString()}var e=this,f=b.get("$timeout");e.programRefresh=c}function wlWebcam(){function a(a,b,c,d){function e(){d.programRefresh()}b.find("img").bind("load error",e)}return{restrict:"E",scope:{src:"@src"},templateUrl:"main/webcam/webcam.directive.html",controller:"WebcamController",controllerAs:"webcamController",link:a}}function StatusController(a,b,c){function d(){return void 0==a.status?c("translate")("status.undefined"):"not_ready"==a.status?c("translate")("status.not.ready"):"[STATUS: "+a.status+"] "+a.message}a.getDisplay=d}function wlStatus(a,b,c){function d(a,c,d,e){function f(a,b){g()}function g(){h.removeClass("wl-status-flash"),b(function(){h.addClass("wl-status-flash")},10)}var h=c.find(".wl-status-message");a.flash=g,a.$watch("message",f)}return{restrict:"E",templateUrl:"main/status/status.directive.html",link:d,controller:"StatusController",controllerAs:"statusController",scope:{status:"=status",message:"=message"}}}function wlButton(a){function b(a,b,c,d){}return{restrict:"E",templateUrl:"main/button/button.directive.html",link:b,controller:"ButtonController",controllerAs:"buttonController",scope:{ident:"@ident",caption:"@caption",overlay:"@overlay",delay:"=delay"}}}function ButtonController(a,b,c,d){function e(){a.ongoingCommand||(a.ongoingCommand=!0,c.debug("Button "+a.ident+" pressed."),a.isPressed=!0,weblab.sendCommand("SetPulse on "+a.ident).done(f).fail(g))}function f(b){c.debug("[Button] SetPulse ON"),a.isOn=!0,a.isPressed=!1;var e=a.delay;void 0==e&&(c.error("[BUTTON]: Please define a button delay. Meanwhile setting it to 1000 ms"),e=1e3),d(function(){weblab.sendCommand("SetPulse off "+a.ident).done(function(b){c.debug("[Button] SetPulse OFF"),a.isOn=!1,a.isPressed=!1,a.ongoingCommand=!1,a.$apply()}).fail(function(b){c.error("SetPulse failed (while sending button pulse)"),c.error(b),a.ongoingCommand=!1,a.isPressed=!1,a.$apply()})},e),a.$apply()}function g(b){c.error("SetPulse failed"),a.ongoingCommand=!1,a.isPressed=!1,a.$apply()}a.button={},a.isOn=!1,a.isPressed=!1,a.ongoingCommand=!1,a.press=e}function wlSwitch(a){function b(a,b,c,d){}return{restrict:"E",templateUrl:"main/switch/switch.directive.html",link:b,controller:"SwitchController",controllerAs:"switchController",scope:{ident:"@ident",caption:"@caption",overlay:"@overlay"}}}function SwitchController(a,b,c,d){function e(){if(!a.ongoingCommand){a.ongoingCommand=!0,c.debug("Switch "+a.ident+" pressed."),a.isPressed=!0;var b=a.isOn?"off":"on";weblab.sendCommand("ChangeSwitch "+b+" "+a.ident).done(f).fail(g)}}function f(b){c.debug("ChangeSwitch succeeded"),a.isOn=!a.isOn,a.isPressed=!1,a.ongoingCommand=!1,a.$apply()}function g(b){c.error("SetPulse failed"),a.ongoingCommand=!1,a.isPressed=!1,a.$apply()}a.button={},a.isOn=!1,a.isPressed=!1,a.ongoingCommand=!1,a.press=e}function statusUpdater(a,b,c){function d(a){l=a}function e(){k=c(g,j)}function f(){c.cancel(k)}function g(){weblab.sendCommand("STATE").done(h).fail(i)}function h(a){if(b.debug("SUCCESS: STATUS: "+a),void 0!=l){var d=a.substring(6);l(d)}k=c(g,j)}function i(a){b.error("ERROR: sendCommand (status)"),b.error(a),k=c(g,j)}var j=2e3,k=void 0,l=void 0;return{start:e,stop:f,setOnStatusUpdate:d}}function virtualmodelUpdater(a,b,c){function d(a){l=a}function e(){k=c(g,j)}function f(){c.cancel(k)}function g(){weblab.sendCommand("VIRTUALWORLD_STATE").done(h).fail(i)}function h(a){if(b.debug("SUCCESS: VM STATUS: "+a),void 0!=l){var d=JSON.parse(a);l(d)}k=c(g,j)}function i(a){b.error("ERROR: sendCommand (status)"),b.error(a),k=c(g,j)}var j=2e3,k=void 0,l=void 0;return{start:e,stop:f,setOnVirtualmodelUpdate:d}}function ledUpdater(a,b,c){function d(a){l=a}function e(){k=c(g,j)}function f(){c.cancel(k)}function g(){weblab.sendCommand("READ_LEDS").done(h).fail(i)}function h(a){if(b.debug("SUCCESS: READ_LEDS: "+a),void 0!=l){var d=a;l(d)}k=c(g,j)}function i(a){b.error("ERROR: sendCommand (read_leds)"),b.error(a),k=c(g,j)}var j=2e3,k=void 0,l=void 0;return{start:e,stop:f,setOnLedUpdate:d}}function TimerController(a,b,c){function d(b,c){return 0>b?void(a.time=0):(0==c&&h.startDecreasing(),void(0==b&&h.stopDecreasing()))}function e(){a.time>0&&(a.time-=1)}function f(){c.cancel(h._interval),h._interval=c(e,1e3)}function g(){c.cancel(h._interval)}var h=this;a.$watch("time",d),h.startDecreasing=f,h.stopDecreasing=g}function wlTimer(){return{restrict:"E",templateUrl:"main/timer/timer.directive.html",controller:"TimerController",controllerAs:"timerController",link:wlTimerLink,scope:{time:"=time"}}}function wlTimerLink(a,b,c,d){}function ClockControlController(a,b){function c(){return a.activated}function d(){b.debug("Activating clock"),a.runningCommand=!0,weblab.sendCommand("ClockActivation on "+a.frequency).done(function(c){b.debug("Clock activated"),a.activated=!0,a.runningCommand=!1,a.$apply()}).fail(function(b){a.activated=!1,a.runningCommand=!1,a.$apply()})}function e(){b.debug("Deactivating clock"),a.runningCommand=!0,weblab.sendCommand("ClockActivation off ").done(function(c){b.debug("Clock deactivated"),a.activated=!1,a.runningCommand=!1,a.$apply()}).fail(function(b){a.activated=!1,a.runningCommand=!1,a.$apply()}),a.activated=!1}a.activated=!1,a.runningCommand=!1,a.frequency=1e3,a.isActivated=c,a.activate=d,a.deactivate=e}function wlClockControl(){function a(a,b,c,d){}return{restrict:"E",controller:"ClockControlController",controllerAs:"clockControlController",templateUrl:"main/clock/clock-control.directive.html",link:a,scope:{}}}function wlVirtualModel(){function a(a,b,c){function d(){return $(e)}var e=b.find("iframe");a.getIframeElement=d}return{restrict:"E",templateUrl:"main/virtual-model/virtual-model.directive.html",controller:"VirtualModelController",controllerAs:"virtualModelController",link:a,scope:{}}}function VirtualModelController(a){function b(b,c){var d=a.getIframeElement(),e=d[0];e.contentWindow.postMessage({message:"virtualmodel-status",data:c},"*")}a.$on("virtualmodel-status-report",b)}function wlBooleWeb(){function a(a,b,c){function d(){return $(e)}var e=b.find("iframe");a.getIframeElement=d}return{restrict:"E",templateUrl:"main/boole-web/boole-web.directive.html",controller:"BooleWebController",controllerAs:"booleWebController",link:a,scope:{}}}function BooleWebController(a,b,c){a.booleWebURL=b.trustAsResourceUrl(c.BOOLEWEB)}function ModalController(a,b,c){a.params=c,a.ok=function(){b.close()},a.cancel=function(){b.dismiss("cancel")}}function ReserveModalController(a,b,c){a.params=c,a.ok=function(){b.close()},a.cancel=function(){b.dismiss("cancel")}}function AdviseFactory(a,b){function c(a,c){var d=c.split(".").pop();if("vhd"!=d&&"bit"!=d)return{result:"error",message:b("translate")("advise.unrecognized.termination")};if("vhd"==d){var e=a.search(/architecture/);if(-1==e)return{result:"error",message:b("translate")("advise.no.vhdl")};if(e=a.search(/inout/),-1==e)return{result:"error",message:b("translate")("advise.invalid.vhdl")}}return{result:"ok"}}return{evalFile:c}}function wlTranslateMe(a){return{restrict:"A",transclude:!1,link:function(b,c,d){var e=c.text(),f=a("translate")(e);c.contents().filter(function(){return 3==this.nodeType}).replaceWith(f)}}}function translateFilter(){function a(a){var b=a.trim(),c=TRANSLATIONS[b];return void 0!=c?a.replace(b,c):a}return a}angular.module("hwboard",["ngAnimate","ngCookies","ngResource","ngRoute","ngSanitize","ngTouch","ui.slider","angular.vertilize","ui.bootstrap","ui.bootstrap.modal"]).run(["$rootScope",function(a){var b={en:{"advise.unrecognized.termination":"The file you have uploaded has an unrecognized termination (does not seem to be a VHDL or a BITSTREAM file). Please, ensure that you are uploading the right file. If you are indeed uploading the right one, ensure that your file name matches its type.","advise.no.vhdl":"The file you uploaded does not seem to be a VHDL file at all. Maybe it has not been generated properly.","advise.invalid.vhdl":"The file you uploaded seems to be VHDL, but it does not seem to contain the expected input output declarations. If you generated the file, make sure that you generated it to be compatible with WebLab-Deusto",ok:"Ok",activate:"Activate",deactivate:"Deactivate","clock.freq":"Clock frequency","current.freq":"Current frequency: ","status.undefined":"You need to Reserve the experiment before using it. Please, click on the Reserve button below.","status.not.ready":"You will probably want to upload your logic file before interacting with the board.",uploading:"Uploading...",upload:"Upload","no.file":"No file chosen","choose.file":"Choose file",welcome:"Welcome",welcomeMsg:"Welcome! Before sending your program or using the device, you will need to RESERVE the experiment. You can find the Reserve button at the bottom of the page. Please, prepare your program before reserving so that you have more time. Thank you!",openBooleMessage:"Open Boole-Web",startCreatingMessage:"To start creating your digital system, you can:"},es:{"advise.unrecognized.termination":"El archivo que has subido tiene una terminación desconocida (no parece ser ni un archivo VHDL ni un archivo BITSTREAM). Por favor, asegurate de que estás subiendo el archivo correcto. Si el archivo es realmente el correcto, asegúrate de que tu nombre de archivo concuerda con su tipo.","advise.no.vhdl":"El archivo que has subido no parece ser realmente un archivo VHDL. Quizás no ha sido generado de la forma correcta.","advise.invalid.vhdl":"El archivo que has subido parece ser VHDL, pero no parece contener las declaraciones de entradas y salidas que se esperan. Por favor, si has auto-generado el archivo, asegúrate de haberlo generado para ser compatible con WebLab-Deusto.",ok:"Aceptar",activate:"Activar",deactivate:"Desactivar","clock.freq":"Frecuencia de reloj","current.freq":"Frecuencia actual: ","status.undefined":"Necesitas RESERVAR el experimento antes de usarlo. Por favor, haz click en el botón de Reservar que se puede encontrar abajo.","status.not.ready":"Probablemente quieras subir tu lógica al servidor antes de interactuar con la placa.",uploading:"Subiendo...",upload:"Subir","no.file":"No se ha elegido archivo","choose.file":"Elige archivo",welcome:"Bienvenido",welcomeMsg:"Bienvenido! Antes de enviar tu programa o utilizar el dispositivo, necesitarás RESERVAR el experimento. Puedes encontrar el botón RESERVAR al final de la página. Por favor, prepara tu programa antes de reservar, para poder así disponer de más tiempo. Gracias!",openBooleMessage:"Abrir Boole-Web",startCreatingMessage:"Para empezar a crear tu sistema digital, puedes:"}},c="en";try{var d="";d=parent===window?window.location.href:parent.window.location.href,d.search("locale=eu")>0?c="eu":d.search("locale=es")>0?c="es":d.search("locale=nl")>0&&(c="nl")}catch(e){}window.TRANSLATIONS=b[c],console.log("onConfigLoad callback set"),weblab.onConfigLoad(function(){console.log("onConfigLoad called");try{a.VIRTUALMODEL=weblab.config.virtualmodel}catch(b){console.log("VirtualModel blank because 'virtualmodel' client property is not defined"),a.VIRTUALMODEL=""}try{a.BOOLEWEB=weblab.config.booleweb}catch(b){console.log("BooleWeb blank because 'booleweb' client property is not defined"),a.BOOLEWEB=""}try{a.BOOLEWEB_EXTERNAL=weblab.config.boolewebExternal}catch(b){console.log("BooleWebExternal blank because 'boolewebExternal' client property is not defined"),a.BOOLEWEB_EXTERNAL=""}})}]).config(["$routeProvider",function(a){a.when("/",{templateUrl:"main/main.html",controller:"MainController"}).when("/about",{templateUrl:"main/about.html",controller:"AboutController"}).otherwise({redirectTo:"/"})}]),angular.module("hwboard").controller("MainController",MainController),MainController.$inject=["$scope","$rootScope","$injector","$log","$uibModal","$filter","advise"],angular.module("hwboard").controller("AboutController",["$scope",function(a){a.awesomeThings=["HTML5 Boilerplate","AngularJS","Karma"]}]),angular.module("hwboard").controller("WebcamController",WebcamController),WebcamController.$inject=["$scope","$injector"],angular.module("hwboard").directive("wlWebcam",wlWebcam),angular.module("hwboard").controller("StatusController",StatusController),StatusController.$inject=["$scope","$injector","$filter"],angular.module("hwboard").directive("wlStatus",wlStatus),wlStatus.$inject=["$injector","$timeout","$log"],angular.module("hwboard").directive("wlButton",wlButton),wlButton.$inject=["$injector"],angular.module("hwboard").controller("ButtonController",ButtonController),ButtonController.$inject=["$scope","$injector","$log","$timeout"],angular.module("hwboard").directive("wlSwitch",wlSwitch),wlSwitch.$inject=["$injector"],angular.module("hwboard").controller("SwitchController",SwitchController),SwitchController.$inject=["$scope","$injector","$log","$timeout"],angular.module("hwboard").factory("statusUpdater",statusUpdater),statusUpdater.$inject=["$injector","$log","$timeout"],angular.module("hwboard").factory("virtualmodelUpdater",virtualmodelUpdater),virtualmodelUpdater.$inject=["$injector","$log","$timeout"],angular.module("hwboard").factory("ledUpdater",ledUpdater),ledUpdater.$inject=["$injector","$log","$timeout"],angular.module("hwboard").controller("TimerController",TimerController),TimerController.$inject=["$scope","$injector","$interval"],angular.module("hwboard").directive("wlTimer",wlTimer),angular.module("hwboard").filter("secondsToDateTime",[function(){return function(a){return new Date(1970,0,1).setSeconds(a)}}]),angular.module("hwboard").controller("ClockControlController",ClockControlController),ClockControlController.$inject=["$scope","$log"],angular.module("hwboard").directive("wlClockControl",wlClockControl),angular.module("hwboard").directive("wlVirtualModel",wlVirtualModel),angular.module("hwboard").controller("VirtualModelController",VirtualModelController),VirtualModelController.$inject=["$scope"],angular.module("hwboard").directive("wlBooleWeb",wlBooleWeb),angular.module("hwboard").controller("BooleWebController",BooleWebController),BooleWebController.$inject=["$scope","$sce","$rootScope"],angular.module("hwboard").controller("ModalController",ModalController),ModalController.$inject=["$scope","$uibModalInstance","params"],angular.module("hwboard").controller("ReserveModalController",ReserveModalController),ReserveModalController.$inject=["$scope","$uibModalInstance","params"],angular.module("hwboard").factory("advise",AdviseFactory),AdviseFactory.$inject=["$log","$filter"],angular.module("hwboard").directive("wlTranslateMe",wlTranslateMe),wlTranslateMe.$inject=["$filter"],angular.module("hwboard").filter("translate",translateFilter);
//# sourceMappingURL=scripts.0820a318.js.map