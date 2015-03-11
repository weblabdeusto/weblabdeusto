
angular
    .module("lab")
    .directive("wlExperimentIframe", wlExperimentIframe);


function wlExperimentIframe() {
    return {
        restrict: "E",
        template: $("#experiment-iframe-template").html(),
        link: function(scope, elem, attrs, ctrl) {
            {# Inject the new experiment library and the compatibility layer which automagically is supposed to replace the old one #}
            $("#exp-frame").load(function () {
                console.debug("Injecting scripts");

                // TODO: We should maybe consider removing this and just forcing experiment developers to include the library if they want to support proper resizing.
                InjectScriptIntoFrame("{{ url_for('.static', filename='js/iframeResizer.contentWindow.min.js', _external=True, _scheme=request.scheme) }}"); // Automatic iframe resizing.
            });
        }
    }

} //! wlExperimentIframe

