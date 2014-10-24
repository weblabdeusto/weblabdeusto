
    var Registry = {
        "archimedes1" : {
            "ball_mass": 32.7, // g
            "ball_diameter": 3.9, // cm
            "ball_density": 1.05,
            "liquid_name": "water",
            "liquid_density": 1000, // 1000/m3
            "liquid_diameter": 7, // cm
            "webcam": "//www.weblab.deusto.es/webcam/proxied.py/arquimedes1"
        },
        "archimedes2" : {
            "ball_mass": 41,
            "ball_diameter": 3.9, // cm
            "ball_density": 1.32,
            "liquid_name": "water",
            "liquid_density": 1000,
            "liquid_diameter": 7, // cm
            "webcam": "//www.weblab.deusto.es/webcam/proxied.py/arquimedes2"
        },
        "archimedes3" : {
            "ball_mass": 2.8,
            "ball_diameter": 3.9, // cm
            "ball_density": 0.09,
            "liquid_density": 1000, // 1000/m3
            "liquid_diameter": 7, // cm
            "liquid_name": "water",
            "webcam": "//www.weblab.deusto.es/webcam/proxied.py/arquimedes3"
        },
        "archimedes4" : {
            "ball_mass": 30,
            "ball_diameter": 3.9, // cm
            "ball_density": 0.96,
            "liquid_density": 1000, // 1000/m3
            "liquid_diameter": 7, // cm
            "liquid_name": "water",
            "webcam": "//www.weblab.deusto.es/webcam/proxied.py/arquimedes4"
        },
        "archimedes5" : {
            "ball_mass": 20,
            "ball_density": 60,
            "liquid_density": 1000, // 1000/m3
            "liquid_diameter": 7, // cm
            "liquid_name": "water",
            "webcam": "//www.weblab.deusto.es/webcam/proxied.py/arquimedes5"
        },
        "archimedes6" : {
            "ball_mass": 89.1,
            "ball_density": 0.79,
            "ball_diameter": 6, // cm
            "liquid_density": 1000, // 1000/m3
            "liquid_diameter": 7, // cm
            "liquid_name": "water",
            "webcam": "//www.weblab.deusto.es/webcam/proxied.py/arquimedes6"
        },
        "archimedes7" : {
            "ball_mass": 43.3,
            "ball_density": 0.66,
            "ball_diameter": 5, // cm
            "liquid_density": 1000, // 1000/m3
            "liquid_diameter": 7, // cm
            "liquid_name": "water",
            "webcam": "//www.weblab.deusto.es/webcam/proxied.py/arquimedes7"
        }
    };



    // Possible values:
    // ["controls", "sensor_weight", "sensor_level", "webcam", "hdcam", "plot", "ball_mass", "ball_volume",
    // "ball_diameter", "ball_density", "liquid_density", "liquid_diameter", "liquid_volume"]
    var View = {
        "archimedes1" : ["controls", "sensor_weight",  "sensor_level", "webcam", "hdcam", "plot", "ball_mass",
            "ball_volume", "ball_diameter", "ball_density", "liquid_density", "liquid_diameter"],
        "archimedes2" : "ALL",
        "archimedes3" : "ALL",
        "archimedes4" : "ALL",
        "archimedes5" : "ALL",
        "archimedes6" : "ALL",
        "archimedes7" : "ALL"
    };


    var EDTFilter = {
        //"ball_mass" : 20
    };



    //! Pseudo-class to manage EDT-config filtering.
    //!
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
        this.getFilteredView = function() {

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








    //! Global pseudo-class which will be used through the code
    //! to access the current view etc.
    Configuration = new function() {

        //! Returns the current global registry.
        this.getRegistry = function() {
            return Registry;
        };

        //! Returns the current view, filtered by the Registry and the EDTFilter.
        this.getView = function() {
            return EDT.getFilteredView();
        };

    };









