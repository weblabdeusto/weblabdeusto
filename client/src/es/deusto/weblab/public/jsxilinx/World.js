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
                "model" : "WaterTank.js",
                "scale" : [100, 100, 100],
                "position" : [600, 0, 0]
            },
            {
                "name" : "waterfallRight",
                "model" : "waterfall.js",
                "initialTranslation" : [-0.311444, 0, 0],
                "scale": [100, 100, 100],
                "position": [700, 0, 0]
            },
            {
                "name" : "waterfallLeft",
                "model" : "waterfall.js",
                "initialTranslation" : [-0.311444, 0, 0],
                "scale": [100, 100, 100],
                "position": [495, 0, 0],
                "rotations": [ { "axis" : [0, 1, 0], "deg" : 180 } ]
            },
            {
                "name" : "waterfallOut",
                "model" : "waterfall.js",
                "initialTranslation" : [-0.311444, 0, 0],
                "scale" : [100, 100, 100],
                "position" : [445, -155, 0]
            },
            {
                "name" : "waterpumpRight",
                "ignoreMaterials" : true,
                "model" : "waterpump.js",
                "scale" : [100, 100, 100],
                "position" : [720, 70, 30]
            },
            {
                "name" : "waterpumpLeft",
                "ignoreMaterials" : true,
                "model" : "waterpump.js",
                "scale" : [100, 100, 100],
                "position" : [470, 78, 0],
                "rotations": [ { "axis" : [0, 1, 0], "deg" : 180 } ]
            },
            {
                "name" : "pipe",
                "model" : "pipe.js",
                "scale" : [100, 100, 100],
                "position": [470, -80, 0]
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
    }

}