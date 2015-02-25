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

        link: function(scope, element, attrs) {
            scope.getClassesForType = getClassesForType;

            function getClassesForType(type) {
                console.debug("Returning classes for type: " + type);

                if(type == 'danger')
                    return "alert alert-danger";
                else
                    return "alert alert-info";
            } // !getClassesForType
        }
    }; // !return
} // !function