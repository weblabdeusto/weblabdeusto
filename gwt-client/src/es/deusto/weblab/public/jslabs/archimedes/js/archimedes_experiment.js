REFRESH_DATA_INTERVAL = 1000;

//! CLASS meant to contain the experiment and the logic that is not
//! specific to an instance. It will handle the creation of the appropriate
//! Archimedes Instances.
//! There should exist a single instance of this class,
//! no matter how many Archimedes Instances there are.
//!
//! @param registry: Registry object of Archimedes instance data,
//! from which the instances themselves will be constructed.
//!
//! @param view: View definition. To indicate which components of each
//! instance are shown and which are not.
ArchimedesExperiment = function (registry, view) {

    // To store the instances.
    this.instances = {};

    // Initializes the experiment, by creating all instances and rendering the templates.
    // Most of the initialization is done asynchronously.
    this.initialize = function () {

        // If we are running in the WEBLAB mode and not stand-alone, we hide the frame.
        if (Weblab.checkOnline() == true)
            hideFrame();

        var archimedes_instance_tpl = $.get("archimedes_instance_tpl.html", function (template) {

            var rendered = "";
            var instancesNumber = 0;

            // Render the HTML for every instance.
            for (var instance in Registry) {
                if (!Registry.hasOwnProperty(instance))
                    continue;

                var data = Registry[instance];
                instancesNumber += 1;
                rendered += Mustache.render(template, {"instanceid": instance, "webcam": data.webcam, instancename: Registry[instance].name});
            }

            // Insert it.
            $(".instances_row").html(rendered);

            // No longer done. Archimedes instances will look somewhat small on large screens but that way
            // there won't be issues with smaller ones.
            // fitInstances(instancesNumber);

            // Initialize every Archimedes instance.
            for (var instance in registry) {
                if (!Registry.hasOwnProperty(instance))
                    continue;

                var archimedesInstance = new ArchimedesInstance(instance);
                archimedesInstance.initializeInstance();

                this.instances[instance] = archimedesInstance;
            }

            // Hides those components that should not be shown according to the
            // specified view.
            this.updateView();

            // Enable image zooming on hover.
            enableImageZooming();

            // Translate the interface.
            this.translateInstanceInterface();

            // Add the instance selector for the design view.
//            $.each(Registry, function(name, instdata) {
//                var cb = $('<input type="checkbox"/>').attr(
//                    {"id": "is-" + name, "value": name});
//                var div = $("<div></div>")
//                cb.appendTo(div);
//                cb.after(name);
//                div.appendTo($(".instances_select"));
//            });


            console.log("Setting onStartInteractionCallback");

            // Declare onStartInteraction listener.
            // This is at times not getting called.
            // TODO: Fix this.
            Weblab.setOnStartInteractionCallback(function (initial_config) {

                console.log("[OnStartInteractionCallback");

                showFrame();

                if(typeof(initial_config) === "string") {
                    var config = JSON.parse(initial_config);
                    console.log("Initial config: ");
                    console.log(config);

                    if("view" in config) {
                        // If the config specifies the view we must initialize it accordingly.
                        View = config["view"];
                    }

                    this.updateView();
                }

                console.log("Starting refreshing data");

                this.startRefreshingData();

                $.each(this.instances, function (instanceid, instance) {
                    instance.handleStartInteraction();
                    var data = Registry[instanceid];
                    instance.cameraRefresher.start(data.webcam);
                }.bind(this));
                //debugger;


            }.bind(this));



            Weblab.setOnEndCallback(function () {

                this.stopRefreshingData();

                hideFrame();

                $.each(this.instances, function (instanceid, instance) {
                    instance.handleEndCallback();
                }.bind(this));
            }.bind(this));


        }.bind(this)); //! template $.get
    };


    // Repeteadly queries the server for data for all
    // instances.
    this.startRefreshingData = function() {
        var that = this;
        var command = "ALLINFO";

        var that = this;
        $.each(View, function(name, data) {
            var instance = that.instances[name];

            // Do not request updates for paused instances.
            if(instance.paused == false)
            {
                command += ":" + name;
            }
        });

        Weblab.dbgSetOfflineSendCommandResponse('{"archimedes1":{"level":2000, "load":3000}}');
        Weblab.sendCommand(command,
            function(data) {
                var response = JSON.parse(data);

                console.log("Refreshing data: ");
                console.log(response);

                $.each(response, function(inst, data) {

                    if(!(inst in that.instances)) {
                        console.error("ALLINFO: Reported instance is not registered. Ignoring it.");
                        return true;
                    }

                    var instance = that.instances[inst];

                    instance.sensors["liquid.level"] = data["level"];
                    instance.sensors["ball.weight"] = data["load"];
                    instance.updateBallStatus(data["ball_status"]);

                    $("#" + inst + "-table-sensors").datatable("updateAll");

                    return true;
                });

                // Invoke a refresh again in some seconds.
                that._refresh_timer = setTimeout(that.startRefreshingData, REFRESH_DATA_INTERVAL);
            },
            function() {
                // BUGFIX: In case of error, we will retry to refresh in twice the standard refresh data interval.
                console.error("[Error]: Refreshing data. Retrying soon.");
                that._refresh_timer = setTimeout(that.startRefreshingData, REFRESH_DATA_INTERVAL * 2);
            });
    }.bind(this);

    // Stops querying the server for data.
    this.stopRefreshingData = function() {
        if(this._refresh_timer !== undefined)
            clearTimeout(this._refresh_timer);
    };

    // To set the timer to its initial value.
    this.setTimeToGo = function(time) {
        //timer function
        var d = new Date();
        d.setTime(d.getTime() + (time * 1000));

        this.timerDisplayer.setTimeLeft(time);
        this.timerDisplayer.startCountDown();
    };


    //! Defines (for the first or nth time) which components
    //! are seen and which are not, through the provided view.
    //!
    //! @param view: View definition. Optional. Uses Configuration.getView() by default.
    this.updateView = function(view) {

        console.log("Update view");

        if(view == undefined)
            view = Configuration.getView();

        console.log("Updating view of all instances");
        console.log(view);

        $.each(this.instances, function(name, instance) {
            if(name in view) {
                var inst_view = view[name];
                instance.updateView(inst_view);
            } else {
                instance.updateView([]);
            }
        }.bind(this));

        // Fit the bootstrap cols properly.
        // fitInstances($(".instance-column:visible").length);

        // Reinitialize the client-side control to show or hide full instances.
        initializeShownPanel();

        console.log("Setting length: " + $(".instance-column:visible").length);
    };

    //! Handles translation for the dynamic part of the interface.
    //!
    this.translateInstanceInterface = function() {
        $(".title-ballinfo").text($.i18n._("ball.weight.liquid.level"));
        $("#plotexplanation").text($.i18n._("plot.explanation"))
    };


    //////////////////
    // CONSTRUCTION //
    //////////////////


    this.initialize();

    this.timerDisplayer = new TimerDisplayer("timer");

    // Set the timer initialization handler.
    Weblab.setOnTimeCallback(function (time) {
        console.log("[DBG]: Time left: " + time);
        this.setTimeToGo(time);
    }.bind(this));

}; //! End-of ArchimedesInstance
