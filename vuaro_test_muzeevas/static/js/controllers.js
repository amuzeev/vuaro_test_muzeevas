var galleryApp = angular.module('galleryApp', []);


galleryApp.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
});

galleryApp.config(
    ['$locationProvider',
        function($locationProvider) {
            $locationProvider.html5Mode(true);
        }
    ]
);

galleryApp.controller('MyPictureListCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $http.get('/api/v1/my/').success(function(data) {
            $scope.pictures = data;
        });
    }]);

galleryApp.controller('IndexPictureListCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $http.get('/api/v1/last/').success(function(data) {
            $scope.last_pictures = data;
        });
    }]);


galleryApp.controller("UserPictureListCtrl", ['$scope', '$http', '$location',
    function($scope, $http, $location)
    {
        var path = $location.path();
        var re = new RegExp('^/user/(\\d+)/$');
        var match = path.match(re);

        if (match){
            var userId = match[1];
            var url = '/api/v1/user/' + userId +'/';

            $http.get(url).success(function(data) {
                $scope.pictures = data;
            });
        }
    }]
);