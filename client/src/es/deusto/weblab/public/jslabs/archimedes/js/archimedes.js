ArchimedesInstance = function (instanceid) {

    var state;
    var response;
    var remainingTime;


    LoadRetriever = function (instanceid) {
        //to retrive real time parameters

        var _timeout = undefined;

        this.readSuccess = function (response) {
            console.log(response);
            var load = parseFloat(response);
            $("#" + instanceid + "-load").text(load + " gr.");
        };

        this.readFailure = function (response) {
            //console.log(response);
            console.log("Error retrieving LOAD");
        };

        this.readParams = function () {
            //read params

            // Create a fake PARAMS response, for testing offline.
            var rand1 = Math.random() * 10;
            fakeResponse = rand1;
            //console.log(fakeResponse);
            //debugger;
            Weblab.dbgSetOfflineSendCommandResponse(fakeResponse, true);
            if (Weblab.isExperimentActive() || Weblab.checkOnline() == false)
                Weblab.sendCommand("LOAD", this.readSuccess, this.readFailure);
        };

        this.refreshParams = function () {
            //to auto refresh every 3 sec
            try {
                //try this
                this.readParams();
            }
            catch (error) {
                //error
                console.log("Error Refreshing LOAD");
            }
            _timeout = setTimeout(this.refreshParams.bind(this), 3000);
        };

        this.stop = function () {
            if (_timeout != undefined) {
                clearTimeout(_timeout);
                _timeout = undefined;
            }
        };

    }//end of load retrive

    LevelRetriever = function (instanceid) {
        //to retrive real time parameters

        var _timeout = undefined;

        this.readSuccess = function (response) {
            console.log(response);

            var level = parseFloat(response);

            $("#" + instanceid + "-level").text(level + " cm. ");
        };

        this.readFailure = function (response) {
            console.log(response);
            console.log("Error retriving LEVEL");
        };

        this.readParams = function () {
            //read params

            // Create a fake PARAMS response, for testing offline.
            var rand1 = Math.random() * 10;
            fakeResponse = rand1;
            //console.log(fakeResponse);
            //debugger;
            Weblab.dbgSetOfflineSendCommandResponse(fakeResponse, true);
            if (Weblab.isExperimentActive() || Weblab.checkOnline() == false)
                Weblab.sendCommand("LEVEL", this.readSuccess, this.readFailure);
        };

        this.refreshParams = function () {
            //to auto refresh every 3 sec
            try {
                //try this
                this.readParams();
            }
            catch (error) {
                //error
                console.log("Error Refreshing LEVEL");
            }
            _timeout = setTimeout(this.refreshParams.bind(this), 3000);
        };

        this.stop = function () {
            if (_timeout != undefined) {
                clearTimeout(_timeout);
                _timeout = undefined;
            }
        }
    }//end of level retrive


    function setTimeToGo(time) {
        //timer function
        var d = new Date();
        d.setTime(d.getTime() + (time * 1000));
        //$('#timer').tinyTimer({ to: d });

        timerDisplayer.setTimeLeft(time);
        timerDisplayer.startCountDown();
    }


    Weblab.setOnTimeCallback(function (time) {
        //debugger;
        console.log("[DBG]: Time left: " + time);
        setTimeToGo(time);
    });

    Weblab.setOnStartInteractionCallback(function () {
        showFrame();
        console.log("[DBG]: On start interaction");

        loadRetriever = new LoadRetriever("name1");
        levelRetriever = new LevelRetriever("name1");
        loadRetriever.refreshParams();
        levelRetriever.refreshParams();

        //light_page();
    });

    Weblab.setOnEndCallback(function () {
        hideFrame();
        console.log("[DBG]: On end interaction");
        LoadRetriever.stop();
        LevelRetriever.stop();
    });


    //! Initializes the Archimedes instance.
    //!
    this.initializeInstance = function() {

        function getidselect(id) {
            return "#" + instanceid + "-" + id
        }

        // If we are running in the WEBLAB mode and not stand-alone, we hide the frame.
        if (Weblab.checkOnline() == true)
            hideFrame();

        var refresher1 = new CameraRefresher(instanceid + "-cam1");
        var refresher2 = new CameraRefresher(instanceid + "-cam2");
        refresher1.start();
        refresher2.start();

        // Create the timer for later.
        timerDisplayer = new TimerDisplayer(instanceid + "-timer");

        // Declare button handlers.
        var downButton = $(getidselect("downButton"));
        downButton.click(function () {

            console.log("DOWN");

            if (downButton.attr("disabled") == undefined) {
                Weblab.sendCommand("DOWN",
                    function (success) {
                        $(getidselect("downButton") + " img").attr("src", "img/down_green.png");
                        $(getidselect("downButton")).removeAttr("disabled");
                    },
                    function (error) {
                        console.error("DOWN command failed: " + error);
                        displayErrorMessage("DOWN command failed");
                    });
            }

            $(getidselect("downButton") + " img").attr("src", "img/down.png");
            $(getidselect("downButton")).attr("disabled", "disabled");
        });

        var upButton = $(getidselect("upButton"));
        $(upButton).click(function () {
            console.log("UP");

            if (upButton.attr("disabled") == undefined) {
                Weblab.sendCommand("UP",
                    function (success) {
                        upButton.find("img").attr("src", "img/up_green.png");
                        upButton.removeAttr("disabled");
                    },
                    function (error) {
                        console.error("UP command failed: " + error);
                        displayErrorMessage("UP command failed");
                    });
            }

            // Disable the button for now.
            upButton.find("img").attr("src", "img/up.png");
            upButton.attr("disabled", "disabled");
        });

        var photoButton = $(getidselect("photoButton"));
        photoButton.click(function () {

            console.log("IMAGE");
            if ($(this).attr("disabled") == undefined) {

                //$("#hdpic").attr("src", "img/image_placeholder.png");
                $("#hdpic").attr("src", "");
                $("#photoModal").modal();

                Weblab.sendCommand("IMAGE",
                    function (data) {
                        $(this).removeAttr("disabled");
                        $("#hdpic").attr("src", "data:image/jpg;base64," + data);
                        $(this).find("img").attr("src", "img/photo_green.png");
                    },
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

                Weblab.dbgSetOfflineSendCommandResponse(fakeData);

                Weblab.sendCommand("PLOT",
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
                    },
                    function (error) {
                        console.error("Error: " + error);
                        displayErrorMessage("PLOT command failed");
                    });
            }

            // Disable the button for now.
            $(this).find("img").attr("src", "img/plot.png");
            $(this).attr("disabled", "disabled");
        });

    } //! End-of initializeInstance()


}; //! End-of ArchimedesInstance
