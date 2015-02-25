var retry = require('../');

var executionCount;

exports.setUp = function (callback) {
  executionCount = 0;
  callback();
};

/**
 * falible function for unit tests
 *
 * @param {number} successfulExecution the number of the execution to
 * return successfully on.
 * @param {callback} cb
 */
function errorsUntil(successfulExecution, cb) {
  executionCount += 1;

  if (executionCount === successfulExecution) {
    return cb(null, executionCount);
  }

  return cb(
    new Error('Execution: ' + executionCount)
  );
}

function alwaysSuccessful(cb) {
  executionCount += 1;
  process.nextTick(function() {
    cb(null);
  });
}

function alwaysError(cb) {
  executionCount += 1;
  process.nextTick(function() {
    cb(new Error('Execution: ' + executionCount));
  });
}

function linearBackoff(factor) {
  return function (attempt) {
    return factor * attempt;
  };
}

/**
 * noop - async no operation, just calls callback on next tick
 *
 */
function noop(cb) {
  process.nextTick(cb);
}

exports['should throw error when maxTimeout < minTimeout'] = function (test) {
  test.expect();

  test.throws(function() {
    retry(noop, {minTimeout: 200, maxTimeout: 100});
  });

  test.done();
};

exports['should throw error when maxAttempts is negative'] = function (test) {
  test.expect();

  test.throws(function() {
    retry(noop, {maxAttempts: -10});
  });

  test.done();
};

exports['should accept number as static timeout'] = function (test) {
  test.expect(1);
  var successfulExecution = 2;

  var fn = retry(errorsUntil, {timeout: 100});

  fn(successfulExecution, function(error, execution) {
    test.strictEqual(successfulExecution, execution);
    test.done();
  });
};

exports['should accept function as variable timeout'] = function (test) {
  test.expect(1);
  var successfulExecution = 2;

  function myTimeout (attempts) {
    return attempts * 5;
  }

  var fn = retry(errorsUntil, {timeout: myTimeout});

  fn(successfulExecution, function(error, execution) {
    test.strictEqual(successfulExecution, execution);
    test.done();
  });
};

exports['should throw error when timeout is negative number'] = function (test) {
  test.expect();

  test.throws(function() {
    retry(noop, {timeout: -1000});
  });

  test.done();
};

exports['should not retry if first attempt succeeds'] = function (test) {
  test.expect(2);

  var fn = retry(alwaysSuccessful);

  fn(function (error) {
    test.ifError(error);
    test.strictEqual(1, executionCount);
    test.done();
  });
};

exports['should callback with success after error'] = function (test) {
  test.expect(1);
  var successfulExecution = 2;

  var fn = retry(errorsUntil);

  fn(successfulExecution, function(error, execution) {
    test.strictEqual(successfulExecution, execution);
    test.done();
  });
};

exports['should callback with last error after max retries all error'] = function (test) {
  test.expect(2);

  var fn = retry(alwaysError, { maxAttempts: 3 });

  fn(function(error, times) {
    test.ok(error);
    test.strictEqual('Execution: 3', error.message);
    test.done();
  });
};

exports['should allow custom accept function'] = function (test) {
  test.expect(1);

  var responses = ['bar', 'foo'];
  function fooThenBar(cb) {
    cb(null, responses.pop());
  }

  var fn = retry(fooThenBar, {
    accept: function (error, result) {
      return result === 'bar';
    }
  });

  fn(function(error, result) {
    test.strictEqual('bar', result);
    test.done();
  });
};
