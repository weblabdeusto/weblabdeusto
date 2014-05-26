

//! Enables the image zooming feature.
//! As of now, when the webcam images are zoomed in this script
//! makes them bigger and centered. Eventually the behaviour
//! will probably need to be modified slightly for touch devices.
//!
function enableImageZooming() {

    $(".arch-camera").hover(function(ev){
        var cam = $(this);

        if(ev.type == "mouseenter") {
            // Store the original dimensions.
            cam.data("original-dimensions", {w: cam.width(), h: cam.height()});

            cam.width(cam.width() * 1.5);
            cam.height(cam.height() * 1.5);

            // Center it.
            cam.css("left", "" + -cam.width() / 8 + "px");
        } else {
            // Restore the original dimensions.
            var original = cam.data("original-dimensions");
            cam.width(original.w);
            cam.height(original.h);

            // Center it.
            cam.css("left", "0px");
        }
    });

} //! enableImageZooming.
