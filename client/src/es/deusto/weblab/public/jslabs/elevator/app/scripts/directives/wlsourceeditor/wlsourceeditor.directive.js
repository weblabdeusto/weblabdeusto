
angular
    .module("elevatorApp")
    .directive("wlSourceEditor", wlSourceEditorDirective);


function wlSourceEditorDirective()
{
    return {
        restrict: "E",
        templateUrl: "views/wlsourceeditor.directive.html",
        controller: "SourceEditorController",
        controllerAs: "sourceEditorController",
        link: wlSourceEditorLink,
        scope: {}
    };

    ///////////
    // Implementations
    ///////////

    function wlSourceEditorLink(scope, elem, attrs)
    {

    } // !wlSourceEditorLink

} // !wlSourceEditorDirective