//! This script contains the WaterTankSimulation class.
//!


//! Notes about the Xilinx WaterTank simulation mode.
//!
//! The following FPGA board inputs/outputs are used thus:
//!
//! LEDs are used as inputs for the simulation. 
//! LED 0: RightPump on or off.
//! LED 1: LeftPump on or off.
//! 
//! Switches are used as sensor inputs and the like. Thus, the FPGA board
//! can infer the "state" of the simulation, and the user's program react
//! accordingly.
//! SWI0, SWI1, SWI2 are level sensors. They indicate the following:
//! 20%, 50%, 80%

/// The following references are for VisualStudio, so that Intellisense recognizes every library.
/// <reference path="../jslib/weblabjs.js" />
/// <reference path="../jslib/three.min.js" />
/// <reference path="../jslib/stats.min.js" />
/// <reference path="../jslib/THREEx.FullScreen.js" />
/// <reference path="../jslib/jquery-1.9.1.js" />
/// <reference path="../jslib/jquery-ui-1.10.2.custom/js/jquery-ui-1.10.2.custom.js" />

WaterTankSimulation = function () {

    this._init = function () {
        this.world = new WorldLoader();
        this.waterOutputLevel = 0.5;
        this.rightPumpLevel = 0.5;
        this.leftPumpLevel = 0.5;
        this.waterLevel = 0.5;
        this.rightPumpTemperature = 0.0;
        this.leftPumpTemperature = 0.0;

        this._loadingDeferred = $.Deferred();
    }

    this.setLeftPumpTemperature = function (temp) {
        var pump = this.world.getObject("waterpumpLeft");
        if(temp > 0.8)
            pump.material = new THREE.MeshLambertMaterial({ color: 0xFF0000, ambient: 0x00 });
        else if(temp > 0.5)
            pump.material = new THREE.MeshLambertMaterial({ color: 0xFF6600, ambient: 0x00 });
        else if (temp > 0.2)
            pump.material = new THREE.MeshLambertMaterial({ color: 0xFFFF00, ambient: 0x00 });
        else 
            pump.material = new THREE.MeshLambertMaterial({ color: 0x0000FF, ambient: 0x00 });
    }

    this.setRightPumpTemperature = function (temp) {
        var pump = this.world.getObject("waterpumpRight");
        if (temp > 0.8)
            pump.material = new THREE.MeshLambertMaterial({ color: 0xFF0000, ambient: 0x00 });
        else if (temp > 0.5)
            pump.material = new THREE.MeshLambertMaterial({ color: 0xFF6600, ambient: 0x00 });
        else if (temp > 0.2)
            pump.material = new THREE.MeshLambertMaterial({ color: 0xFFFF00, ambient: 0x00 });
        else
            pump.material = new THREE.MeshLambertMaterial({ color: 0x0000FF, ambient: 0x00 });
    }

    this.setWaterOutputLevel = function (level) {
        var wo = this.world.getObject("waterfallOut");
        this.waterOutputLevel = level;

        if (this.waterOutputLevel == 0 || this.waterLevel == 0) {
            wo.visible = false;
        } else {
            wo.scale.set(50 + 100 * level, 100, 100);
            wo.visible = true;
        }
    }

    this.setWaterLevel = function (level) {
        var water = this.world.getObject("water");
        this.waterLevel = level;

        if (this.waterLevel == 0) {
            water.visible = false;

            // Invoke this so that it can hide the output waterflow if there
            // isn't actually any water left on the deposit.
            this.setWaterOutputLevel(this.waterOutputLevel);
        } else {
            water.scale.set(.95, level, .95);
            water.visible = true;
        }

    }

    this.setRightPumpLevel = function (level) {
        var wr = this.world.getObject("waterfallRight");
        this.rightPumpLevel = level;

        if (this.rightPumpLevel == 0) {
            wr.visible = false;
        } else {
            wr.scale.set(50 + 100 * level, 100, 100);
            wr.visible = true;
        }
    }

    this.setLeftPumpLevel = function (level) {
        var wl = this.world.getObject("waterfallLeft");
        this.leftPumpLevel = level;

        if (this.leftPumpLevel == 0) {
            wl.visible = false;
        } else {
            wl.scale.set(50 + 100 * level, 100, 100);
            wl.visible = true;
        }
    }

    this.loadScene = function (scene, camera) {

        this.world.setOnLoad(function () {
            water = this.world.getObject("water");
            waterfall = this.world.getObject("waterfallRight");
            waterfall2 = this.world.getObject("waterfallLeft");
            waterfallOut = this.world.getObject("waterfallOut");


            this._animate_water(waterfall);
            this._animate_water(waterfall2);
            this._animate_water(waterfallOut);

            this._loadingDeferred.resolve();

        }.bind(this)); //! OnLoad


        this.world.load("World.js", scene);


        return this._loadingDeferred.promise();
    }



    this._animate_water = function (water) {

        new function (water, range, target_scale, increment) {
            return;
            setInterval(
                function () {

                    var currentX = water.scale.x;
                    
                    if (target_scale == undefined || currentX == target_scale) {
                        var target = Math.random(range) * range;
                        var positive = Math.floor(Math.random(2) * 2) == 1 ? true : false;

                    }

                    wfcurrent += wfinc;

                    if (wfcurrent > wftarget) {
                        wfcurrent = wftarget;
                        wfinc *= -1;

                        wftarget = 100 + Math.random(40) * 20;
                    }


                    if (wfcurrent < 0) {
                        wfcurrent = 0;
                        wfinc *= -1;

                        wftarget = 100 + Math.random(40) * 20;
                    }

                    wfscale = 100 + wfcurrent / 100.0 * wfrange;
                    //console.log("New scale: " + wfscale + " " + wfcurrent + " " + wfinc);

                    water.scale.set(wfscale, 100, 100);

                },
                    100
            );

        }(water, 5, 50, 0, 100);
    } // !_animate_water()



    this._init();

}


//! Pseudo-class to constantly update the state of the simulation, asking
//! Weblab for the state. Should not be used before the simulation has been
//! loaded.
//! 
WeblabSimulationUpdater = function ( simulation ) {

    this._init = function () {
        this._active = undefined;
        this._simulation = simulation;
        this._initialized = false
    }

    this.startUpdating = function () {
        this._active = true;
        // Not using an Interval lets us respond more appropriately to network limitations. (Several requests won't queue up when the network is slow).
        setTimeout( this._requestUpdate.bind(this), 1500 );
    }

    this._initialize_watertank = function () {
        Weblab.dbgSetOfflineSendCommandResponse("");

        if (Weblab.isExperimentActive() && Weblab.checkOnline())
            Weblab.sendCommand("VIRTUALWORLD_MODE watertank", function (msg) { this._initialized = true; }.bind(this));
    }

    this._requestUpdate = function () {
        if (!this._initialized)
            this._initialize_watertank()

        // Note: These commands are actually sent asynchronously, so the second one might actually get called before
        // the first one finishes. Shouldn't matter in this instance, however. Though it's not tidy.
        // Maybe we could consider adding Promises support to the Weblab class (though it would add a dependency on
        // jquery.

        Weblab.dbgSetOfflineSendCommandResponse("{\"water\": 0.56, \"inputs\": [0.5, 0.5], \"outputs\": [0.5]}");
        if( Weblab.isExperimentActive() && Weblab.checkOnline() )
            Weblab.sendCommand("VIRTUALWORLD_STATE", this._onStateReceived.bind(this), this._onStateReceivedError.bind(this));
    }

    this.stopUpdating = function () {
        this._active = false;
    }

    this._onStateReceived = function (state_json) {
        state = $.parseJSON(state_json);

        if ($.isEmptyObject(state))
            return;

        this._simulation.setWaterLevel(state["water"]);
        this._simulation.setLeftPumpLevel(state["inputs"][0]);
        this._simulation.setRightPumpLevel(state["inputs"][1]);
        this._simulation.setWaterOutputLevel(state["outputs"][0]);

        if( this._active )
            this.startUpdating(); // Does actually *continue* updating.
    }

    this._onStateReceivedError = function (state_json) {
        state = $.parseJSON(state_json);

        if( this._active )
            this.startUpdating(); // Does actually *continue* updating.
    }

    this._init();
}





//waterLevel = 0.01;
//waterLevelChange = 0.03;
//setTimeout(
//    function () {
//        setInterval(
//            function () {

//                elapsed = 50;

//                waterLevel += waterLevelChange;
//                if (waterLevel > 1)
//                    waterLevel = 1;
//                else if (waterLevel < 0)
//                    waterLevel = 0;

//                if (waterLevel >= 1 || waterLevel <= 0) {
//                    waterLevelChange *= -1;

//                    if (typeof (waterfall) != "undefined") {
//                        if (waterLevelChange > 0) {
//                            waterfall.scale.set(150, 100, 100);
//                            waterfall2.scale.set(150, 100, 100);
//                        }
//                        else {
//                            waterfall.scale.set(50, 100, 100);
//                            waterfall2.scale.set(50, 100, 100);
//                        }

//                    }
//                }

//                water.scale.set(.95, waterLevel, .95);

//            },
//                50
//            );
//    },
//3000
//);


//wfrange = 5;
//wfinc = 25;
//wfcurrent = 0;
//wftarget = 100;

//setTimeout(
//    function () {
//        setInterval(
//            function () {



//                wfcurrent += wfinc;

//                if (wfcurrent > wftarget) {
//                    wfcurrent = wftarget;
//                    wfinc *= -1;

//                    wftarget = 100 + Math.random(40) * 20;
//                }


//                if (wfcurrent < 0) {
//                    wfcurrent = 0;
//                    wfinc *= -1;

//                    wftarget = 100 + Math.random(40) * 20;
//                }

//                wfscale = 100 + wfcurrent / 100.0 * wfrange;
//                //console.log("New scale: " + wfscale + " " + wfcurrent + " " + wfinc);

//                waterfallOut.scale.set(wfscale, 100, 100);

//            },
//                50
//            );
//    },
//3000
//);
