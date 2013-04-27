


WorldLoader = function () {
    
    this._init = function () {
        this.file = undefined;
        this.world = undefined;
        this.scene = undefined;
        this.objects = {}
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
    }

    //! Loads the objects into the scene manager.
    //! @param objs JSON object describing the objects.
    this._loadObjects = function(objs) {
        for (var i = 0; i < objs.length; i++) {
            var obj = objs[i];

            var name = obj["name"];
            var model = obj["model"];
            var scale = obj["scale"];
            var initialTranslation = obj["initialTranslation"];
            var position = obj["position"];

            this.jsonLoader.load(model, function (geometry, materials) {
                var mats = undefined;

                if (materials != undefined)
                    mats = new THREE.MeshFaceMaterial(materials);

                var mesh = new THREE.Mesh(geometry, mats);

                if(initialTranslation != undefined)
                    geometry.applyMatrix(new THREE.Matrix4().translate(new THREE.Vector3(initialTranslation[0], initialTranslation[1], initialTranslation[2])));

                if(scale != undefined)
                    mesh.scale.set(scale[0], scale[1], scale[2]);

                if(position != undefined)
                    mesh.position.set(position[0], position[1], position[2]);
                
                this.scene.add(mesh);

                this.objects[name] = mesh;
            });
        } //! for
    } //! func

    //! Returns the THREEJS Mesh for a loaded object.
    //!
    //! @param name Name of the object.
    this.getObject = function (name) {
        return this.objects[name];
    }

    this._init();

}



