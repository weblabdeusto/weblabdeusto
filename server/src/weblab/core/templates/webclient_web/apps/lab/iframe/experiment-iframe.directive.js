
angular
    .module("lab")
    .directive("wlExperimentIframe", wlExperimentIframe);


function wlExperimentIframe($injector) {
    return {
        restrict: "E",
        template: $("#experiment-iframe-template").html(),
        controller: "ExperimentIframeController",
        controllerAs: "experimentIframeController",
        link: wlExperimentIframeLink
    };



    function wlExperimentIframeLink(scope, elem, attrs, ctrl) {

        // -------------
        // Dependencies
        // -------------
        var $log = $injector.get('$log');

        // -------------
        // DOM bindings
        // -------------
        elem.find("iframe").load(handleLoadEvent);

        // -------------
        // Scope bindings & data
        // -------------
        scope.$on("experimentFinished", onExperimentFinished);


        // -------------
        // Implementations
        // -------------

        /**
         * Reloads the iframe when the experimentFinished event is caught.
         */
        function onExperimentFinished() {
            // Reload the frame.
            // This is particularly important at the moment because the WeblabExp compatibility library
            // does not support any kind of reset besides re-instancing. (and it probably shouldn't support it either).
            elem.find("iframe").attr('src', function (i, val) {
                return val;
            });
        } // !onExperimentFinished

        /**
         * Inject the new experiment library and the compatibility layer which automagically is supposed to replace the old one.
         */
        function handleLoadEvent() {
            $log.debug("Injecting scripts");

            // TODO: We should maybe consider removing this and just forcing experiment developers to include the library if they want to support proper resizing.
            InjectScriptIntoFrame("{{ url_for('.static', filename='js/iframeResizer.contentWindow.min.js', _external=True, _scheme=request.scheme) }}"); // Automatic iframe resizing.
        }

    } // !wlExperimentIframeLink



} //! wlExperimentIframe

