// In case we want to test against the standard (deployed) Weblab server.
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
            WeblabWeb.reserve_experiment(sessionid, "aquariumjs", "Aquatic experiments")
                .done(function (result) {
                    reserve_result = result;
                    done();
                })
                .fail(function (result) {
                    throw result;
                });
        });
    });

    after(function (done) {
        this.timeout(5000);

        // Finish the experiment so that we can reserve again for the next test.
        WeblabExp.setReservation(reserve_result.reservation_id.id);
        WeblabExp.finishExperiment()
            .done(function(result){

                // The result should be an empty JSON dictionary
                should.exist(result);
                result.should.be.empty;

                done();
            })
            .fail(function(error){
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

})
; // !describe