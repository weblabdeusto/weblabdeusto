//! Enables the image zooming feature.
//!
function enableImageZooming() {


    var cams = $(".arch-camera");

    function makeBig(cam) {
        cam.addClass("arch-camera_hover");
    }

    function makeSmall(cam) {
        cam.removeClass("arch-camera_hover");
    }

    cams.hover(function (ev) {
        var cam = $(this);

        if (ev.type == "mouseenter") {
            makeBig(cam);
        } else {
            makeSmall(cam);
        }
    });


    cams.click(function (ev) {
        var cam = $(this);
        if(cam.hasClass("arch-camera_hover")) {
            makeSmall(cam);
        } else {
            makeBig(cam);
        }
    });

} //! enableImageZooming.
