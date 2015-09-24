'use strict'

describe 'Service: refreshstate', ->

  # load the service's module
  beforeEach module 'elevatorApp'

  # instantiate service
  refreshstate = {}
  beforeEach inject (_refreshstate_) ->
    refreshstate = _refreshstate_

  it 'should do something', ->
    expect(!!refreshstate).toBe true
