var assert = require("assert");
var should = require("should");
var request = require("supertest");

app = require("../sample").app;



describe('Create', function() {

    before(function(done) {
        done();
    });

    it("should be reachable", function(done) {
        request(app)
            .post("/sample/weblab/sessions/")
            .send({})
            .end(function(err, res){
                if(err) throw err;

                res.statusCode.should.not.be.exactly(404);
                res.statusCode.should.be.exactly(400);
                done();
            });
    });

    var client_initial_data = {
        "back": "http://localhost"
    };

    var server_initial_data = {
        "request.locale": "",
        "request.experiment_id.experiment_name": "http",
        "request.experiment_id.category_name": "HTTP experiments",
        "priority.queue.slot.initialization_in_accounting": true,
        "priority.queue.slot.start": "2014-10-03 16:54:02.394173",
        "priority.queue.slot.length": "200.0",
        "request.username": "any",
        "request.full_name": "any"
    };

    var data = {
        "back": "http://localhost",
        "client_initial_data": JSON.stringify(client_initial_data),
        "server_initial_data": JSON.stringify(server_initial_data)
    };

    it("should create a new session and return its session_id", function(done) {
        request(app)
            .post("/sample/weblab/sessions/")
            .send(data)
            .expect("Content-Type", "application/json; charset=utf-8")
            .end(function(err, res){
                if(err) throw err;

                res.statusCode.should.not.be.exactly(404);

                res.body.should.have.property("url");
                res.body.should.have.property("session_id");

                var sessionid = res.body["session_id"];

                sessionid.should.be.type("string");

                var controller = require("../controllers/weblab");
                controller.GDATA[sessionid].should.be.type("object");

                done();
            });
    });

    it("should create a new session with expiry information", function(done) {
        request(app)
            .post("/sample/weblab/sessions/")
            .send(data)
            .expect("Content-Type", "application/json; charset=utf-8")
            .end(function(err, res){
                if(err) throw err;

                var controller = require("../controllers/weblab");
                var session = controller.GDATA[res.body.session_id];

                should.exist(session);

                session.max_date.should.be.an.instanceOf(Date);
                session.max_date.getTime().should.be.below((new Date()).getTime()); // Because it's an old expired date.

                done();
            });
    });



}); //! Describe Create