
# Starts sending a periodical command to retrieve the load.
@StartRetrievingLoad = (instanceid, values) ->
  fakeResponse = Math.random() * 10

  Weblab.dbgSetOfflineSendCommandResponse fakeResponse, true

  if Weblab.isExperimentActive() or !Weblab.checkOnline()
    controller = Weblab.sendCommandPeriodically(instanceid + ":LOAD", 4000
      (load) =>
        load = parseFloat(load);
        load = load.toFixed(2);

        # Report the new value to the Instance.
        values["ball.weight"] = load

        console.log "[LoadRetriever]: LOAD response: " + load
        #$("#" + instanceid + "-load").text(load + " " + $.i18n._("grams"));

        $("#" + instanceid + "-table-sensors").datatable("updateAll")
      (response) =>
        console.error "[LoadRetriever]: ERROR: " + response
    )

  controller


# Starts sending a periodical command to retrieve the level.
@StartRetrievingLevel = (instanceid, values) ->
  fakeResponse = Math.random() * 10

  Weblab.dbgSetOfflineSendCommandResponse fakeResponse, true

  if Weblab.isExperimentActive() or !Weblab.checkOnline()

    controller = Weblab.sendCommandPeriodically(instanceid + ":LEVEL", 4000
      (level) =>
        level = parseFloat(level);
        level = level.toFixed(2);

        # Report the new value to the Instance.
        values["liquid.level"] = level
        @level = level;
        console.log "[LevelRetriever]: LEVEL response: " + level
        #$("#" + instanceid + "-level").text(level + " " + $.i18n._("cm"));

        $("#" + instanceid + "-table-sensors").datatable("updateAll")
      (response) =>
        console.error "[LevelRetriever]: ERROR: " + response
    )

  controller