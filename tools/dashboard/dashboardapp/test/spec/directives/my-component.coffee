'use strict'

describe 'Directive: myComponent', ->

  # load the directive's module
  beforeEach module 'dashboardappApp'

  scope = {}

  beforeEach inject ($controller, $rootScope) ->
    scope = $rootScope.$new()

  it 'should make hidden element visible', inject ($compile) ->
    element = angular.element '<my-component></my-component>'
    element = $compile(element) scope
    expect(element.text()).toBe 'this is the myComponent directive'
