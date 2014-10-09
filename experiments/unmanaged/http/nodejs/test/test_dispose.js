var assert = require("assert");
var should = require("should");
var request = require("supertest");

app = require("../sample").app;



describe('Dispose', function() {

    before(function(done) {
        done();
    });

    it("should return 'unknown op' when called without the delete action", function(done) {
        request(app)
            .post("/sample/weblab/sessions/invalidid")
            .end(function(err, res){
                if(err) throw err;

                res.statusCode.should.be.exactly(200);
                res.text.should.be.exactly("unknown op");
                done();
            });
    });

    it("should return 'not found' when called with the delete action but when the session does not exist", function(done){
        request(app)
            .post("/sample/weblab/sessions/invalidid")
            .send({"action": "delete"})
            .end(function(err, res) {
                if(err) throw err;

                res.statusCode.should.be.exactly(200);
                res.text.should.be.exactly("not found");
                done();
            })
    });

    it("should return 'deleted' when called with a valid, existing session", function(done){

        var controller = require("../controllers/weblab");
        controller.GDATA["testid"] = {
            "username": "Test Username",
            "max_date": "2014-20-30",
            "last_poll": "",
            "back": ""
        };

        request(app)
            .post("/sample/weblab/sessions/testid")
            .send({"action": "delete"})
            .end(function(err, res) {
                if(err) throw err;

                res.statusCode.should.be.exactly(200);
                res.text.should.be.exactly("deleted");
                done();
            });
    });


    it("deleted sessions should be moved to the EXPIRED dictionary", function(done){

        var controller = require("../controllers/weblab");
        controller.GDATA["testid"] = {
            "username": "Test Username",
            "max_date": "2014-20-30",
            "last_poll": "",
            "back": ""
        };

        request(app)
            .post("/sample/weblab/sessions/testid")
            .send({"action": "delete"})
            .end(function(err, res) {
                if(err) throw err;

                res.statusCode.should.be.exactly(200);
                res.text.should.be.exactly("deleted");

                should.not.exist(controller.GDATA["testid"]);
                should.exist(controller.GEXPIRED["testid"]);

                done();
            });
    });

}); //! Describe dispose