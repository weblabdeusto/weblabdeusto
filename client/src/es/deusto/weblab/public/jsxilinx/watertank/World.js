{
    "metadata":
    {
        "format" : "myWorld",
        "formatVersion" : 1.0
    },

    "objects":
        [
            {
                "name" : "watertank",
                "model" : "models/watertank.js",
                "scale" : [100, 100, 100],
                "position" : [600, 0, 0]
            },
            {
                "name" : "water",
                "model" : function() { return new THREE.CylinderGeometry(95, 95, 200, 50, 50, false); },
                "initialTranslation" : [0, 100, 0],
                "scale" : [.95, .1, .95],
                "position" : [597, -95, 0],
                "material" : function() { return new THREE.MeshBasicMaterial({ color: 0x0000FF }); },
            },
            {
                "name" : "waterfallRight",
                "model" : "models/waterfall.js",
                "initialTranslation" : [-0.311444, 0, 0],
                "scale": [100, 100, 100],
                "position": [700, 0, 0],
                "material" : function() { return new THREE.MeshBasicMaterial({color:0x0000FF}); }
            },
            {
                "name" : "waterfallLeft",
                "model" : "models/waterfall.js",
                "initialTranslation" : [-0.311444, 0, 0],
                "scale": [100, 100, 100],
                "position": [495, 0, 0],
                "rotations": [ { "axis" : [0, 1, 0], "deg" : 180 } ],
                "material" : function() { return new THREE.MeshBasicMaterial({color:0x0000FF}); }
            },
            {
                "name" : "waterfallOut",
                "model" : "models/waterfall.js",
                "initialTranslation" : [-0.311444, 0, 0],
                "scale" : [100, 100, 100],
                "position" : [445, -155, 0],
                "material" : 
                    function() {
                        var watertexture = THREE.ImageUtils.loadTexture('../models/water.jpg');
                        var mat = new THREE.MeshPhongMaterial({ map: watertexture, ambient: 0.9, color: 0xAAAAFF });
                        var mats = new THREE.MeshFaceMaterial([mat]);
                        return mats;
                    }
            },
            {
                "name" : "waterpumpRight",
                "model" : "models/waterpump.js",
                "scale" : [100, 100, 100],
                "position" : [732, 78, -2],
                "material" : function() { return new THREE.MeshLambertMaterial({ color: 0x0000FF, ambient: 0x00 }); }
            },
            {
                "name" : "waterpumpLeft",
                "model" : "models/waterpump.js",
                "scale" : [100, 100, 100],
                "position" : [470, 78, 0],
                "rotations": [ { "axis" : [0, 1, 0], "deg" : 180 } ],
                "material" : function() { return new THREE.MeshLambertMaterial({ color: 0x0000FF, ambient: 0x00 }); }
            },
            {
                "name" : "pipe",
                "model" : "models/pipe.js",
                "scale" : [100, 100, 100],
                "position": [470, -80, 0]
            },
            {
                "name" : "lowMarker",
                "model" : function() { return new THREE.SphereGeometry(5, 10, 10); },
                "material" : function() { return new THREE.MeshBasicMaterial({ color: 0xFF0000 }); },
                "position" : [600, -60, 94]
            },
            {
                "name" : "mediumMarker",
                "model" : function() { return new THREE.SphereGeometry(5, 10, 10); },
                "material" : function() { return new THREE.MeshBasicMaterial({ color: 0xFF0000 }); },
                "position" : [600, 0, 94]
            },
            {
                "name" : "highMarker",
                "model" : function() { return new THREE.SphereGeometry(5, 10, 10); },
                "material" : function() { return new THREE.MeshBasicMaterial({ color: 0xFF0000 }); },
                "position" : [600, 60, 94]
            },
            {
                "name" : "lowMarkerFront",
                "model" : function() { return new THREE.SphereGeometry(5, 10, 10); },
                "material" : function() { return new THREE.MeshBasicMaterial({ color: 0xFF0000 }); },
                "position" : [600, -60, -94]
            },
            {
                "name" : "mediumMarkerFront",
                "model" : function() { return new THREE.SphereGeometry(5, 10, 10); },
                "material" : function() { return new THREE.MeshBasicMaterial({ color: 0xFF0000 }); },
                "position" : [600, 0, -94]
            },
            {
                "name" : "highMarkerFront",
                "model" : function() { return new THREE.SphereGeometry(5, 10, 10); },
                "material" : function() { return new THREE.MeshBasicMaterial({ color: 0xFF0000 }); },
                "position" : [600, 60, -94]
            }

    ],

    "pointlights":
    [
        {
            "name" : "light1",
            "position" : [10, 250, 130],
            "color": "0xFFFFFF"
        }
    ],

    "ambientlight":
    {
        "color" : "0xFFFFFF"
    },


    "onLoad" : 
        function() {
        }

}


