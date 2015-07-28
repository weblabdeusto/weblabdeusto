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

                    //console.log(exps_by_name);

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

    it("should support the basic _reserve request", function (done) {
        // Login first.
        var $login = WeblabWeb._login(valid_account, valid_password);
        $login.done(function (sessionid) {
            WeblabWeb._reserve_experiment(sessionid, "visir", "Visir experiments")
                .done(function (result) {
                    should.exist(result);

                    result.status.should.equal("Reservation::waiting_confirmation");
                    should.exist(result.reservation_id.id);
                    should.exist(result.url);

                    done();
                })
                .fail(function (result) {
                    throw result;
                });
        });
    }); // !it

    it("should support _get_reservation_status", function (done) {
        // Login first.
        var $login = WeblabWeb._login(valid_account, valid_password);
        $login.done(function (sessionid) {
            WeblabWeb._reserve_experiment(sessionid, "visir", "Visir experiments")
                .done(function (result) {
                    should.exist(result);
                    var reservation_id = result.reservation_id.id;

                    WeblabWeb._get_reservation_status(reservation_id)
                        .done(function (r) {
                            should.exist(r);

                            should.exist(r.status);
                            should.exist(r.reservation_id.id);
                            should.exist(r.url);

                            done();
                        })
                        .fail(function (result) {
                            throw result;
                        });

                })
                .fail(function (result) {
                    throw result;
                });
        });
    }); // !it

    it("should support the full reserve request", function (done) {
        this.timeout(5000);
        // Login first.
        var $login = WeblabWeb._login(valid_account, valid_password);
        $login.done(function (sessionid) {
            WeblabWeb.reserve_experiment(sessionid, "robot-standard", "Robot experiments")
                .done(function (reservationid, time, initialConfig, result) {

                    reservationid.should.be.a("string");

                    time.should.be.above(190);
                    time.should.be.below(210);

                    var conf = JSON.parse(initialConfig);
                    conf.webcam.should.contain("robot");
                    result.should.be.an("object");

                    result.status.should.equal("Reservation::confirmed");
                    should.exist(result.url);
                    should.exist(result.initial_configuration);
                    should.exist(result.time);
                    result.time.should.be.above(190);
                    result.time.should.be.below(210);

                    done();
                })
                .progress(function(status, position, result){
                    console.log("In progress: " + status);
                })
                .fail(function (result) {
                    throw result;
                });
        });
    }); // !it


    it("reserve_experiment should report queue position", function (done) {
        this.timeout(15000);
        // Login first.
        var $login = WeblabWeb._login(valid_account, valid_password);
        $login.done(function (sessionid) {

            WeblabWeb.reserve_experiment(sessionid, "robotarm", "Robot experiments")
                .progress(function (status, position, result) {
                    console.log("PROGRESS 1: " + status);
                })
                .fail(function (error) {
                    throw error;
                })
                .done(function (reservationid, time, initialConfig, result) {

                    console.log("R1.DONE");

                    WeblabWeb.reserve_experiment(sessionid, "robotarm", "Robot experiments")
                        .done(function (reservationid, time, initialConfig, result) {
                            // TODO: Make tests independent.
                            // throw "Second reserve shouldn't succeed";
                            console.log("R2.DONE");
                        })
                        .progress(function (status, position, result) {
                            console.log("PROG 3 " + status + " | " + position);
                            should.exist(status);
                            should.exist(result);
                            if(status === "Reservation::waiting") {
                                position.should.equal(0);
                                done();
                            }
                        })
                        .fail(function (result) {
                            throw result;
                        }); //! Second reserve done
                }); //! First reserve done

        }); //! login.done
    }); // !it


}); // !describe