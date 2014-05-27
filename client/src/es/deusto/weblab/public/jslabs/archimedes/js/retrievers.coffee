
# Starts sending a periodical command to retrieve the load.
@StartRetrievingLoad = (instanceid) ->
  fakeResponse = Math.random() * 10

  Weblab.dbgSetOfflineSendCommandResponse fakeResponse, true

  if Weblab.isExperimentActive() or !Weblab.checkOnline()
    controller = Weblab.sendCommandPeriodically("LOAD", 3000
      (load) =>
        load = parseFloat(load);
        load = load.toFixed(2);
        console.log "[LoadRetriever]: LOAD response: " + load
        $("#" + instanceid + "-load").text(load + " " + $.i18n._("grams"));
      (response) =>
        console.error "[LoadRetriever]: ERROR: " + response
    )

  controller


# Starts sending a periodical command to retrieve the level.
@StartRetrievingLevel = (instanceid) ->
  fakeResponse = Math.random() * 10

  Weblab.dbgSetOfflineSendCommandResponse fakeResponse, true

  if Weblab.isExperimentActive() or !Weblab.checkOnline()

    controller = Weblab.sendCommandPeriodically("LEVEL", 3000
      (load) =>
        load = parseFloat(load);
        load = load.toFixed(2);
        console.log "[LevelRetriever]: LEVEL response: " + load
        $("#" + instanceid + "-level").text(load + " " + $.i18n._("cm"));
      (response) =>
        console.error "[LevelRetriever]: ERROR: " + response
    )

  controller