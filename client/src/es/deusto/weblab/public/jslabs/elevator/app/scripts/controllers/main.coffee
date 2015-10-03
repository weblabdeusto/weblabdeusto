'use strict'

###*
 # @ngdoc function
 # @name elevatorApp.controller:MainCtrl
 # @description
 # # MainCtrl
 # Controller of the elevatorApp
###
angular.module('elevatorApp')
  .controller 'MainCtrl', ($scope, RefreshState) ->

    # Create basic parameters for the whole experiment
    $scope.experiment = {}
    $scope.experiment.status = 'not_ready'

    $scope.aceEditor = {}
    $scope.aceEditor.text = ""

    # Start refreshing the state
    RefreshState.start (state) ->
      $scope.experiment.status = state


    # Get an appropriate description for the current status of the experiment.
    $scope.experiment.getStatusDescription = ->
      if $scope.experiment.status == 'not_ready'
        return "The experiment is not ready to be used. Please, send a program."
      else if $scope.experiment.status == 'synthesizing'
        return "Now synthesizing the program you provided. Please, wait."
      else if $scope.experiment.status == 'programming'
        return "Now programming with the logic you provided. Please, wait."
      else if $scope.experiment.status == 'synthesizing_error'
        return "There was a problem while trying to synthesize your program. You might try with another."
      else if $scope.experiment.status == 'not_allowed'
        return "The type of program you provided is not allowed."
      else if $scope.experiment.status == 'awaiting_code'
        return "Waiting for a logic file to program into the board"
      else if $scope.experiment.status == 'failed'
        return "An error occurred. Maybe the logic you provided is not valid. Please, try something else or contact the administrators."
      else if $scope.experiment.status == 'user_time_exceeded'
        return "Sorry, you exceeded the allocated time."
      else if $scope.experiment.status == 'ready'
        return "The system is ready. Your logic is running on the equipment."
      else
        return "The experiment is in an unknown state. It may not work as expected."

    # Get the appropriate alert class for the current status of the experiment.
    $scope.experiment.getStatusClass = ->
      if $scope.experiment.status == 'not_ready'
        return "alert-info"
      else if $scope.experiment.status == 'synthesizing'
        return "alert-info"
      else if $scope.experiment.status == 'programming'
        return "alert-info"
      else if $scope.experiment.status == 'synthesizing_error'
        return "alert-danger"
      else if $scope.experiment.status == 'not_allowed'
        return "alert-danger"
      else if $scope.experiment.status == 'awaiting_code'
        return "alert-info"
      else if $scope.experiment.status == 'failed'
        return "alert-danger"
      else if $scope.experiment.status == 'user_time_exceeded'
        return "alert-warning"
      else if $scope.experiment.status == 'ready'
        return "alert-success"
      else
        return "alert-danger"


    $scope.shouldShowStatus = ->
      return $scope.experiment.status == 'programming'

    $scope.doTest = ->
      return Math.random() * 2 < 1;


    ###################
    # IMPLEMENTATIONS #
    ###################

