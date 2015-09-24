var state;
var response;
var remainingTime;



BulbManage = new function(){
    //to manage all referent to incubator Bulb
    

    
    this.readSuccess = function(response){
        //success
        //console.log(response);
        state = response.split("=");
        //console.log(state[1]);
        //debugger;
        if(state[1] == 0){
            $("#bulb").attr("src","../img/bulb_off.png");
        }
        else if (state[1] == 1){
            $("#bulb").attr("src","../img/bulb_on.png");
        }else {
            console.log("Error");
        }

    }

    this.readFailure = function(response){
        console.log('Error reading the state of Bulb');
    }

    this.stateBulb = function (){
        //to get the state of bulb
        
        // Create a fake BULB response, for testing offline.
        var rand = Math.floor(Math.random() * 2);
        fakeResponse = "BULB_STATUS=" + rand;
        //console.log(fakeResponse);

        Weblab.dbgSetOfflineSendCommandResponse(fakeResponse, true);

        if (Weblab.isExperimentActive() || Weblab.checkOnline() == false)
            Weblab.sendCommand("READ_BULB", this.readSuccess, this.readFailure);

    }

    this.chgstateBulb = function (){
        //to get the state of bulb
        
        // Create a fake BULB response, for testing offline.
        var rand = Math.floor(Math.random() * 2);
        fakeResponse = "BULB_STATUS=" + rand;
        //console.log(fakeResponse);

        Weblab.dbgSetOfflineSendCommandResponse(fakeResponse, true);

        if (Weblab.isExperimentActive() || Weblab.checkOnline() == false)
            Weblab.sendCommand("CHANGE_BULB", this.readSuccess, this.readFailure);

    }

    
    this.refreshBulb =function(){
        //to auto refresh every 3 sec
        try{
            //try this
            this.stateBulb();
        }
        catch (error){
            //error
            console.log("Error refreshing BULB statatus");
        }
        setTimeout(this.refreshBulb.bind(this), 3000);
    }
}//END BULB Manager

ParamsRetriver = new function(){
    //to retrive real time parameters
    var temperature;
    var humidity;

    
    this.readSuccess = function(response){
        //console.log(response);
        var params1 = response.split("=");
        var params = params1[1].split("&");
        temperature = params[0];
        humidity = params[1];
        
        $("#temperature").text(temperature + "°C");
        $("#humidity").text(humidity + "%");

        //console.log(temperature);
        //console.log(humidity);

    }
    this.readFailure = function(response){
        //console.log(response);
        console.log("Error retriving parameters");
    }

    this.readParams = function(){
        //read params

        // Create a fake PARAMS response, for testing offline.
        var rand1 = Math.random() * 10;
        var rand2 = Math.floor(Math.random()*10);
        fakeResponse = "PARAMS_NOW=" + rand1 + "&" + rand2;
        //console.log(fakeResponse);
        //debugger;
        Weblab.dbgSetOfflineSendCommandResponse(fakeResponse, true);
        if (Weblab.isExperimentActive() || Weblab.checkOnline() == false)
            Weblab.sendCommand("PARAMS_CHECK", this.readSuccess, this.readFailure);


    }

    this.refreshParams =function(){
        //to auto refresh every 3 sec
        try{
            //try this
            this.readParams();
        }
        catch (error){
            //error
            console.log("Error Refreshing Parameters");
        }
        setTimeout(this.refreshParams.bind(this), 3000);
    }

}//END PARAMS Retriver

function setTimeToGo(time){
    //timer function
    var d = new Date();
    d.setTime(d.getTime() + (time*1000));
    $('#timer').tinyTimer({ to: d });
}



Weblab.setOnTimeCallback(function (time) {
    console.log("[DBG]: Time left: " + time);
    setTimeToGo(time);
});

Weblab.setOnStartInteractionCallback(function () {
    console.log("[DBG]: On start interaction");
    BulbManage.refreshBulb();
    ParamsRetriver.refreshParams();
    light_page();
});

    


$(document).ready(function(){
    //dim_page();

    rc = new RefreshingCameraWidget("video", "https://cams.weblab.deusto.es/webcam/proxied.py/incubator1");
    rc.startRefreshing();


    //when user click on the bulb
    $("#bulb").click(function(){
        BulbManage.chgstateBulb();
    });

    //parameters
    $("#hish").click(function(){
        $(this).attr("src","../img/add.png"),
        $("#meas").slideUp(1000);
    });

    $("#hish").dblclick(function(){
        $(this).attr("src","../img/subtract.png");
        $("#meas").slideDown(1000);
    });

    //cameras
    $("#hosh").click(function(){
        $(this).attr("src","../img/add.png"),
        $("#cams").slideUp(1000);
    });

    $("#hosh").dblclick(function(){
        $(this).attr("src","../img/subtract.png");
        $("#cams").slideDown(1000);
    });

    $( "#hish" ).trigger( "click" );
    $( "#hosh" ).trigger( "click" );

    $("#cam1").click(function(){
        rc.changeImg("video", "https://cams.weblab.deusto.es/webcam/proxied.py/incubator1");
        $("#video").attr("src","https://cams.weblab.deusto.es/webcam/proxied.py/incubator1");

    });
    $("#cam1").click(function(){
        rc.changeImg("video", "https://cams.weblab.deusto.es/webcam/proxied.py/incubator2");
        $("#video").attr("src","https://cams.weblab.deusto.es/webcam/proxied.py/incubator2");
    });


});
