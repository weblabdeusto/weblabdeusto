
angular
    .module("elevatorApp")
    .controller("SourceEditorController", SourceEditorController);

function SourceEditorController($scope) {


    ///////////////////////////
    // SCOPE DATA
    ///////////////////////////

    // Initialize the HTML editor
    $scope.aceOptions = {
      useWrapMode : true,
      showGutter : true,
      showPrintMargin: true,
      highlightActiveLine: true,
      theme: 'chrome',
      mode: 'vhdl',
      firstLineNumber: 1,
      onLoad: aceLoaded,
      onChange: aceChanged
    };

    ////////////////////////////
    // SCOPE METHODS
    ////////////////////////////

    $scope.alert = alertimpl;

    ////////////////////////////
    // IMPLEMENTATIONS
    ////////////////////////////

    function aceLoaded (editor) {
        $scope._editor = editor;
        editor.setOptions({fontSize: '12pt'});
    }

    function aceChanged (editor) {
    }

    function alertimpl( msg ) {
        alert(msg);
    }

} // !SourceEditorController
