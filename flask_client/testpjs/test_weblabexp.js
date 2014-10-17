// In case we want to test against the standard (deployed) Weblab server.
// As of now this MUST be false, testing against the real server is not supported.
TESTING_DEPLOYED_SERVER = false;

describe("WeblabExp Test", function () {

    // That is a valid combination for the testing database.
    var valid_account = "any";
    var valid_password = "password";

    // If we are testing against the deployed server we use a combination we know is valid.
    if (TESTING_DEPLOYED_SERVER) {
        valid_account = "demo";
        valid_password = "demo";
    }

    var reserve_result = undefined;

    before(function (done) {
        this.timeout(5000);
        // Login first.
        var $login = WeblabWeb._login(valid_account, valid_password);
        $login.done(function (sessionid) {
            WeblabWeb.reserve_experiment(sessionid, "ud-dummy", "Dummy experiments")
                .done(function (result) {
                    reserve_result = result;
                    WeblabExp.setReservation(reserve_result.reservation_id.id);
                    done();
                })
                .fail(function (result) {
                    throw result;
                });
        });
    });

    after(function (done) {
        this.timeout(5000);

        // Finish the experiment so that we can immediately test again if we want to.
        WeblabExp.finishExperiment()
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
        WeblabExp._send_command("ChangeSwitch on 1")
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

// NOTE: This test has been disabled because the aquariumjs experiment never returns an exception. (At least, in an easy way without really breaking it).
//       Maybe eventually we should add a test experiment to test against more thoroughly.
//
//    it("raw _send_command should return error if the command does not exist and is reported with is_exception=true", function (done) {
//        WeblabExp._send_command("ball:w")
//            .done(function (result) {
//                // This should not be called.
//                throw result;
//            })
//            .fail(function (error) {
//                console.log(error);
//                done();
//            });
//    });

    it("sendCommand should succeed and report the output", function (done) {
        WeblabExp.sendCommand("ChangeSwitch on 1")
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

})
; // !describe