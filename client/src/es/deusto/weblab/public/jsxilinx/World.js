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
            "name" : "waterfall1",
            "enabled" : false,
            "model" : "waterfall.js",
            "initialTranslation" : [-0.311444, 0, 0],
            "scale": [100, 100, 100],
            "position": [700, 0, 0]
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