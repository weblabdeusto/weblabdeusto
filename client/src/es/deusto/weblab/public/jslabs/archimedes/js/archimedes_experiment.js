//! CLASS meant to contain the experiment and the logic that is not
//! specific to an instance. It will handle the creation of the appropriate
//! Archimedes Instances.
//! There should exist a single instance of this class,
//! no matter how many Archimedes Instances there are.
//!
//! @param registry: Registry object of Archimedes instance data,
//! from which the instances themselves will be constructed.
ArchimedesExperiment = function (registry) {

    // To store the instances.
    this.instances = {};

    // Initializes the experiment, by creating all instances and rendering the templates.
    // Most of the initialization is done asynchronously.
    this.initialize = function () {
        var archimedes_instance_tpl = $.get("archimedes_instance_tpl.html", function (template) {

            var rendered = "";
            var instancesNumber = 0;

            // Render the HTML for every instance.
            for (var instance in Registry) {
                if (!Registry.hasOwnProperty(instance))
                    continue;

                var data = Registry[instance];
                instancesNumber += 1;
                rendered += Mustache.render(template, {"instanceid": instance, "webcam": data.webcam});
            }

            // Insert it.
            $(".instances_row").html(rendered);

            // Dynamically size the bootstrap columns so that it looks pretty enough.
            fitInstances(instancesNumber);

            // Initialize every Archimedes instance.
            for (var instance in registry) {
                if (!Registry.hasOwnProperty(instance))
                    continue;

                var archimedesInstance = new ArchimedesInstance(instance);
                archimedesInstance.initializeInstance();

                this.instances[instance] = archimedesInstance;
            }

            // Fix the issue with the webcam image rotation.
            fixImageRotation();

            // Enable image zooming on hover.
            enableImageZooming();


            // Declare onStartInteraction listener.
            Weblab.setOnStartInteractionCallback(function () {
                showFrame();

                $.each(this.instances, function (instanceid, instance) {
                    instance.handleStartInteraction();
                }.bind(this));
            }.bind(this));


            Weblab.setOnEndCallback(function () {
                hideFrame();

                $.each(this.instances, function (instanceid, instance) {
                    instance.handleEndCallback();
                }.bind(this));
            }.bind(this));


        }.bind(this)); //! template $.get
    };

    // To set the timer to its initial value.
    function setTimeToGo(time) {
        //timer function
        var d = new Date();
        d.setTime(d.getTime() + (time * 1000));
        //$('#timer').tinyTimer({ to: d });

        timerDisplayer.setTimeLeft(time);
        timerDisplayer.startCountDown();
    }


    //////////////////
    // CONSTRUCTION //
    //////////////////


    this.initialize();

    // Set the timer initialization handler.
    Weblab.setOnTimeCallback(function (time) {
        //debugger;
        console.log("[DBG]: Time left: " + time);
        setTimeToGo(time);
    });

}; //! End-of ArchimedesInstance
