var appcomposer = new (function () {
    var self = this;

    this.config_retrieval = null;
    this.initializer = null;
    this.labmanager_retrieval = null;

    this._processMessages = function(e) {
        if(new String(e.data) == "get-configuration") {
            if (self.config_retrieval != null) {
                var config = self.config_retrieval();
                var configString = JSON.stringify(config);
                window.parent.postMessage("lab-configuration::" + configString, '*');
            }
        } else if(new String(e.data).indexOf("initializer::") == 0) {
            var initialConfiguration = new String(e.data).substr("initializer::".length);
            if (self.initializer != null) {
                var initialConfigObj = JSON.parse(initialConfiguration);
                self.initializer(initialConfigObj);
            }
        }
    }

    window.addEventListener('message', this._processMessages, false);

    this.registerConfigRetrieval = function(func) {
        self.config_retrieval = func;
    }
    this.registerInitializer = function(func) {
        self.initializer = func;
    }
    this.registerLabmanagerRetrieval = function(func) {
        self.labmanager_retrieval = func;
    }


    if (appcomposer_config != undefined) {
        for (var i=0; i<appcomposer_config.length; i++) {
            var tag_name = appcomposer_config[i][0];
            var value = appcomposer_config[i][1];
            if (tag_name == 'get_view') {
                this.registerConfigRetrieval(value);
            } else if (tag_name == 'initializer') {
                this.registerInitializer(value);
            } else if (tag_name == 'labmanager_retrieval') {
                this.registerLabmanagerRetrieval(value);
            }
        }
    }

    window.parent.postMessage("request-initialization", "*");
    if (this.labmanager_retrieval != null) {
        var labmanager_config = this.labmanager_retrieval();
        var message = "labmanager::" + JSON.stringify(labmanager_config);
        window.parent.postMessage(message, "*");
    }
});
