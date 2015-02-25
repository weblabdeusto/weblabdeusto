'use strict'

###*
 # @ngdoc service
 # @name elevatorApp.RefreshState
 # @description
 # # RefreshState
 # Service in the elevatorApp.
###
angular.module('elevatorApp')
  .service 'RefreshState', ['$timeout', '$rootScope', class RefreshState

    # Constructs the RefreshState object.
    constructor: (@$timeout, @$rootScope) ->
      console.log "ctor"
      @shouldStop = false;
      @_timeout = undefined;

    # Starts checking the state through repeated commands.
    start: (update) =>
      @shouldStop = false;
      @update = update;

      console.log "[STARTING REFRESHSTATE]"
      console.log Weblab

      @_check()

    # Checks the state and initiates the timeouts for further requests.
    _check: =>
      @$timeout ( =>

        # Set a random state for debugging purposes.
        dbgStates = ["ready", "programming", "fail"]
        dbgState = dbgStates[Math.floor(Math.random() * dbgStates.length)]
        Weblab.dbgSetOfflineSendCommandResponse 'STATE=' + dbgState

        Weblab.sendCommand 'STATE',
          (response) =>
            state = response.substr(6)

            if @update
              @$rootScope.$apply =>
                @update(state)

            if !@shouldStop
              @_timeout = @$timeout @_check, 2000
          ,
          (response) =>
            # TODO: Handle connection lost
            console.error "Error on STATE:"
            console.error response

            if !@shouldStop
              @_timeout = @$timeout @_check, 6000
        ,
        2000)


    # Stops the refreshing task from running. May take some seconds to stop.
    stop: ->
      console.log "Stopping RefreshState"
      @shouldStop = true
      @$timeout.cancel(@_timeout)

    # Returns true if the task is not running or about to stop.
    running: ->
      !@shouldStop
  ]