var GalleryApp = angular.module('GalleryApp', []).config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
});


GalleryApp.controller('PictureListCtrl', function ($scope, $http) {
    $http.get('/api/v1/my/').success(function(data) {
        $scope.pictures = data;
    });

    //$scope.orderProp = 'age';
});