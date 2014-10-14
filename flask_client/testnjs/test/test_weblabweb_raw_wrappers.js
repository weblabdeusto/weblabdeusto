///////////////////////////////////////////////
//
// WARNING: As of now, the tests here are incomplete
// and don't work at all. The approach will probably
// need to be different.
//
///////////////////////////////////////////////


var assert = require("assert");
var should = require("should");
var request = require("supertest");
var jQuery = require("jquery-deferred");
var req = require("request");

// We require a fake jQuery for the AJAX requests.
var $ = {};
$.post = function (target_url, data, func) {
    var options = {
        uri: target_url,
        method: 'POST',
        json: JSON.parse(data)
    };

    req(options, function (error, response, body) {
        if (!error && response.statusCode == 200) {
            console.log(body.id);
            func(body);
        }
        else
        {
            console.error("Failed");
        }
    });
};

//var weblabweb = require("../../flaskclient/static/weblabjs/weblabweb")(jQuery);

describe('TestSystem', function () {

    before(function (done) {
        done();
    });

    it("should just pass", function (done) {
        done();
    });

    it("should support jquery ajax", function (done) {
        $.post("http://httpbin.org/ip", "{}", function(success) {
            console.log("hai");
            console.log(success);
            done();
        });
    });

}); //! Describe TestSystem

describe('WeblabWeb Basic', function () {

    var weblabweb;

    before(function (done) {
        done();
    });

    it("should be accessible and have certain attrs", function (done) {
        //should.exist(WeblabWeb);
        //should.exist(WeblabWeb.BASE_URL);
        done();
    });

}); //! Describe TestSystem
