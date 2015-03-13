angular
    .module("lab")
    .directive("wlReserveStatus", wlReserveStatus);


function wlReserveStatus() {
    return {
        restrict: "E",

        scope: {
            message: "=message",
            type: "=type"
        },

        template: $("#reserve-status-template").html(),

        link: wlReserveStatusLink

    }; // !return


    // ---------
    // Implementations
    // ---------

    function wlReserveStatusLink(scope, elem, attrs) {

        // ------
        // Scope & related
        // ------

        scope.getClassesForType = getClassesForType;

        // ------
        // Implementations
        // ------

        function getClassesForType(type) {
            if(type == 'danger')
                return "alert alert-danger";
            else
                return "alert alert-info";
        }

    } // !wlReserveStatusLink

} // !function