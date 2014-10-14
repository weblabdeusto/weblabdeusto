// In case we want to test against the standard (deployed) Weblab server.
TESTING_DEPLOYED_SERVER = false;

describe("WeblabWeb Test", function () {

    // That is a valid combination for the testing database.
    var valid_account = "any";
    var valid_password = "password";

    // If we are testing against the deployed server we use a combination we know is valid.
    if (TESTING_DEPLOYED_SERVER) {
        valid_account = "demo";
        valid_password = "demo";
    }

    it("should be present", function (done) {
        should.exist(WeblabWeb);
        done();
    });

    it("should return a sessionid at login", function (done) {

        WeblabWeb._login(valid_account, valid_password)
            .done(function (result) {
                should.exist(result);
                result.should.be.a("string"); // Should be a sessionid
                done();
            })
            .fail(function (result) {
                throw result;
            });
    });

    it("login with wrong password should be reported as failed", function (done) {
        this.timeout(20000);
        WeblabWeb._login("wronguser", "wrongpassword")
            .done(function (result) {
                throw "Should not be called";
            })
            .fail(function (result) {
                // In this case the error should be an invalid credentials one.
                result.code.should.equal("JSON:Client.InvalidCredentials")
                done();
            });
    });

    it("should be able to retrieve user information (get_user_information) after login", function (done) {

        // Login first.
        var $login = WeblabWeb._login(valid_account, valid_password);
        $login.done(function (sessionid) {
            WeblabWeb._get_user_information(sessionid)
                .done(function (result) {
                    should.exist(result);
                    result.should.be.a("object");

                    // Check that result contains the kind of information we expect.
                    result.should.have.property("full_name");
                    result.should.have.property("email");
                    result.should.have.property("login");
                    result.should.have.property("admin_url");
                    result.should.have.property("role");

                    if (TESTING_DEPLOYED_SERVER) {
                        result.full_name.should.equal("Demo User");
                        result.login.should.equal("demo");
                        result.email.should.equal("weblab@deusto.es");
                    }
                    else {
                        result.full_name.should.equal("Name of any");
                        result.login.should.equal("any");
                        result.email.should.equal("weblab@deusto.es");
                    }

                    done();
                })
                .fail(function (result) {
                    throw result;
                });
        });
    });

    it("should be able to list experiments (list_experiments) after login", function (done) {
        // Login first.
        var $login = WeblabWeb._login(valid_account, valid_password);
        $login.done(function (sessionid) {
            WeblabWeb._list_experiments(sessionid)
                .done(function (result) {
                    should.exist(result);

                    result.should.be.a("Array");

                    var exps_by_name = {};
                    // Check that it contains some of the experiments we expect.
                    for (var i = 0; i < result.length; ++i) {
                        var exp = result[i];

                        should.exist(exp.experiment.name);
                        exps_by_name[exp.experiment.name] = exp;
                    }

                    exps_by_name.should.have.property("submarine");
                    exps_by_name.should.have.property("robot-standard");
                    exps_by_name.should.have.property("visir");

                    done();
                })
                .fail(function (result) {
                    throw result;
                });
        });
    });


}); // !describe