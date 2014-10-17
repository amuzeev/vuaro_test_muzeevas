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
/*
galleryApp.config(['$routeProvider',
    function($routeProvider) {
        $routeProvider.
            when('/my/', {
                //templateUrl: 'partials/phone-list.html',
                controller: 'MyPictureListCtrl'
            }).
            when('/user/:userId/', {
                //templateUrl: 'partials/phone-detail.html',
                controller: 'UserPictureListCtrl'
            }).
            when('/', {
                //templateUrl: 'partials/phone-detail.html',
                controller: 'IndexPictureListCtrl'
            })
    }]);
*/

//var galleryControllers = angular.module('galleryControllers', []);

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
        console.log(path);
        var re = new RegExp('^/user/(\\d+)/$');

        var match = path.match(re);
        console.log(match);
        if (match){

            var userId = match[1];
            console.log(userId);
            var url = '/api/v1/user/' + userId +'/';
            console.log(url);
            $http.get(url).success(function(data) {
                $scope.pictures = data;
            });
        }



    }]
);
/*
galleryControllers.controller('UserPictureListCtrl', ['$scope', '$routeParams', '$http',
    function($scope, $routeParams, $http) {
        $http.get('/api/v1/user/'+$routeParams.userId+'/').success(function(data) {
            $scope.pictures = data;
        });
    }]);
*/


/*
galleryApp.controller('MyPictureListCtrl', function ($scope, $http) {
    $http.get('/api/v1/my/').success(function(data) {
        $scope.pictures = data;
    });
});


galleryApp.controller('IndexPictureListCtrl', function ($scope, $http) {
    $http.get('/api/v1/last/').success(function(data) {
        $scope.last_pictures = data;
    });
});
*/

/*
GalleryApp.controller('UserPictureListCtrl', function ($scope, $http, $routeParams) {
    $http.get('/api/v1/user/'+$routeParams.userId+'/').success(function(data) {
        $scope.pictures = data;
    });
});

*/
/*
galleryApp.controller('UserPictureListCtrl', ['$scope', '$routeParams', '$http',
    function($scope, $routeParams, $http) {
        console.log($routeParams);
        $http.get('/api/v1/user/'+$routeParams.userId+'/').success(function(data) {
            $scope.pictures = data;
        });
    }]);

*/