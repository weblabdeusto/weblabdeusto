
angular
    .module("hwboard")
    .controller("WebcamController", WebcamController);


function WebcamController($scope, $injector) {

    ///
    /// Self-reference
    ///
    var controller = this;

    ///
    /// Dependencies
    ///
    var $timeout = $injector.get('$timeout');

    ///
    /// Controller methods
    ///

    // To be invoked from the link function or similar. It will refresh the webcam (in a short time after being called).
    controller.programRefresh = programRefresh;



    ///
    /// Implementations
    ///

    function programRefresh() {
        $timeout(function () {
            refresh();
        }, 100)
    }

    function refresh() {
        // To prevent cache-related issues we add a random parameter to the URL.
        // Randomly change a number in the rnd parameter so that it always gets downloaded.
        var uri = URI($scope.src);
        uri.query({rnd: Math.random() * 100000});
        $scope.src = uri.toString();
    }

} // !WebcamController
