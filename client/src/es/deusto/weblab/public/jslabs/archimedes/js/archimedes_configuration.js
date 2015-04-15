
    var Registry = {
        "archimedes1" : {
            "name": "1st Tube",
            "ball_mass": 155, // g
            "ball_diameter": 6.0, // cm
            "ball_density": 0.5,
            "object_density": 0.5,
            "object_volume": 310,
            "object_type": "Cylinder",
            "liquid_name": "water",
            "liquid_density": 1000, // 1000/m3
            "liquid_diameter": 9.4, // cm
            "webcam": "//cams.weblab.deusto.es/webcam/proxied.py/arquimedes1_rotate"
        },
        "archimedes2" : {
            "name": "2nd Tube",
            "ball_mass": 56,
            "ball_diameter": 6.0, // cm
            "ball_density": 0.5,
            "object_type": "cylinder",
            "object_density": 1.32,
            "object_volume": 113.10,
            "object_type": "Ball",
            "liquid_name": "water",
            "liquid_density": 1000,
            "liquid_diameter": 7, // cm
            "webcam": "//cams.weblab.deusto.es/webcam/proxied.py/arquimedes2_rotate"
        },
        "archimedes3" : {
            "name": "3rd Tube",
            "ball_mass": 155,
            "ball_diameter": 6, // cm
            "ball_density": 1.17,
            "object_density": 1.17,
            "object_volume": 113.10,
            "object_type": "Ball",
            "liquid_density": 1000, // 1000/m3
            "liquid_diameter": 7, // cm
            "liquid_name": "water",
            "webcam": "//cams.weblab.deusto.es/webcam/proxied.py/arquimedes3_rotate"
        },
        "archimedes4" : {
            "name": "4th Tube",
            "ball_mass": 111,
            "ball_diameter": 6, // cm
            "ball_density": 0.98,
            "object_density": 0.98,
            "object_volume": 113.10,
            "object_type": "Ball",
            "liquid_density": 1000, // 1000/m3
            "liquid_diameter": 7, // cm
            "liquid_name": "water",
            "webcam": "//cams.weblab.deusto.es/webcam/proxied.py/arquimedes4_rotate"
        },
        "archimedes5" : {
            "name": "5th Tube",
            "ball_mass": 111,
            "ball_diameter": 6.0    , // cm
            "ball_density": 0.98,
            "object_density": 0.98,
            "object_volume": 113.10,
            "object_type": "Ball",
            "liquid_density": 900, // 900/m3
            "liquid_diameter": 7, // cm
            "liquid_name": "oil",
            "webcam": "//cams.weblab.deusto.es/webcam/proxied.py/arquimedes5_rotate"
        },
        "archimedes6" : {
            "name": "6th Tube",
            "ball_mass": 89.3,
            "ball_density": 0.79,
            "object_density": 0.79,
            "object_volume": 113.10,
            "object_type": "Ball",
            "ball_diameter": 6, // cm
            "liquid_density": 1000, // 1000/m3
            "liquid_diameter": 7, // cm
            "liquid_name": "water",
            "webcam": "//cams.weblab.deusto.es/webcam/proxied.py/arquimedes6_rotate"
        },
        "archimedes7" : {
            "name": "7th Tube",
            "ball_mass": 50.9,
            "ball_density": 0.78,
            "object_density": 0.78,
            "object_volume": 65.45,
            "object_type": "Ball",
            "ball_diameter": 5, // cm
            "liquid_density": 1000, // 1000/m3
            "liquid_diameter": 7, // cm
            "liquid_name": "water",
            "webcam": "//cams.weblab.deusto.es/webcam/proxied.py/arquimedes7_rotate"
        }
    };



    // Possible values:
    // ["controls", "sensor_weight", "sensor_level", "webcam", "hdcam", "plot", "ball_mass", "ball_volume",
    // "ball_diameter", "ball_density", "liquid_density", "liquid_diameter", "liquid_volume"]
    var View = {
        "archimedes1" : ["controls", "sensor_weight",  "sensor_level", "webcam", "hdcam", "plot", "ball_mass",
            "ball_volume", "ball_diameter", "ball_density", "liquid_density", "liquid_diameter"],
        "archimedes2" : "ALL",
        "archimedes3" : ["controls", "sensor_level", "sensor_weight", "webcam", "hdcam", "plot", "ball_mass",
            "ball_volume", "ball_diameter", "ball_density", "liquid_density", "liquid_diameter"], // Fake weight
        "archimedes4" : "ALL",
        "archimedes5" : ["controls", "sensor_level", "sensor_weight", "webcam", "hdcam", "plot", "ball_mass",
            "ball_volume", "ball_diameter", "ball_density", "liquid_density", "liquid_diameter"], // Fake weight
        "archimedes6" : ["controls", "sensor_level", "sensor_weight", "webcam", "hdcam", "plot", "ball_mass",
            "ball_volume", "ball_diameter", "ball_density", "liquid_density", "liquid_diameter"], // Fake weight
        "archimedes7" : ["controls", "sensor_level", "sensor_weight", "webcam", "hdcam", "plot", "ball_mass",
            "ball_volume", "ball_diameter", "ball_density", "liquid_density", "liquid_diameter"]  // Fake weight
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









