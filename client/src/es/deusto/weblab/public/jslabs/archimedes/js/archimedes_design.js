//! This script is meant to contain the logic of the design view, to be used with the Composer.
//!

ArchimedesDesign = new function() {

    this.enableDesignView = function() {
        View = {};
        archimedesExperiment.updateView(View);

        $("#editmodeh").removeClass("hide");
        $("#timer").hide();

        $(".arch-control, .arch-img-wrapper, .arch-camera").toggleClass("design-editable");
        $("td:first-child").toggleClass("design-editable").toggleClass("design-editable-marked");

        $(".arch-control, .arch-img-wrapper, .arch-camera").off("click");
        $(".arch-img-wrapper, .arch-camera").off("mouseenter mouseleave");

        $(".arch-control, .arch-img-wrapper, .arch-camera, td:first-child").click(function(){
           $(this).toggleClass("design-disabled");
        });
    };


    this.getView = function() {

    };


};


