// File that contains minor experiment-specific UI small utils and fixes.
//

//! Fits the instances by defining the col-md-* classes through JS,
//! depending on the actual number of instances.
function fitInstances(instancesNumber) {
    var col = $(".instance-column");

    if(instancesNumber == 1) {
        col.addClass("col-md-6");
        col.addClass("col-md-offset-3");
    } else if(instancesNumber == 2) {
        col.addClass("col-md-6");
    } else if(instancesNumber == 3) {
        col.addClass("col-md-4");
    } else {
        col.addClass("col-md-3");
    }
}


//! Fixes the issues that appear because the webcamera image
//! needs to be rotated through CSS.
function fixImageRotation() {
    $(window).resize(function() {
        // The image wrappers should meet the 640x480 aspect ratio of the image.
        var wrapper = $(".arch-img-wrapper");
        var width = wrapper.width();
        var ratio = 640 / 480;
        wrapper.height(ratio * width);

        // The image itself should be the wrapper's size. However, the image is
        // rotated, so the width/height are interchanged.
        var img = $(".arch-camera");
        img.height(wrapper.width());
        img.width(wrapper.height());
    });

    // Trigger it on the start.
    $(window).trigger("resize");
}