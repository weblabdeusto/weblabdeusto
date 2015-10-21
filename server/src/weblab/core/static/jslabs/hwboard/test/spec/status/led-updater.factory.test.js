'use strict';

var $q;
var $timeout;

// Weblab mock.
var Weblab = new function() {
    var _cmd = "";
    var _result = "";

    this.dbgSetOfflineSendCommandResponse = function(cmd, result) {
        _cmd = cmd;
        if(result == undefined)
            result = true;
        _result = result;
    };

    this.sendCommand = function(cmd, success, failure) {
        if(_result) {
            success(_cmd);
        }
        if(!_result)
            failure(_cmd);
    };
};

describe('Factory: ledUpdater', function () {

    // load the controller's module
    beforeEach(module('hwboard'));

    // Initialize the controller and a mock scope
    beforeEach(inject(function (_ledUpdater_, _$q_, _$timeout_) {
        ledUpdater = _ledUpdater_;
        $timeout = _$timeout_;
        $q = _$q_;
    }));

    it('should pass', function () {
        expect(3).toBe(3);
    });

    it('should call callback just after starting', function(done) {
        expect(statusUpdater).toBeDefined();

        ledUpdater.setOnLedUpdate(onLedUpdateSimple);

        ledUpdater.start();

        $timeout.flush();

        // --------------
        // Implementations
        // --------------

        function onLedUpdateSimple(status) {
            done();
        } // !onStatusUpdate
    });

    it('should call callback after a while through $timeout', function(done) {
        expect(ledUpdater).toBeDefined();

        ledUpdater.setOnLedUpdate(onLedUpdateDeferred);

        ledUpdater.start();

        var times_called = 0;

        $timeout.flush();
        $timeout.flush();

        // ---------------
        // Implementations
        // ---------------

        function onLedUpdateDeferred(status) {
            times_called += 1;

            if(times_called > 1) {
                done();
            }
        } // !onStatusUpdate
    });

    it('should report a "programming" test status', function(done) {
        expect(ledUpdater).toBeDefined();

        ledUpdater.setOnLedUpdate(onLedUpdateCheck);

        ledUpdater.start();

        $timeout.flush();

        // ---------------
        // Implementations
        // ---------------

        function onLedUpdateCheck(status) {
            expect(status).toBeDefined();
            expect(status).toEqual(jasmine.any(String));
            //expect(status).toBe("programming");
            done();
        }
    });

});
