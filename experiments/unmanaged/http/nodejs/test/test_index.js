var assert = require("assert");
var should = require("should");
var request = require("supertest");

app = require("../sample").app;



describe('Index', function() {

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


    it("should be unreachable 404 with a non-existing session", function(done) {
        request(app)
            .get("/lab/nonexistingid")
            .end(function(err, res){
                if(err) throw err;

                res.statusCode.should.be.exactly(404);
                done();
            });
    });


    it("should be reachable 200 with an existing session", function(done) {
        request(app)
            .get("/lab/testid")
            .end(function(err, res){
                if(err) throw err;

                res.statusCode.should.be.exactly(200);
                done();
            });
    });

}); //! Describe Index