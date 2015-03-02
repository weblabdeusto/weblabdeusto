'use strict'

###*
 # @ngdoc filter
 # @name dashboardappApp.filter:NonInternalFilter
 # @function
 # @description
 # # NonInternalFilter
 # Filter in the dashboardappApp.
###
angular.module 'dashboardappApp'
  .filter 'NonInternal', ->
    (input) ->

      if input == undefined
        return undefined

      # Get an object with the same contents but with no internal vars (those that start with '$').
      obj = {}
      for key in Object.keys(input) when key.length < 1 || key[0] != '$'
        obj[key] = input[key]

      return obj
