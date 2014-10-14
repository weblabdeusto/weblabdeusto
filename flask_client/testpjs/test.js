
describe("DOM Test", function () {
    var el = document.createElement("div");
    el.id = "myDiv";
    el.innerHTML = "Hello World!";
    document.body.appendChild(el);
    var myEl = document.getElementById('myDiv');

    it("tests seem to work", function () {
        (myEl.innerHTML).should.equal("Hello World!");
    });
});


describe("WeblabWeb Test", function() {

    it("should be present", function(done) {
        should.exist(WeblabWeb);
        done();
    });

    it("should return a sessionid at login", function(done) {
        WeblabWeb._login("demo", "demo")
            .done(function(result){
                should.exist(result);
                result.should.be.a("string"); // Should be a sessionid
                done();
            })
            .fail(function(result){
                throw result;
            });
    });

    it("should be able to retrieve user information (get_user_information) after login", function(done) {

        // Login first.
        var $login = WeblabWeb._login("demo", "demo");
        $login.done(function(sessionid) {
            WeblabWeb._get_user_information(sessionid)
                .done(function(result) {
                    should.exist(result);
                    result.should.be.a("object");

                    // Check that result contains the kind of information we expect.
                    result.should.have.property("full_name");
                    result.should.have.property("email");
                    result.should.have.property("login");
                    result.should.have.property("admin_url");
                    result.should.have.property("role");

                    result.full_name.should.equal("Demo User");
                    result.login.should.equal("demo");
                    result.email.should.equal("weblab@deusto.es");

                    done();
                })
                .fail(function(result) {
                    throw result;
                });
        });
    });

    it("should be able to list experiments (list_experiments) after login", function(done) {
        // Login first.
        var $login = WeblabWeb._login("demo", "demo");
        $login.done(function(sessionid) {
            WeblabWeb._list_experiments(sessionid)
                .done(function(result) {
                    should.exist(result);

                    result.should.be.a("Array");

                    var exps_by_name = {};
                    // Check that it contains some of the experiments we expect.
                    for(var i = 0; i < result.length; ++i) {
                        var exp = result[i];

                        should.exist(exp.experiment.name);
                        exps_by_name[exp.experiment.name] = exp;
                    }

                    exps_by_name.should.have.property("submarine");
                    exps_by_name.should.have.property("flashdummy");
                    exps_by_name.should.have.property("visir");

                    done();
                })
                .fail(function(result) {
                    throw result;
                });
        });
    });




}); // !describe