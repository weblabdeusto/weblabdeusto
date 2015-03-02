'use strict'

###*
 # @ngdoc directive
 # @name elevatorApp.directive:wlUpload
 # @description
 # # Upload file directive for WebLab.
 # # Relies on: https://github.com/danialfarid/angular-file-upload
 # # In Weblab official page upload is done to: https://weblab.deusto.es/weblab/web/upload/
###
angular.module('elevatorApp')
  .directive('wlUpload', ($upload) ->
    templateUrl: 'views/wlupload.html',
    restrict: 'E'
    link: (scope, element, attrs) ->
      scope.$watch "files", ->
        if scope.files == undefined
          return
        console.log "WATCH HAS: "
        console.log scope.files

        scope.upload = $upload.upload(
          url: '../../../../../web/upload/'
          data: {
          },
          fields: {
            file_info: "vhd"
          },
          file: scope.files
        ).progress( (evt) ->
          console.log "Progress: " + parseInt(100.0 * evt.loaded / evt.total) + '% file : ' + evt.config.file.name
        ).success( (data, status, headers, config) ->
          console.log 'file ' + config.file.name + ' is uploaded successfully. Response: ' + data
        ).error( ->
          console.error("Could not upload the file");
        )
  )
