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
  .directive('wlButton', ->
    templateUrl: 'views/wlbutton.html',
    scope:
      'ident': '@ident'
    restrict: 'E'
    link: (scope, element, attrs) ->

      # The button can currently be on or off.
      scope.button = {};
      scope.button.isOn = false;
      scope.isOn = -> return scope.button.isOn


      scope.press = ->
        console.debug("Button " + scope.ident + " pressed.")

        Weblab.dbgSetOfflineSendCommandResponse("ok")

        Weblab.sendCommand "SetPulse on " + scope.ident,
          =>
            console.debug "A"
          =>
            console.debug "B"

#          (=>
#            console.debug "aSetPulse succeeded"
#          ),(=>
#            console.debug "SetPulse failed"
#          )

#        Weblab.sendCommand "SetPulse on " + scope.ident,
#          =>
#            # On success
#            console.debug "SetPulse succeeded"
#            scope.button.isOn = true
#
#            $timeout (->
#              Weblab.dbgSetOfflineSendCommandResponse "ok"
#              Weblab.sendCommand "SetPulse off " + scope.ident, (
#                =>
#                  # On success
#                  scope.button.isOn = false
#                ), (
#                =>
#                  # On failure
#                  scope.button.isOn = false
#                )
#            ),(
#            2000
#            )
#          =>
#              # On failure
#              console.debug "SetPulse failed"


  )
