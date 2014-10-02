



///////////////////////////////////////////////////////////////
//
// WEBLAB WEB MODULE
//
// WeblabWeb is intended to carry the basic functions required
// by the Weblab flask-based client to interact with the core
// Weblab services. Thus, this library should be able to handle
// things such as Login, Reserve or List Experiments.
//
// Interaction with the experiments themselves is BEYOND THE
// SCOPE of this module.
//
// REQUIREMENTS: jQuery
//
///////////////////////////////////////////////////////////////
WeblabWeb = new function()
{

    ///////////////////////////////////////////////////////////////
    //
    // PRIVATE ATTRIBUTES AND FUNCTIONS
    // The API uses these internally to provide an easier to use,
    // higher level API. Users of this class do not need to be
    // aware of them.
    //
    ///////////////////////////////////////////////////////////////

    var BASE_URL = "www.weblab.deusto.es/weblab";


    //! Internal send function. It will send the request to the target URL.
    //! Meant only for internal use. If an error occurs (network error, "is_exception" to true, or other) then
    //! the exception will be printed to console, and nothing else will happen (as of now).
    //!
    //! @param request: The JSON-able to send. This method will not check whether the format of the JSON-able is
    //! right or not. It is assumed it is. This should be a JSON-able object and NOT a JSON string.
    //!
    //! @return: Promise, whose .done or .fail will be invoked depending on the success of the request.
    //!
    this._send = function(targetURL, request, successHandler) {

        var promise = $.Deferred();

        if(typeof(request) !== 'object')
        {
            console.error("[_SEND]: Request parameter should be an object.");
            return;
        }

        $.post(targetURL, JSON.stringify(request), function(success) {
                // Example of a response: {"params":{"reservation_id":{"id":"2da9363c-c5c4-4905-9f22-817cbdf1e397;2da9363c-c5c4-4905-9f22-817cbdf1e397.default-route-to-server"}}, "method":"get_reservation_status"}

                // Check that the internal is_exception is set to false.
                if(success["is_exception"] === true) {

                    console.error("[ERROR][_send]: Returned exception (is_exception is true)");
                    console.error(success);

                    promise.reject(success);
                    return;
                }

                var result = success["result"];

                if(result == undefined) {
                    console.error("[ERROR][_send]: Response didn't contain the expected 'result' key.");
                    console.error(success);

                    promise.reject(success);
                    return;
                }

                // The request, whatever it contains, was apparently successful. We call the success handler.
                promise.resolve(success);
            }, "json"
        ).fail(function(fail){
                console.error("[ERROR][_send]: Could not carry out the POST request to the target URL: " + targetURL);
                console.error(fail);

                promise.reject(fail);
            });

        return promise;

    };//!_send


    //! Login to the server.
    //!
    //! @param account: Account name.
    //! @param password: Password.
    //! @return: Promise. Done will be called if success, Fail otherwise.
    this._login = function(account, password)
    {
        var promise = $.Deferred();

        this._send(BASE_URL + "/login/json",
            {
                "params": {
                    "username": account,
                    "password": password
                }
            }
        ).done(function(response){
                promise.resolve(response);
            }).fail(function(response){
                promise.reject(response);
            });

        return promise;
    };


    ///////////////////////////////////////////////////////////////
    //
    // PUBLIC INTERFACE
    // The following methods are part of the public interface of this
    // class. They can be used freely. Several of them rely on callbacks.
    // They might not work properly if they are run stand-alone, on a
    // context different than Weblab-Deusto.
    //
    ///////////////////////////////////////////////////////////////



    ///////////////////////////////////////////////////////////////
    //
    // CONSTRUCTOR
    // The following is internal code to create the object.
    //
    ///////////////////////////////////////////////////////////////



}; // !Weblab




