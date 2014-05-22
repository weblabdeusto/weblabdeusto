
class @LoadRetriever

  _timeout : undefined
  _instanceid : undefined

  constructor : (instanceid) ->
    @_instanceid = instanceid

  # Retrieves the load.
  retrieveLoad : () =>
    fakeResponse = Math.random() * 10

    Weblab.dbgSetOfflineSendCommandResponse fakeResponse, true

    if Weblab.isExperimentActive() or !Weblab.checkOnline()

      Weblab.sendCommand("LOAD",
        (load) =>
          console.log "[LoadRetrieved]: LOAD response: " + load
          $("#" + @_instanceid + "-load").text(load + " gr.")
        (response) =>
          console.error "[LoadRetrieved]: ERROR: " + response
      )

  # Starts refreshing the load for this instance.
  #
  start : () =>
    try
      @retrieveLoad()
    catch error
      console.error "Error refreshing LOAD"
    @_timeout = setTimeout @start, 3000

  # Stops refreshin ghte load for this instance.
  #
  stop : () =>
    if @_timeout?
      clearTimeout @_timeout
      @_timeout = undefined
