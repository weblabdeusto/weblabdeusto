'use strict'

###*
 # @ngdoc function
 # @name dashboardappApp.controller:MainCtrl
 # @description
 # # MainCtrl
 # Controller of the dashboardappApp
###
angular.module('dashboardappApp')
  .controller 'MainCtrl', ($scope) ->
    $scope.awesomeThings = [
      'HTML5 Boilerplate'
      'AngularJS'
      'Karma'
    ]

    $scope.components =
      archimedes1:
        webcamtest1:
          text: "First webcam is working"
          status: "OK"
          date: "2015-02-23"
          task_state: "finished"
      fpga:
        whatever:
          text: "First webcam is working"
          status: "OK"
          date: "2015-02-23"
          task_state: "finished"

