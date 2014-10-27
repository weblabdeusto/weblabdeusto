// File that contains minor experiment-specific UI small utils and fixes.
//

//! Fits the instances by defining the col-md-* classes through JS,
//! depending on the actual number of instances.
//! NO LONGER USED.
function fitInstances(instancesNumber) {
//
//    console.log("[fitInstances]");
//
//    var col = $(".instance-column");
//
//    // Clear the classes before setting the right ones.
//    col.removeAttr("class");
//    col.addClass("instance-column");
//    col.addClass("col-sd-12");
//    col.addClass("column");
//
//    if(instancesNumber == 1) {
//        col.addClass("col-md-6");
//        col.addClass("col-md-offset-3");
//    } else if(instancesNumber == 2) {
//        col.addClass("col-md-6");
//    } else if(instancesNumber == 3) {
//        col.addClass("col-md-4");
//    } else {
//        col.addClass("col-md-3");
//    }
}


//! Fixes the issues that appear because the webcamera image
//! needs to be rotated through CSS.
function fixImageRotation() {
    $(window).resize(function() {
        // The image wrappers should meet the 640x480 aspect ratio of the image.
        var wrapper = $(".arch-img-wrapper");

        // We calculate each separatedly because wrapper.width() returns wrong
        // results from some of the webcams if they are hidden.
        wrapper.each( function() {
            var w = $(this);
            var width = w.width();

            var ratio = 640/480;
            w.height(ratio * width);

            // The image itself should be the wrapper's size. However, the image is
            // rotated, so the width/height are interchanged.
            var img = w.find(".arch-camera");
            img.height(w.width());
            img.width(w.height());
        });

    });

    // Trigger it on the start.
    $(window).trigger("resize");
}