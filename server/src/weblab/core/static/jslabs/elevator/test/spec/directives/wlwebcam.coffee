'use strict'

describe 'Directive: wlWebcam', ->

  # load the directive's module
  beforeEach module 'elevatorApp'

  scope = {}

  beforeEach inject ($controller, $rootScope) ->
    scope = $rootScope.$new()

  it 'should make hidden element visible', inject ($compile) ->
    element = angular.element '<wl-webcam></wl-webcam>'
    element = $compile(element) scope
    expect(element.text()).toBe 'this is the wlWebcam directive'
