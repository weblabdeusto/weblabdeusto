
angular
    .module("hwboard")
    .factory("advise", AdviseFactory);


function AdviseFactory() {

    // -----------
    // Initialization
    // -----------



    // -------------
    // Declare the API
    // -------------
    return {
        eval: eval
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
                message: "The file you have uploaded has an unrecognized termination (does not seem to be a VHDL or a BITSTREAM file). Please, ensure that you are uploading the right file. If you are indeed uploading the right one, ensure that your file name matches its type."
            }
        }

        if(termination == "vhd") {
            var pos = content.search(/architecture/);
            if (pos == -1) {
                return {
                    result: "error",
                    message: "The file you uploaded does not seem to be a VHDL file at all. Maybe it has not been generated properly."
                }
            }

            pos = content.search(/inout/);
            if (pos == -1) {
                return {
                    result: "error",
                    message: "The file you uploaded seems to be VHDL, but it does not seem to contain the expected input output declarations. If you generated the file, make sure that you generated it to be compatible with WebLab-Deusto"
                }
            }
        }

        return {
            result: "ok"
        }
    } // !eval

} // !AdviseFactory