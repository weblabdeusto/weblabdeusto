
//! CLASS meant to contain the logic for an archimedes instance.
//! The Archimedes experiment can support an arbitrary number of simultaneous
//! Archimedes instances. Each instance will bind itself to specific DOM
//! nodes, which will be identified by the instanceid.
ArchimedesInstance = function (instanceid) {

    // Stores the current sensor values (they are updated somewhat automatically
    // by the retrievers).
    this.sensors = {
        "liquid.level": 0,
        "ball.weight": 0
    };

    // If an instance is paused then it is generally not being shown, and webcam and commands
    // should not be refreshed / sent.
    this.paused = false;

    // Simple utility function to retrieve a CSS selector for an
    // instance-specific ID.
    function getidselect(id) {
        return "#" + instanceid + "-" + id
    };


    // Callback to handle interaction start for the instance.
    // It should be invoked from the single Experiment.
    this.handleStartInteraction = function () {
        // TODO: Remove this.
        //this._retrieveLevelController = StartRetrievingLevel(instanceid, this.sensors);
        //this._retrieveLoadController = StartRetrievingLoad(instanceid, this.sensors);
    };

    // Callback to handle interaction start for the instance.
    // It should be invoked from the single Experiment.
    this.handleEndCallback = function () {
        // TODO: Remove this.
        //this._retrieveLoadController.stop();
        //this._retrieveLevelController.stop();
    };


    // Pauses this instance (stops refreshing webcam, etc)
    this.pause = function() {
        this.cameraRefresher.stop();
        this.paused = true;
    };

    // resumes this instance (refreshes webcam again, etc)
    this.resume = function() {
        this.cameraRefresher.start();
        this.paused = false;
    };


    //! Updates the view to show only those components that it
    //! should, according to the view definition.
    //!
    //! @param inst_view: The part of the view definition that
    //! corresponds to the specific instance. This should be a simple
    //! list with certain fields inside.
    this.updateView = function(inst_view) {

        console.log("Updating view of instance: " + instanceid);

        if(inst_view === undefined || inst_view === "ALL") {
            inst_view = ["controls", "sensor_weight", "sensor_level",  "webcam", "hdcam", "plot", "ball_mass",
            "ball_volume", "ball_diameter", "ball_density", "liquid_density", "liquid_diameter"]
        }


        // WARNING: This code is currently affected by https://bugzilla.mozilla.org/show_bug.cgi?id=1012413
        // and doesn't work properly on Firefox.

        if(inst_view.length == 0) {
            $(getidselect("experiment-instance")).hide();
        } else {
            $(getidselect("experiment-instance")).show();
        }



        // The following element names are the specific names
        // that the View MUST contain or not.
        var elements = {
            "webcam" : $(getidselect("webcam-wrapper")),
            "controls" : $(getidselect("upButton") + "," + getidselect("downButton")),
            "hdcam" : $(getidselect("photoButton")),
            "plot" : $(getidselect("plotButton"))
        };

        // Store them internally.
        this.elements = elements;

        // Hide those elements which aren't present in the inst_view list.
        $.each(elements, function(elem, selector) {
            if(inst_view.indexOf(elem) > -1)
                selector.show();
            else
                selector.hide();
        });


        // Match the View options to the names within the data table.
        var sensor_matches = {
            "sensor_level" : "liquid.level",
            "sensor_weight" : "ball.weight"
        };

        var liquid_matches = {
            "liquid_density": "density",
            "liquid_diameter": "internal.diameter"
        };

        var ball_matches = {
            "ball_mass": "mass",
            "ball_diameter": "diameter",
            "ball_density": "density",
            "ball_volume": "volume"
        };

        // Control visibility for the Sensors table.
        var sensors = $(getidselect("table-sensors"));
        var nshown = 0;
        $.each(sensor_matches, function(key, value) {
            if(inst_view.indexOf(key) > -1) {
                sensors.datatable("show", value);
                nshown++;
            }
            else
                sensors.datatable("hide", value);
        });
        if(nshown == 0)
            sensors.datatable("hideAll");
        else
            sensors.datatable("showAll");


        // Control visibility for the Liquid table.
        var liquid = $(getidselect("table-liquid"));
        nshown = 0;
        $.each(liquid_matches, function(key, value) {
            if(inst_view.indexOf(key) > -1) {
                liquid.datatable("show", value);
                nshown++;
            }
            else
                liquid.datatable("hide", value);
        });
        if(nshown == 0)
            liquid.datatable("hideAll");
        else
            liquid.datatable("showAll");

        // Control visibility for the ball table.
        var ball = $(getidselect("table-ball"));
        nshown = 0;
        $.each(ball_matches, function(key, value) {
            if(inst_view.indexOf(key) > -1) {
                ball.datatable("show", value);
                nshown++;
            }
            else
                ball.datatable("hide", value);
        });
        if(nshown == 0)
            ball.datatable("hideAll");
        else
            ball.datatable("showAll");

    };


    // Creates the data tables for the instance.
    this.createDataTables = function() {

        // Creates the data tables, and data-bind them to the values.
        $(getidselect("table-sensors")).datatable({
            header: $.i18n._("sensors"),
            vars: {
                "liquid.level": function() { return this.sensors["liquid.level"] + " " + $.i18n._("cm"); }.bind(this),
                "ball.weight": function() { return this.sensors["ball.weight"] + " " + $.i18n._("grams"); }.bind(this)
            },
            translator: $.i18n._.bind($.i18n)
        });

        // Create the tooltip for the sensors tab.
        var sensorsrow = $(getidselect("table-sensors")).find("thead>tr>:first-child");
        var tooltip = $('<a tabindex="0" style="margin-left: 1em; font-size: 1.2em;" class="glyphicon glyphicon-info-sign"/>');
        sensorsrow.append(tooltip);
        tooltip.popover({html: true, placement: "bottom", trigger: "", title: $.i18n._("sensorsHelpTitle"), content: $.i18n._("sensorsHelpContent")})

        $(getidselect("table-liquid")).datatable({
            header: $.i18n._("Liquid"),
            vars: {
                "density": Registry[instanceid]["liquid_density"] / 1000.0 + " " + $.i18n._("gcm3"),
                "internal.diameter": Registry[instanceid]["liquid_diameter"] + " " + $.i18n._("cm")
            },
            translator: $.i18n._.bind($.i18n)
        });

        $(getidselect("table-ball")).datatable({
            header: $.i18n._("ball"),
            vars: {
                "mass": Registry[instanceid]["ball_mass"] + " " + $.i18n._("grams"),

                "diameter": Registry[instanceid]["ball_diameter"] + " " + $.i18n._("cm"),

                "density": function() {
                        var r = this["ball_diameter"] / (2 * 100); //  Radius: cm to m
                        var vol = (4/3) * Math.PI * r * r * r * 1000000; // m3 to cm3
                        var den = this["ball_mass"] / vol; // Density: g / cm3
                        return den.toFixed(2) + " " + $.i18n._("gcm3");
                }.bind(Registry[instanceid]),

                "volume": function() {
                    var r = this["ball_diameter"] / (2 * 100); //  To meters
                    var vol = (4/3) * Math.PI * r * r * r * 1000000; // m3 to cm3
                    return vol.toFixed(2) + " " + $.i18n._("cm3");
                }.bind(Registry[instanceid])
            },
            translator: $.i18n._.bind($.i18n)
        });
    };


    //! Reports an update to the ball status.
    //! The update may actually not be so; the ball status
    //! might be the same as the previous.
    //!
    this.updateBallStatus = function(ballStatus) {
        if(ballStatus == 'BALL_UP') {
            // The ball is UP, DOWN should be enabled, UP should be disabled.
            this.setUpDownStatus(false, true);
        }
        else if(ballStatus == 'BALL_DOWN') {
            this.setUpDownStatus(true, false);
        }
        else if(ballStatus == 'BALL_GOING_DOWN')
        {
            this.setUpDownStatus(false, false);
        }
        else if(ballStatus == 'BALL_GOING_UP')
        {
            this.setUpDownStatus(false, false);
        }
        else
        {
            console.error("Unexpected ball status: " + ballStatus);
            // Enable everything, This shouldn't happen though.
            this.setUpDownStatus(true, true);
        }
    };


    /**
     * Sets the status of the up and down buttons. (Whether they are enabled or disbaled)
     *
     */
    this.setUpDownStatus = function(upEnabled, downEnabled) {
        if(downEnabled) {
            $(getidselect("downButton") + " img").attr("src", "img/down_green.png");
            $(getidselect("downButton")).removeAttr("disabled");
        } else {
            $(getidselect("downButton") + " img").attr("src", "img/down.png");
            $(getidselect("downButton")).attr("disabled", "disabled");
        }

        if(upEnabled) {
            $(getidselect("upButton") + " img").attr("src", "img/up_green.png");
            $(getidselect("upButton")).removeAttr("disabled");
        } else {
            $(getidselect("upButton") + " img").attr("src", "img/up.png");
            $(getidselect("upButton")).attr("disabled", "disabled");
        }
    };


    //! Initializes the Archimedes instance.
    //!
    this.initializeInstance = function() {

        // Create the data tables.
        this.createDataTables();


        // Call an updateView so that view-related things are always initialized.
        this.updateView();

        this.cameraRefresher = new CameraRefresher(instanceid + "-cam1");
        this.cameraRefresher.setInterval(500);

        // Create the timer for later.
        timerDisplayer = new TimerDisplayer(instanceid + "-timer");

        // Declare button handlers.
        var downButton = $(getidselect("downButton"));
        downButton.click(function () {

            console.log("DOWN");

            if (downButton.attr("disabled") == undefined) {
                weblab.sendCommand(instanceid + ":DOWN")
                    .done(
                        function (success) {
                            //$(getidselect("downButton") + " img").attr("src", "img/down_green.png");
                            //$(getidselect("downButton")).removeAttr("disabled");
                        })
                    .fail(
                        function (error) {
                            console.error("DOWN command failed: " + error);
                            displayErrorMessage("DOWN command failed");
                        });
            }

            //$(getidselect("downButton") + " img").attr("src", "img/down.png");
            //$(getidselect("downButton")).attr("disabled", "disabled");
        });

        var upButton = $(getidselect("upButton"));
        $(upButton).click(function () {
            console.log("UP");

            if (upButton.attr("disabled") == undefined) {
                weblab.sendCommand(instanceid + ":UP")
                    .done(
                    function (success) {
                        //upButton.find("img").attr("src", "img/up_green.png");
                        //upButton.removeAttr("disabled");
                    })
                    .fail(
                    function (error) {
                        console.error("UP command failed: " + error);
                        displayErrorMessage("UP command failed");
                    });
            }

            // Disable the button for now.
            //upButton.find("img").attr("src", "img/up.png");
            //upButton.attr("disabled", "disabled");
        });

        var photoButton = $(getidselect("photoButton"));
        photoButton.click(function () {

            console.log("IMAGE");
            if ($(photoButton).attr("disabled") == undefined) {

                //$("#hdpic").attr("src", "img/image_placeholder.png");
                //$("#hdpic").attr("src", "");
                $("#photoModal").modal();

                weblab.sendCommand(instanceid + ":IMAGE")
                    .done(
                    function (data) {
                        photoButton.removeAttr("disabled");

                        $("#hdpic").attr("src", "data:image/jpg;base64," + data);
                        $(this).find("img").attr("src", "img/photo_green.png");
                    })
                    .fail(
                    function (error) {
                        console.error("Error: " + error);
                        displayErrorMessage("IMAGE command failed");
                    });
            }

            // Disable the button for now.
            $(this).find("img").attr("src", "img/photo.png");
            $(this).attr("disabled", "disabled");
        });


        var plotButton = $(getidselect("plotButton"));
        plotButton.click(function () {
            console.log("PLOT");

            if ($(plotButton).attr("disabled") == undefined) {

                $("#plotModalBody").empty();
                $("#plotModal").modal();

                // For debugging purpose, when offline we hard-code the data.
                var fakeData = "1:20\n" +
                    "2:40\n" +
                    "3:60\n" +
                    "4:90";

                weblab.setSendCommandResponse(fakeData);

                weblab.sendCommand(instanceid + ":PLOT")
                    .done(
                    function (data) {

                        plotButton.removeAttr("disabled");

                        // Parse the data to convert each element into a "number" & "value" object.
                        var items = [];
                        var lines = data.split("\n");
                        $.each(lines, function (index, line) {
                            if (line.length <= 1)
                                return;
                            var elems = line.split(":");
                            var number = elems[0];
                            var value = elems[1];
                            items.push({"number": number, "value": value});
                        });

                        drawChart(items);

                        plotButton.find("img").attr("src", "img/plot_green.png");
                    })
                    .fail(
                    function (error) {
                        console.error("Error: " + error);
                        displayErrorMessage("PLOT command failed");
                    });
            }

            // Disable the button for now.
            $(this).find("img").attr("src", "img/plot.png");
            $(this).attr("disabled", "disabled");
        });

    }; //! End-of initializeInstance()


}; //! End-of ArchimedesInstance
