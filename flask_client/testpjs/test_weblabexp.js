// In case we want to test against the standard (deployed) Weblab server.
// As of now this MUST be false, testing against the real server is not supported.
TESTING_DEPLOYED_SERVER = false;


/**
 * Tests for WeblabExp that are to be executed from an active experiment.
 * They are executed fast because the experiment is reserved before the first test, and only finished after the last one.
 */
describe("WeblabExp Active-Experiment Tests", function () {

    // That is a valid combination for the testing database.
    var valid_account = "any";
    var valid_password = "password";

    // If we are testing against the deployed server we use a combination we know is valid.
    if (TESTING_DEPLOYED_SERVER) {
        valid_account = "demo";
        valid_password = "demo";
    }

    var reserve_result = undefined;

    // Some error-related tests depend on changes to the core URL
    var saved_core_url;

    before(function (done) {
        this.timeout(5000);
        // Login first.
        var $login = WeblabWeb._login(valid_account, valid_password);
        $login.done(function (sessionid) {
            WeblabWeb.reserve_experiment(sessionid, "ud-dummy", "Dummy experiments")
                .done(function (result) {
                    reserve_result = result;
                    weblabExp.setReservation(reserve_result.reservation_id.id);
                    done();
                })
                .fail(function (result) {
                    throw result;
                });
        });
    });

    beforeEach(function(){
        // Save the URL, in case the test will modify it.
        saved_core_url = weblabExp.CORE_URL;
    });

    afterEach(function(){
        // Restore the URL, in case the test modified it.
        weblabExp.CORE_URL = saved_core_url;
        console.log("AFTEREACH()");
        console.log("Restored to: " + saved_core_url);
    });


    // This can be an after() for the most part.
    after(function (done) {
        this.timeout(5000);

        // Finish the experiment so that we can immediately test again if we want to.
        weblabExp.finishExperiment()
            .done(function (result) {
                // The result should be an empty JSON dictionary
                should.exist(result);
                result.should.be.empty;

                done();
            })
            .fail(function (error) {
                throw error;
            });
    });


    it("should be present", function (done) {
        should.exist(WeblabWeb);
        done();
    });

    it("should have reserved", function (done) {
        should.exist(reserve_result);
        done();
    });

    it("raw _send_command should succeed", function (done) {
        weblabExp._send_command("ChangeSwitch on 1")
            .done(function (result) {
                should.exist(result);
                result.should.have.property("commandstring");

                var cmdstring = result.commandstring;

                // Checks specific to the aquariumjs experiment.
                expect(cmdstring).to.contain("Received");
                expect(cmdstring).to.contain("ChangeSwitch");

                done();
            })
            .fail(function (error) {
                console.error(error);
                throw error;
            });
    });


    // TODO: We can't test this yet.
    //    it("raw _send_command should return error if the command does not exist and is reported with is_exception=true", function (done) {


    it("sendCommand should succeed and report the output", function (done) {
        weblabExp.sendCommand("ChangeSwitch on 1")
            .done(function (response) {

                should.exist(response);


                // Checks specific to the aquariumjs experiment.
                expect(response).to.contain("Received");
                expect(response).to.contain("ChangeSwitch");

                done();
            })
            .fail(function (error) {
                console.error(error);
                throw error;
            });
    });


    it("testCommand should succeed and report the output just like the standard sendCommand", function (done) {
        weblabExp.sendCommand("ChangeSwitch on 1")
            .done(function (response) {

                should.exist(response);


                // Checks specific to the aquariumjs experiment.
                expect(response).to.contain("Received");
                expect(response).to.contain("ChangeSwitch");

                done();
            })
            .fail(function (error) {
                console.error(error);
                throw error;
            });
    });


    it("sendCommand should report error if endpoint is not reachable", function (done) {

        // Ensure that the endpoint is not reachable. This URL will be restored
        // by the afterEach handler.
        weblabExp.CORE_URL = "http://localhost/unreachable";

        weblabExp.sendCommand("ChangeSwitch on 1")
            .done(function (response) {
                // Should not be called.
                throw response;
            })
            .fail(function (error) {
                // This *should* run.
                should.exist(error);
                done();
            });
    });

    it("testCommand should report error if endpoint is not reachable", function (done) {
        // Ensure that the endpoint is not reachable. This URL will be restored
        // by the afterEach handler.
        weblabExp.CORE_URL = "http://localhost/unreachable";

        weblabExp.testCommand("ChangeSwitch on 1")
            .done(function (response) {
                // Should not be called.
                throw response;
            })
            .fail(function (error) {
                // This *should* run.
                should.exist(error);
                done();
            });
    });

    it("raw _poll should succeed (returning at least an empty dict)", function (done) {
        weblabExp._poll()
            .done(function(result){
                should.exist(result);
                result.should.be.an.object;
                result.should.be.empty;
                done();
            })
            .fail(function(error){
                throw error;
            });
    });

    it("_startPolling should not crash badly", function (done) {
        weblabExp._startPolling();
        done();
    });

}); // !describe


/**
 * Before each of those tests, a full login and experiment reserve is carried out, which means they
 * are relatively slow.
 */
describe("weblabExp Full-Process Tests", function () {

    // That is a valid combination for the testing database.
    var valid_account = "any";
    var valid_password = "password";

    // If we are testing against the deployed server we use a combination we know is valid.
    if (TESTING_DEPLOYED_SERVER) {
        valid_account = "demo";
        valid_password = "demo";
    }

    var reserve_result = undefined;

    // Some error-related tests depend on changes to the core URL
    var saved_core_url;

    // This can be a before() for the most part.
    beforeEach(function (done) {
        this.timeout(5000);
        // Login first.
        var $login = WeblabWeb._login(valid_account, valid_password);
        $login.done(function (sessionid) {
            WeblabWeb.reserve_experiment(sessionid, "ud-dummy", "Dummy experiments")
                .done(function (result) {
                    reserve_result = result;
                    weblabExp.setReservation(reserve_result.reservation_id.id);
                    done();
                })
                .fail(function (result) {
                    throw result;
                });
        });
    });

    beforeEach(function(){
        // Save the URL, in case the test will modify it.
        saved_core_url = weblabExp.CORE_URL;
    });

    afterEach(function(){
        // Restore the URL, in case the test modified it.
        weblabExp.CORE_URL = saved_core_url;
        console.log("AFTEREACH()");
        console.log("Restored to: " + saved_core_url);
    });


    // This can be an after() for the most part.
    afterEach(function (done) {
        this.timeout(5000);

        // Finish the experiment so that we can immediately test again if we want to.
        weblabExp.finishExperiment()
            .done(function (result) {
                // The result should be an empty JSON dictionary
                should.exist(result);
                result.should.be.empty;

                done();
            })
            .fail(function (error) {
                throw error;
            });
    });


    // TODO: We can't test this yet.
    // it("_startPolling should invoke poll() periodically")

    // TODO: We can't test this yet.
    // it("_startPolling invokes the finish handlers if needed")


    it("finish callbacks can be apparently registered", function (done) {
        weblabExp.onFinish(function(){
            // Callback type 1
        });

        weblabExp.onFinish()
            .done(function(){
                // Callback type 2
            });

        done();
    });

    // TODO:
    // Can't test yet. We need to re-instance WeblabExp after each test for this.

//    it("finishExperiment() invokes the finish callbacks", function (done) {
//        // Finish invoked.
//        weblabExp.onFinish()
//            .done(function(){
//                done();
//            });
//
//        weblabExp.finishExperiment();
//    });

    // TODO: We can't test this yet.
    // it("finishExperiment() invokes the finish callbacks with the right args and context")



}); // !describe