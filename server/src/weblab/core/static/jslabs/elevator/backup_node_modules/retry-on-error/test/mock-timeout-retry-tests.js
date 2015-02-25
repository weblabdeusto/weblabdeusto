var retry = require('../');

var originalSetTimeout;
var firstTime = true;

exports.setUp = function (callback) {
  firstTime = true;
  originalSetTimeout = setTimeout;
  callback();
};

exports.tearDown = function (callback) {
  setTimeout = originalSetTimeout;
  callback();
};

function failOnceThenSucceed(cb) {
  if (firstTime) {
    firstTime = false;
    return cb(new Error());
  }
  cb();
}

exports['should call setTimeout with correct constant timeout'] = function (test) {
  test.expect(1);

  var constantTimeout = 123;

  setTimeout = function (f, timeout) {
    test.strictEqual(constantTimeout, timeout);
    originalSetTimeout.apply(this, arguments);
  };

  var fn = retry(failOnceThenSucceed, { timeout: constantTimeout });
  fn(test.done);
};

exports['should coerce constant timeout using maxTimeout'] = function (test) {
  test.expect(1);

  var options = {
    timeout: 75,
    maxTimeout: 50
  };

  setTimeout = function (f, timeout) {
    test.strictEqual(options.maxTimeout, timeout);
    originalSetTimeout.apply(this, arguments);
  };

  var fn = retry(failOnceThenSucceed, options);

  fn(test.done);
};

exports['should coerce variable timeout using maxTimeout'] = function (test) {
  test.expect(1);

  var staticTimeout = 25;

  var options = {
    timeout: function () {
      return staticTimeout;
    },
    maxTimeout: 15
  };

  setTimeout = function (f, timeout) {
    test.strictEqual(options.maxTimeout, timeout);
    originalSetTimeout.apply(this, arguments);
  };

  var fn = retry(failOnceThenSucceed, options);

  fn(test.done);
};
