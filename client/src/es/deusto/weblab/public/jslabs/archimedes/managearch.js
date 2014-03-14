var state;
var response;
var remainingTime;


MotorUp = new function(){
    //to retrive real time parameters
    
    this.readSuccess = function(response){
        console.log(response);
    }
    this.readFailure = function(response){
        //console.log(response);
        console.log("Error going UP");
    }

    this.readParams = function(){
        //read params

        // Create a fake PARAMS response, for testing offline.
        var rand1 = Math.random() * 10;
        fakeResponse = rand1;
        //console.log(fakeResponse);
        //debugger;
        Weblab.dbgSetOfflineSendCommandResponse(fakeResponse, true);
        if (Weblab.isExperimentActive() || Weblab.checkOnline() == false)
            Weblab.sendCommand("UP", this.readSuccess, this.readFailure);

    }

}//end of up motor

MotorUp = new function(){
    //to retrive real time parameters
    
    this.readSuccess = function(response){
        console.log(response);
    }
    this.readFailure = function(response){
        //console.log(response);
        console.log("Error going DOWN");
    }

    this.readParams = function(){
        //read params

        // Create a fake PARAMS response, for testing offline.
        var rand1 = Math.random() * 10;
        fakeResponse = rand1;
        //console.log(fakeResponse);
        //debugger;
        Weblab.dbgSetOfflineSendCommandResponse(fakeResponse, true);
        if (Weblab.isExperimentActive() || Weblab.checkOnline() == false)
            Weblab.sendCommand("DOWN", this.readSuccess, this.readFailure);

    }

}//end of down motor


LoadRetriver = new function(){
    //to retrive real time parameters

    var _timeout = undefined;
    
    this.readSuccess = function(response){
        console.log(response);

        var load = parseInt(response);
        load = Math.max(0, (load - 1256) * 3.2);

        $("#load").text(load.toFixed(2) + " gr.");

    }
    this.readFailure = function(response){
        //console.log(response);
        console.log("Error retriving LOAD");
    }

    this.readParams = function(){
        //read params

        // Create a fake PARAMS response, for testing offline.
        var rand1 = Math.random() * 10;
        fakeResponse = rand1;
        //console.log(fakeResponse);
        //debugger;
        Weblab.dbgSetOfflineSendCommandResponse(fakeResponse, true);
        if (Weblab.isExperimentActive() || Weblab.checkOnline() == false)
            Weblab.sendCommand("LOAD", this.readSuccess, this.readFailure);
    }

    this.refreshParams =function(){
        //to auto refresh every 3 sec
        try{
            //try this
            this.readParams();
        }
        catch (error){
            //error
            console.log("Error Refreshing LOAD");
        }
        _timeout = setTimeout(this.refreshParams.bind(this), 3000);
    }

    this.stop = function() {
    	if(_timeout != undefined) {
    		clearTimeout(_timeout);
    		_timeout = undefined;
    	}
    }
}//end of load retrive

LevelRetriver = new function(){
    //to retrive real time parameters

    var _timeout = undefined;
    
    this.readSuccess = function(response){
        console.log(response);

        var level = parseInt(response);
        level = (1208 - level) * 7.23 + 64;

        $("#level").text(level.toFixed(2) + " inch.");

    }
    this.readFailure = function(response){
        console.log(response);
        console.log("Error retriving LEVEL");
    }

    this.readParams = function(){
        //read params

        // Create a fake PARAMS response, for testing offline.
        var rand1 = Math.random() * 10;
        fakeResponse = rand1;
        //console.log(fakeResponse);
        //debugger;
        Weblab.dbgSetOfflineSendCommandResponse(fakeResponse, true);
        if (Weblab.isExperimentActive() || Weblab.checkOnline() == false)
            Weblab.sendCommand("LEVEL", this.readSuccess, this.readFailure);
    }

    this.refreshParams =function(){
        //to auto refresh every 3 sec
        try{
            //try this
            this.readParams();
        }
        catch (error){
            //error
            console.log("Error Refreshing LEVEL");
        }
        _timeout = setTimeout(this.refreshParams.bind(this), 3000);
    }

    this.stop = function() {
    	if (_timeout != undefined) {
    		clearTimeout(_timeout);
    		_timeout = undefined;
    	}
    }
}//end of level retrive


function setTimeToGo(time){
    //timer function
    var d = new Date();
    d.setTime(d.getTime() + (time*1000));
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
    LoadRetriver.refreshParams();
	LevelRetriver.refreshParams();

    //light_page();
});

Weblab.setOnEndCallback( function() {
    hideFrame();
	console.log("[DBG]: On end interaction");
	LoadRetriver.stop();
	LevelRetriver.stop();
});

$(document).ready(function(){

    // If we are running in the WEBLAB mode and not stand-alone, we hide the frame.
    if(Weblab.checkOnline() == true)
        hideFrame();

	var refresher1 = new CameraRefresher("cam1");
	var refresher2 = new CameraRefresher("cam2");
	refresher1.start();
	refresher2.start();

    // Create the timer for later.
    timerDisplayer = new TimerDisplayer("timer");

	// Declare button handlers.
	$("#downButton").click(function() {

		console.log("DOWN");

        if($("#downButton").attr("disabled") == undefined) {
            Weblab.sendCommand("DOWN",
                function(success) {
                    $("#downButton img").attr("src", "img/down_green.png");
                    $("#downButton").removeAttr("disabled");
                },
                function(error){
                    console.error("DOWN command failed: " + error);
                    displayErrorMessage("DOWN command failed");
                });
        }

        $("#downButton img").attr("src", "img/down.png");
        $("#downButton").attr("disabled", "disabled");
	});

	$("#upButton").click(function() {
		console.log("UP");

        if($("#upButton").attr("disabled") == undefined) {
            Weblab.sendCommand("UP",
                function(success) {
                    $("#upButton img").attr("src", "img/up_green.png");
                    $("#upButton").removeAttr("disabled");
                },
                function(error){
                    console.error("UP command failed: " + error);
                    displayErrorMessage("UP command failed");
                });
        }

        // Disable the button for now.
        $("#upButton img").attr("src", "img/up.png");
        $("#upButton").attr("disabled", "disabled");
	});

    $("#photoButton").click(function() {
        console.log("IMAGE");

        if($("#photoButton").attr("disabled") == undefined) {

            //$("#hdpic").attr("src", "img/image_placeholder.png");
            $("#hdpic").attr("src", "");
            $("#photoModal").modal();

            Weblab.sendCommand("IMAGE",
                function(data) {
                    $("#photoButton").removeAttr("disabled");
                    $("#hdpic").attr("src", "data:image/jpg;base64," + data);
                    $("#photoButton img").attr("src", "img/photo_green.png");
                },
                function(error) {
                    console.error("Error: " + error);
                    displayErrorMessage("IMAGE command failed");
                });
        }

        // Disable the button for now.
        $("#photoButton img").attr("src", "img/photo.png");
        $("#photoButton").attr("disabled", "disabled");
    });

});