
EDTFilter = {
    "ball_mass": 31
};

EDT = new function() {

    this.filters = {

        //! @param instance: Instance to check.
        //! @param edtvalue: Specified edtvalue.
        //! @return: True if the instance meets the criteria.
        "ball_mass" : function(instance, grams) {
            return instance["ball_mass"] == grams; // ball_mass expected in grams
        },
        "ball_volume" : function(instance, volcm3) {
            var radius_cm = 0.5 * instance["ball_diameter"];
            var vol_cm3 = (4/3) * Math.PI * radius_cm * radius_cm * radius_cm; // ball_volume expected in cm3
            return vol_cm3 == volcm3;
        },
        "liquid_density" : function(instance, kgm3) {
            return instance["liquid_density"] == kgm3;
        }

    };


    //! Gets the result of filtering the global Registry with the global EDTFilter filter.
    //! (Applying it to the View).
    this.getFilteredRegistry = function() {

        // Clone the view.
        view = JSON.parse(JSON.stringify(View));

        var that = this;
        $.each(Registry, function(name, instance) {
            $.each(EDTFilter, function(variable, value) {
                if(variable in that.filters)
                    // If the filter check returns false we remove the instance from the list to show.
                    if(!that.filters[variable](instance, value)) {
                        delete view[name];
                    }
            });
        });

        return view;
    }; // !getFilteredRegistry

}; // !EDT