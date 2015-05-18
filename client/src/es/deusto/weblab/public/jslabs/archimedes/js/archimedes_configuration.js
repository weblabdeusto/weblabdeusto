


    var i18n = {
        "en" : {
            "archimedes.experiment": "Archimedes Experiment",
            "time.remaining": "Time remaining",
            "ball.weight.liquid.level" : "Ball weight & Liquid level",
            "close": "Close",
            "hd.picture" : "HD Picture",

            "show": "Show",
            "hide": "Hide",

            "showInstancesHelpTitle": "Show or hide a particular tube",
            "showInstancesHelpContent": "Sometimes you may want to only display some of the available tubes.<br>This way, the screen can be made less cluttered when not all tubes are needed.<br>To choose which instances to show or hide, simply click on their button to toggle their state.",

            "sensorsHelpTitle": "Sensor information",
            "sensorsHelpContent": "The sensors tab displays the data that is reported by the physical level and weight sensors.<br>This data is automatically refreshed.<br><br>Due to the nature of physical sensors, you should not necessarily expect this data to be fully accurate.<br>Particularly, you should notice that, for instance, when the ball is in the water, the weight sensor will often report a number close to zero when the ball is floating. <br><br>Likewise, because these sensors are real, if the data were wrong, it would likely be due to some kind of hardware error.",

            "sensors": "Sensors",
            "liquid": "Liquid",
            "liquid/tube": "Liquid/Tube",
            "ball": "Ball",
            "liquid.level": "Liquid Level",
            "ball.weight": "Ball Weight",
            "volume": "Volume",
            "diameter": "Diameter",
            "internal.diameter": "Internal Diameter",
            "density": "Density",
            "mass": "Mass",
            "grams": "gr",
            "cm": "cm",
            "kgm3": "kg/m³",
            "gcm3": "gr/cm³",
            "m3": "m³",
            "cm3": "cm³",

            // For the Weight/Time plot
            "plot.explanation": "Measures the perceived weight of the ball as reported by the sensor. The depicted timeframe is that of the last ball movement.",
            "time.weight.plot" : "Time / Weight Plot",
            "weight.g" : "Weight (g)",
            "seconds.s" : "Seconds (s)",

            // For the instance names.
            "instance1": "1st Tube",
            "instance2": "2nd Tube",
            "instance3": "3rd Tube",
            "instance4": "4th Tube",
            "instance5": "5th Tube",
            "instance6": "6th Tube",
            "instance7": "7th Tube",
            "instance8": "8th Tube",

            "toggle-show-hide": "Toggle to <strong style=\"color: green\">show</strong> or <strong style=\"color: slategray\">hide</strong> each tube</div>"
        },
        "eu" : {
            "cm": "cm", 
            "instance5": "5. Hodia", 
            "close": "Itxi", 
            "showInstancesHelpContent": "Batzuetan erabilgarri dauden hodiak bakarrik erakutsi nahi izango dituzu.<br>Modu horretan, hodi guztiak beharrezkoak ez direnean pantaila argiago agertuko da.<br> Ze instantzia erkutsi edo ezkutatuko den aukeratzeko, bere egoera aldatzeko botoia soilik klikatu behar duzu.", 
            "plot.explanation": "Bolaren hautemandako balioa sensorearen informazioaren arabera neurtzen du. Deskribatutako denbora tartea bolaren azken mugimenduarena da.", 
            "hide": "Ezkutatu", 
            "hd.picture": "HD Irudia", 
            "density": "Dentsitatea", 
            "sensors": "Sentsoreak", 
            "show": "Erakutsi", 
            "diameter": "Diametroa", 
            "seconds.s": "Segunduak (s)", 
            "liquid.level": "Likidoaren Maila", 
            "m3": "m?", 
            "showInstancesHelpTitle": "Hodi jakin bat erakutsi edo ezkutatu", 
            "sensorsHelpContent": "Sensorearen fitxak maila fisikoaren eta pisuaren sentsoreak emandako datuak agertzen ditu. <br> Datu hauek automatikoki eguneratzen dira.<br><br>Sentsoreen izaera fisikoa dela eta, ez zenuke espero behar datu hauek guztiz zehatzak izatea.<br>Bereziki, konturatu beharko zinateke, adibidez, bola uretan dagoenean, pisuaren sentsorea sarritan zerotik gertu egongo dela bola flotatzen baldin badago.<br><br>Era berean, sensoreak erralak direlako, datuak gaizki egongo baziren, seguruenik hardwarearen akatsen bategatik izango zen.", 
            "cm3": "cm?", 
            "archimedes.experiment": "Archimedes Esperimentua", 
            "ball": "Bola", 
            "ball.weight.liquid.level": "Bola pisua eta eta likidoaren maila", 
            "volume": "Bolumena", 
            "instance3": "3. Hodia", 
            "instance4": "4. Hodia", 
            "instance7": "7. Hodia", 
            "sensorsHelpTitle": "Sentsorearen informazioa", 
            "internal.diameter": "Barne Diametroa", 
            "instance8": "8. Hodia", 
            "ball.weight": "Bola pisua", 
            "weight.g": "Pisua (g)", 
            "instance2": "2. Hodia", 
            "grams": "gr", 
            "liquid": "Likidoa", 
            "time.weight.plot": "Denbora / Pisua Grafikoa", 
            "kgm3": "kg/m?", 
            "liquid/tube": "Likidoa/ Hodia", 
            "instance1": "1. Hodia", 
            "mass": "Masa", 
            "instance6": "6. Hodia", 
            "gcm3": "gr / cm?", 
            "toggle-show-hide": "Aldatu <strong style=\"color: green\">-ra erakutsi</strong> edo <strong style=\"color: slategray\">ezkutatu</strong> hodi bakoitza</div>", 
            "time.remaining": "Geratzen den denbora"
        }
    };

    // TODO: Improve this mechanism using the WebLab API
    var currentLanguage = "en";
    if (top.window.location.href.search("locale=eu") > 0) {
        currentLanguage = "eu";
    } // Other languages
    $.i18n.load(i18n[currentLanguage]);


    var Registry = {
        "archimedes1" : {
            "name": $.i18n._("instance1"),
            "ball_mass": 134, // g
            "ball_diameter": 8.0, // cm
            "ball_density": 0.5,
            "object_density": 0.5,
            "object_volume": 268,
            "object_type": "Ball",
            "liquid_name": "water",
            "liquid_density": 1000, // 1000/m3
            "liquid_diameter": 9.4, // cm
            "webcam": "//cams.weblab.deusto.es/webcam/proxied.py/arquimedes1_rotate"
        },
        "archimedes2" : {
            "name": $.i18n._("instance2"),
            "ball_mass": 56,
            "ball_diameter": 6.0, // cm
            "ball_density": 0.5,
            "object_density": 1.32,
            "object_volume": 113.10,
            "object_type": "Ball",
            "liquid_name": "water",
            "liquid_density": 1000,
            "liquid_diameter": 7, // cm
            "webcam": "//cams.weblab.deusto.es/webcam/proxied.py/arquimedes2_rotate"
        },
        "archimedes3" : {
            "name": $.i18n._("instance3"),
            "ball_mass": 134,
            "ball_diameter": 6, // cm
            "ball_density": 1.18,
            "object_density": 1.18,
            "object_volume": 113.10,
            "object_type": "Ball",
            "liquid_density": 1000, // 1000/m3
            "liquid_diameter": 7, // cm
            "liquid_name": "water",
            "webcam": "//cams.weblab.deusto.es/webcam/proxied.py/arquimedes3_rotate"
        },
        "archimedes4" : {
            "name": $.i18n._("instance4"),
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
            "name": $.i18n._("instance5"),
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
            "name": $.i18n._("instance6"),
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
            "name": $.i18n._("instance7"),
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









