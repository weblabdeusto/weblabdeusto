(function(){"use strict";angular.module("dashboardappApp",["ngAnimate","ngCookies","ngMessages","ngResource","ngRoute","ngSanitize","ngTouch"]).config(["$routeProvider",function(a){return a.when("/",{templateUrl:"views/main.html",controller:"MainCtrl"}).when("/about",{templateUrl:"views/about.html",controller:"AboutCtrl"}).otherwise({redirectTo:"/"})}])}).call(this),function(){"use strict";angular.module("dashboardappApp").controller("MainCtrl",["$scope","$resource",function(a,b){var c;return a.awesomeThings=["HTML5 Boilerplate","AngularJS","Karma"],c=b("/status"),a.components_raw=c.get(function(b){return console.log("[/status]: Components obtained."),a.components=b.toJSON()},function(){return console.error("[/status]: Error obtaining components: Trying test URL."),c=b("http://localhost:5000/status"),a.components_raw=c.get(function(b){return a.components=b.toJSON(),console.log("[/status]: Components obtained (from localhost server)")},function(){return console.error("[/status]: Error obtaining components from localhost.")})})}])}.call(this),function(){"use strict";angular.module("dashboardappApp").controller("AboutCtrl",["$scope",function(a){return a.awesomeThings=["HTML5 Boilerplate","AngularJS","Karma"]}])}.call(this),function(){"use strict";angular.module("dashboardappApp").directive("myComponent",["$rootScope",function(){return{restrict:"E",scope:{componentid:"=componentid",component:"=component"},templateUrl:"views/my-component.html",link:function(){}}}])}.call(this);