'use strict'

describe 'Directive: wlcallingcontrols', ->

  # load the directive's module
  beforeEach module 'elevatorApp'

  scope = {}

  beforeEach inject ($controller, $rootScope) ->
    scope = $rootScope.$new()

  it 'should make hidden element visible', inject ($compile) ->
    element = angular.element '<wlcallingcontrols></wlcallingcontrols>'
    element = $compile(element) scope
    expect(element.text()).toBe 'this is the wlcallingcontrols directive'
