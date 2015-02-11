'use strict'



###*
 # @ngdoc directive
 # @name elevatorApp.directive:wlbutton
 # @description
 # TODO: Not yet implemented.
 # Command to turn a switch: ChangeSwitch off 0
 # Command to press a button: SetPulse off 0       |    SetPulse on 0
###
angular.module('elevatorApp')
  .directive('wlButton', ($timeout) ->
    templateUrl: 'views/wlbutton.html',
    scope:
      'ident': '@ident'
    restrict: 'E'
    link: (scope, element, attrs) ->

      # The button can currently be on or off.
      scope.button = {};
      scope.button.isOn = false;
      scope.isOn = -> return scope.button.isOn

      # The function to invoke when a button is pressed.
      scope.press = ->
        console.debug("Button " + scope.ident + " pressed.")

        Weblab.dbgSetOfflineSendCommandResponse("ok")

        Weblab.sendCommand "SetPulse on " + scope.ident,
          =>
            console.debug "SetPulse succeeded"
            scope.button.isOn = true

            # In a few seconds, send an off command.
            $timeout (
              ->
                Weblab.dbgSetOfflineSendCommandResponse "ok"
                console.debug "Timeout Triggered"

                Weblab.sendCommand "SetPulse off " + scope.ident,
                  =>
                    console.debug "SetPulse off succeded"
                    scope.button.isOn = false
                  ,
                  =>
                    console.debug "SetPulse off failed"
                    scope.button.isOn = false
              ),
              2000

          ,
          =>
            console.debug "SetPulse failed"
  )
