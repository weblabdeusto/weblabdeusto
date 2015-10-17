// From stackoverflow
(function ($) {
    $.QueryString = (function (a) {
        if (a == "") return {};
        var b = {};
        for (var i = 0; i < a.length; ++i) {
            var p = a[i].split('=');
            if (p.length != 2) continue;
            b[p[0]] = decodeURIComponent(p[1].replace(/\+/g, " "));
        }
        return b;
    })(window.location.search.substr(1).split('&'))
})(jQuery);

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
    var selectedOriginalCategory = $.QueryString.category;

    $scope.experiments = [];
    $scope.categories = {
        // category_name: {
        //     selected: false,
        //     count: 1,
        //     any_visible: true
        //     experiments: []
        // }
    };
    $scope.search = {
        term: "",
        any_experiment_found: true,
        any_category_selected: false
    };
    $scope.experiment_list = {
        order: get_labs_order(LABS_ORDER),
        loading: true
    };

    
    // 
    // Scope methods
    // 
    $scope.filter_experiments = filter_experiments;
    $scope.filterCategory = filterCategory;
    $scope.set_order = set_order;
    $scope.replacePath = replacePath;

    // 
    // Implementation
    // 
    function get_labs_order(db_order) {
        if (db_order == 'alphabetical')
            return 'name';
        if (db_order == 'uses')
            return '-user_uses';
        if (db_order == 'categories')
            return 'category';
        if (db_order == 'date')
            return '-latest_use_epoch';
        return 'name';
    }

    function get_db_order(js_order) {
        if (js_order == 'name')
            return 'alphabetical';
        if (js_order == '-user_uses')
            return 'uses';
        if (js_order == 'category')
            return 'categories';
        if (js_order == '-latest_use_epoch')
            return 'date';
        return null;
    }

    function set_order(order) {
        $scope.experiment_list.order = order;

        var new_order = get_db_order(order);
        if (new_order != null) {
            $http.post(UPDATE_PREFERENCES_URL, { 'labs_sort_method' : new_order }); 
        }
    }

    function filterCategory(category) {

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

    function replacePath(url) {
        location.replace(url);  
    };

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

        angular.forEach($scope.categories, function(category_data, category_name) {
            var any_category_experiment_found = false;
            angular.forEach(category_data.experiments, function(exp, index) {
                if (exp.visible)
                    any_category_experiment_found = true;
            });
            category_data.any_visible = any_category_experiment_found;
        });
    }

    function _on_load_experiments(data) {
        $scope.experiments = data.experiments;
        angular.forEach(data.experiments, function(exp, index) {
            exp.visible = true;
            if (exp.category in $scope.categories) {
                $scope.categories[exp.category].count++;
                $scope.categories[exp.category].experiments.push(exp);
            } else {
                $scope.categories[exp.category] = {
                    any_visible: true,
                    selected: false,
                    count: 1,
                    experiments: [ exp ]
                };
            }
        });
        $scope.experiment_list.loading = false;

        if (selectedOriginalCategory && $scope.categories.hasOwnProperty(selectedOriginalCategory)) {
            filterCategory(selectedOriginalCategory);
        }
    }

    function _on_load_error(data) {
        // TODO TODO TODO
        console.log("ERROR FATAL");
    }
}

angular.element(document).ready(function () {
    angular.bootstrap(document, ['labsScreen']);
});

