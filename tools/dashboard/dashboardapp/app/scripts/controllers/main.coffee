'use strict'

###*
 # @ngdoc function
 # @name dashboardappApp.controller:MainCtrl
 # @description
 # # MainCtrl
 # Controller of the dashboardappApp
###
angular.module('dashboardappApp')
  .controller 'MainCtrl', ['$scope', '$resource', ($scope, $resource) ->
    $scope.awesomeThings = [
      'HTML5 Boilerplate'
      'AngularJS'
      'Karma'
    ]

    Components = $resource('../status')
    $scope.components = Components.get ( (data) ->
      console.log "[/status]: Components obtained."
    ), ( ->
      console.error "[/status]: Error obtaining components: Trying test URL."

      Components = $resource('http://localhost:5000/status')
      $scope.components = Components.get ( (data) ->
        console.log "[/status]: Components obtained (from localhost server)"
      ), ( ->
        console.error "[/status]: Error obtaining components from localhost."
      )
    )

#    $scope.components =
#    archimedes1:
#      webcamtest1:
#        text: "First webcam is working"
#        status: "OK"
#        date: "2015-02-23"
#        task_state: "finished"
#    fpga:
#      whatever:
#        text: "First webcam is working"
#        status: "OK"
#        date: "2015-02-23"
#        task_state: "finished"


  ]

