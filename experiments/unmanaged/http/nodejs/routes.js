//! This file contains the routes for the standard API.
//! Remember that except for the first part, which generally will be the app name, the
//! APIs must conform to the specification so that Weblab can call them.
//!
//! These routes depend on the Express framework.

module.exports = function(app) {
    var weblab = require("./controllers/weblab");
    app.get("/sample/weblab/sessions/", weblab.start);
    app.get("/lab/:sessionid", weblab.index);
    app.get("/sample/weblab/sessions/:sessionid/status", weblab.status);
    app.post("/sample/weblab/sessions/:sessionid", weblab.dispose);
};