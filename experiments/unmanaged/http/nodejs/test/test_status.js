var assert = require("assert");
var should = require("should");
var request = require("supertest");

app = require("../sample").app;



describe('Status', function() {

    var controller = require("../controllers/weblab");

    before(function(done) {
        controller.GDATA["testid"] = {
            "username": "Test Username",
            "max_date": "2014-20-30",
            "last_poll": "",
            "back": ""
        };
        done();
    });

    it("should be reachable", function(done) {
        request(app)
            .get("/sample/weblab/sessions/nonexistingid/status")
            .end(function(err, res){
                if(err) throw err;

                res.statusCode.should.be.exactly(200);
                done();
            });
    });

    it("should report expired if session does not exist", function(done) {
        request(app)
            .get("/sample/weblab/sessions/nonexistingid/status")
            .end(function(err, res){
                if(err) throw err;

                res.statusCode.should.be.exactly(200);
                res.body.should.have.property("should_finish");
                res.body["should_finish"].should.be.exactly(-1); // Because the session shouldn't exist and should thus be somewhat expired.
                done();
            });
    });

    it("should report valid should_finish if the session exists", function(done) {
        request(app)
            .get("/sample/weblab/sessions/testid/status")
            .end(function(err, res){
                if(err) throw err;

                res.statusCode.should.be.exactly(200);
                res.body.should.have.property("should_finish");
                res.body["should_finish"].should.be.above(0); // Because the session shouldn't exist and should thus be somewhat expired.
                done();
            });
    });



}); //! Describe Status