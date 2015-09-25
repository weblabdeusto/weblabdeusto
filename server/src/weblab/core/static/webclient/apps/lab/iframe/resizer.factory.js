
angular
    .module("lab")
    .factory("Resizer", ResizerFactory);


function ResizerFactory() {

    return {
        loadFrameResizer: loadFrameResizer,
        injectScriptIntoFrame: injectScriptIntoFrame,
        forceFrameResizer: forceFrameResizer
    };

    var mHasBeenCalled = false;


    // ----------
    // Implementations
    // ----------

    /**
     * Binds to the iframe and tries calling the resizer initializer function until it manages
     * to do so.
     */
    function loadFrameResizer(iframeElement) {
        iframeElement.on("load", function (ev) {

            // We cannot call the iFrameResize function straightaway, because, the way we handle this as of now, is to load
            // the internal resize script within the iframe asynchronously. This means that we need to make sure it has
            // finished loading.
            // TODO: Consider whether we should assume that the experiment scripts include the script by themselves.
            var timesTried = 0;
            var initResizeInterval = setInterval(function () {
                if(iframeElement !== undefined) {
                    if (!mHasBeenCalled) {
                        mHasBeenCalled = true;
                        iframeElement.iFrameResize({
                            enablePublicMethods: true,
                            checkOrigin: false
                        }, "#exp-frame");
                    }
                    clearInterval(initResizeInterval);
                } else {
                    timesTried++;
                    if(timesTried > 100) {
                        clearInterval(initResizeInterval);
                        console.error("[RESIZE]: We failed to resize the experiment's iframe. Maybe the experiment's iframe resizer script could not be injected properly.");
                    }
                }
            }, 50);
        });
    } // !loadFrameResizer()

    function forceFrameResizer(iframeElement) {
        if (!mHasBeenCalled) {
            mHasBeenCalled = true;
            iframeElement.iFrameResize({
                enablePublicMethods: true,
                checkOrigin: false
            }, "#exp-frame");
        }
    }

    /**
     * Injects the specified script into the specified iframe.
     * @iframe iframe: Iframe element into which to inject.
     * @param url: URL to the script ot inject.
     * @constructor
     */
    function injectScriptIntoFrame(iframe, url) {
        myIframe = iframe[0];
        var script = myIframe.contentWindow.document.createElement("script");
        script.async = false;
        script.defer = false;
        script.type = "text/javascript";
        script.src = url;
        myIframe.contentWindow.document.head.appendChild(script);
    }



} // !ResizerFactory
