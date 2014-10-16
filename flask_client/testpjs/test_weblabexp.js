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

    it("should be present", function (done) {
        should.exist(WeblabWeb);
        done();
    });

}); // !describe