'use strict'

###*
 # @ngdoc directive
 # @name dashboardappApp.directive:myComponent
 # @description
 # # myComponent
###
angular.module 'dashboardappApp'
  .directive 'myComponent', ['$rootScope', ($rootScope) ->
    restrict: 'E',
    scope:
      componentid: '=componentid'
      component: '=component'
    templateUrl: 'views/my-component.html'
    link: (scope, element, attrs) ->
      #
  ]
