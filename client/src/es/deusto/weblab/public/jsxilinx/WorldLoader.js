/// The following references are for VisualStudio, so that Intellisense recognizes every library.
/// <reference path="../jslib/weblabjs.js" />
/// <reference path="../jslib/three.min.js" />
/// <reference path="../jslib/stats.min.js" />
/// <reference path="../jslib/THREEx.FullScreen.js" />
/// <reference path="../jslib/jquery-1.9.1.js" />
/// <reference path="../jslib/jquery-ui-1.10.2.custom/js/jquery-ui-1.10.2.custom.js" />


var rotWorldMatrix;
function rotateAroundWorldAxis(object, axis, radians) {

    var rotationMatrix = new THREE.Matrix4();

    rotationMatrix.makeRotationAxis(axis.normalize(), radians);
    rotationMatrix.multiply(object.matrix);                       // pre-multiply
    object.matrix = rotationMatrix;
    object.rotation.setEulerFromRotationMatrix(object.matrix);
}



WorldLoader = function () {
    
    this._init = function () {
        this.file = undefined;
        this.world = undefined;
        this.scene = undefined;
        this.objects = {};
        this.pointlights = {};
        this.ambientlight = undefined;
        this.jsonLoader = new THREE.JSONLoader();
    }


    //! Loads the World.
    //!
    //! @param file URL of the JSON file that describes the World
    //! @param scene THREE JS scene manager unto which to load the World
    this.load = function (file, scene) {

        this.file = file;
        this.scene = scene;

        $.getJSON("World.js",
            function (json) {
                this._onWorldFileLoaded(json);
            }.bind(this))
            .fail(function (jqxhr, textStatus, error) {
                var err = textStatus + ', ' + error;
                console.log("[WorldLoader] Request Failed: " + err);
        });

    }

    this._onWorldFileLoaded = function (json) {
        this.world = json;

        var objs = this.world["objects"];
        if (objs != undefined) {
            this._loadObjects(objs);
        }

        var pointlights = this.world["pointlights"];
        if (pointlights != undefined) {
            this._loadPointlights(pointlights);
        }

        var ambientlight = this.world["ambientlight"];
        if (ambientlight != undefined) {
            this._loadAmbientlight(ambientlight);
        }
    }

    //! Loads the objects into the scene manager.
    //! @param objs JSON object describing the objects.
    this._loadObjects = function (objs) {

        for (var i = 0; i < objs.length; i++) {
            var obj = objs[i];

            var model = obj["model"];
            var enabled = obj["enabled"];

            if (enabled != undefined && !enabled)
                return;

            this.jsonLoader.load(model, function (obj, geometry, materials) {

                var mats = undefined;

                var name = obj["name"];
                var scale = obj["scale"];
                var initialTranslation = obj["initialTranslation"];
                var position = obj["position"];
                var rotations = obj["rotations"];

                var ignoreMaterials = obj["ignoreMaterials"];
                if(ignoreMaterials == undefined)
                    ignoreMaterials = false;

                if (materials != undefined && !ignoreMaterials)
                    mats = new THREE.MeshFaceMaterial(materials);
                else
                    mats = new THREE.MeshBasicMaterial({ color: 0xFF00FF });

                var mesh = new THREE.Mesh(geometry, mats);

                if(initialTranslation != undefined)
                    geometry.applyMatrix(new THREE.Matrix4().translate(new THREE.Vector3(initialTranslation[0], initialTranslation[1], initialTranslation[2])));

                if(scale != undefined)
                    mesh.scale.set(scale[0], scale[1], scale[2]);

                if(position != undefined)
                    mesh.position.set(position[0], position[1], position[2]);

                if (rotations != undefined) {
                    for (var i = 0; i < rotations.length; i++) {
                        var rot = rotations[i];
                        var axis = rot["axis"];

                        var deg = rot["deg"];
                        var rad = rot["rad"];

                        var realrad = undefined;

                        if (deg != undefined)
                            realrad = deg * Math.PI / 180;

                        if (rad != undefined)
                            realrad = rad;

                        if (realrad == undefined) {
                            console.error("[WorldLoader]: Invalid rotation");
                            break;
                        }

                        var realaxis = new THREE.Vector3(axis[0], axis[1], axis[2]);

                        rotateAroundWorldAxis(mesh, realaxis, realrad);
                    }
                }

                this.scene.add(mesh);

                this.objects[name] = mesh;
            }.bind(this, obj));
        } //! for
    } //! func


    //! Loads the pointlights into the scene manager.
    //! @param pointlights JSON object describing the point lights.
    this._loadPointlights = function (pointlights) {
        for (var i = 0; i < pointlights.length; i++) {
            var pl = pointlights[i];
            
            var enabled = pl["enabled"];
            if (enabled != undefined && !enabled)
                return;

            var name = pl["name"];
            var color = parseInt(pl["color"]);
            var pos = pl["position"];

            var light = new THREE.PointLight(color);
            
            this.scene.add(light);

            this.pointlights[name] = light;
        }
    }

    //! Loads the ambientlight into the scene manager.
    //! @param ambientlight JSON object describing the ambientlight.
    this._loadAmbientlight = function (ambientlight) {
        this.ambientlight = new THREE.AmbientLight(parseInt(ambientlight["color"]));
        this.scene.add(this.ambientlight);
    }

    //! Returns the THREEJS Mesh for a loaded object.
    //!
    //! @param name Name of the object.
    this.getObject = function (name) {
        return this.objects[name];
    }

    //! Returns the THREEJS PointLight.
    //!
    //! @param name Name of the pointlight.
    this.getPointlight = function (name) {
        return this.pointlights[name];
    }

    //! Registers an object (a THREEJS Mesh) with the specified name.
    //! This can be used to register custom objects in the WorldLoader.
    //!
    //! @param name Name of the object to register. Should be unique.
    //! @param THREEJS mesh to associate with the object.
    this.registerObject = function ( name, mesh ) {
        this.objects[name] = mesh;
    }


    this._init();

}



