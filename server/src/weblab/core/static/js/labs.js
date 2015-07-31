angular
        .module("labsScreen", [])
        .controller("LabsScreenController", LabsScreenController);

function LabsScreenController($scope, $http) {

    // 
    // Initialization (obtaining labs data)
    // 
    $http.get(LABS_JSON).success(_on_load_experiments).error(_on_load_error);

    // 
    // Variables
    // 
    $scope.experiments = [];
    $scope.categories = {
        // category_name: {
        //     selected: false,
        //     count: 1
        // }
    };
    $scope.search = {
        term: "",
        any_experiment_found: true,
        any_category_selected: false
    };
    
    // 
    // Scope methods
    // 
    $scope.filter_experiments = filter_experiments;
    $scope.category_click = category_click;

    // 
    // Implementation
    // 
    function category_click(category) {

        $scope.categories[category].selected = !$scope.categories[category].selected;
        var any_category_found = false;
        $.each($scope.categories, function(index, cat_data) {
            if (cat_data.selected) {
                any_category_found = true;
                return false;
            }
        });
        $scope.search.any_category_selected = any_category_found;
        filter_experiments();
    }

    function filter_experiments() {
        angular.forEach($scope.experiments, function(experiment, index) {
            // By default, it's visible
            experiment.visible = true;

            // By search term
            var search_term = $scope.search.term.toLowerCase();
            if (search_term.length > 0) { // If there's a search term
                if (!( experiment.name.toLowerCase().indexOf(search_term) >= 0 ||
                        experiment.category.toLowerCase().indexOf(search_term) >= 0 ||
                        experiment.description.toLowerCase().indexOf(search_term) >= 0 
                    )) {
                    experiment.visible = false;
                    return;
                }
            }

            // By category
            if ($scope.search.any_category_selected) {
                if (!$scope.categories[experiment.category].selected) {
                    experiment.visible = false;
                    return;
                }
            }

            // Other filters (future)
        });

        $scope.search.any_experiment_found = $scope.experiments.filter(function(exp) { return exp.visible; }).length > 0;
    }

    function _on_load_experiments(data) {
        $scope.experiments = data.experiments;
        angular.forEach(data.experiments, function(exp, index) {
            exp.visible = true;
            if (exp.category in $scope.categories) {
                $scope.categories[exp.category].count++;
            } else {
                $scope.categories[exp.category] = {
                    selected: false,
                    count: 1
                };
            }
        });
    }

    function _on_load_error(data) {
        // TODO TODO TODO
        console.log("ERROR FATAL");
    }
}

angular.element(document).ready(function () {
    angular.bootstrap(document, ['labsScreen']);
});

