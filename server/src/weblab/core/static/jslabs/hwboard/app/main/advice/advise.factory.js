
angular
    .module("hwboard")
    .factory("advise", AdviseFactory);


function AdviseFactory($log, $filter) {

    // -----------
    // Initialization
    // -----------



    // -------------
    // Declare the API
    // -------------
    return {
        evalFile: evalFile
    }; // !return


    // -----------
    // Implementations
    // -----------

    /**
     * Evaluates the validity of a VHDL code. Returns a result object.
     * @param vhdl
     */
    function evalFile(content, name) {

        // Extract termination
        var termination = name.split('.').pop();
        if(termination != "vhd" && termination != "bit") {
            return {
                result: "error",
                message: $filter("translate")("advise.unrecognized.termination")
            }
        }

        if(termination == "vhd") {
            var pos = content.search(/architecture/);
            if (pos == -1) {
                return {
                    result: "error",
                    message: $filter("translate")("advise.no.vhdl")
                }
            }

            pos = content.search(/inout/);
            if (pos == -1) {
                return {
                    result: "error",
                    message: $filter("translate")("advise.invalid.vhdl")
                }
            }
        }

        return {
            result: "ok"
        }
    } // !eval

} // !AdviseFactory