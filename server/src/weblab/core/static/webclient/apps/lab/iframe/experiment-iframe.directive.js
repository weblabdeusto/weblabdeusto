
angular
    .module("lab")
    .directive("wlExperimentIframe", wlExperimentIframe);


function wlExperimentIframe($injector) {
    return {
        restrict: "E",
        scope: {
            laburl: "=",
            experiment: "=",
            iframeurl: "=",
            language: "="
        },
        templateUrl: EXPERIMENT_IFRAME_TEMPLATE_URL,
        controller: "ExperimentIframeController",
        controllerAs: "experimentIframeController",
        link: wlExperimentIframeLink
    };



    function wlExperimentIframeLink(scope, elem, attrs, ctrl) {
        // -------------
        // Dependencies
        // -------------
        var $log = $injector.get('$log');
        var resizer = $injector.get('Resizer');

        var iframe = elem.find("iframe");

        // -------------
        // DOM bindings & initialization.
        // -------------
        iframe.load(handleLoadEvent);
        resizer.loadFrameResizer(iframe);
        window.addEventListener('message', _processMessages, false);

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
            iframe.attr('src', function (i, val) {
                return val;
            });
        } // !onExperimentFinished

        /**
         * Inject the new experiment library and the compatibility layer which automagically is supposed to replace the old one.
         */
        function handleLoadEvent() {
            $log.debug("Injecting scripts");

            // TODO: We should maybe consider removing this and just forcing experiment developers to include the library if they want to support proper resizing.
            resizer.injectScriptIntoFrame(iframe, IFRAME_RESIZER_URL); // Automatic iframe resizing.


        }

        function _processMessages(e) {
            if (new String(e.data).indexOf("weblabdeusto::") == 0) {
                if (new String(e.data) == "weblabdeusto::experimentLoaded") {
                    resizer.forceFrameResizer(iframe);
                    setTimeout( function() {
                        scope.$emit("experimentLoaded");
                    }, 2000);
                }
            }
        }

    } // !wlExperimentIframeLink



} //! wlExperimentIframe

