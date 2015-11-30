
angular
    .module("hwboard")
    .directive("wlStatus", wlStatus);


function wlStatus($injector, $timeout, $log) {
    return {
        restrict: "E",
        templateUrl: "main/status/status.directive.html",
        link: wlStatusLink,
        controller: "StatusController",
        controllerAs: "statusController",
        scope: {
            'status': '=status',
            'message': '=message'
        }
    };

    function wlStatusLink(scope, elem, attrs, ctrl) {
        var flashElem = elem.find(".wl-status-message");

        scope.flash = flash;

        //// For testing, call it every once in a while.
        //$interval(function(){
        //    flash();
        //}, 5000);

        // When the message changes, we flash it to draw attention.
        scope.$watch("message", onMessageChanged);


        // ---------------
        // IMPLEMENTATIONS
        // ---------------

        function onMessageChanged(newVal, oldVal) {
            flash();
        } // !onMessageChanged

        /**
         * Flashes the message with a CSS3 anim, to draw attention.
         */
        function flash() {
            flashElem.removeClass("wl-status-flash");
            $timeout(function(){
                flashElem.addClass("wl-status-flash");
            }, 10);
        } // !flash
    } // !wlStatusLink
} // !wlStatus