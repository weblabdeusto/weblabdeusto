angular
    .module("lab")
    .directive("wlReserveStatus", wlReserveStatus);


function wlReserveStatus() {
    return {
        restrict: "E",

        scope: {
            message: "=",
            translationData: "=",
            type: "="
        },

        templateUrl: RESERVE_STATUS_TEMPLATE_URL,

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
