var app = angular.module("myApp", []);
app.factory('$socket', function ($rootScope) {
  var socket = io.connect('http://' + document.domain + ':' + location.port+"/s");
  return {
    on: function (eventName, callback) {
      socket.on(eventName, function () {
        var args = arguments;
        $rootScope.$apply(function () {
          callback.apply(socket, args);
        });
      });
    },
    emit: function (eventName, data, callback) {
      socket.emit(eventName, data, function () {
        var args = arguments;
        $rootScope.$apply(function () {
          if (callback) {
            callback.apply(socket, args);
          }
        });
      })
    }
  };
});


app.controller("TaskController", function($scope, $http, $timeout,$socket) {
    $scope.last_result = -1;
    $scope.current_task = -1;
    $scope.target_id = -1
    $scope.error_id = -1

    //Socket Bindings
    $socket.on("connected",function(data){$socket.emit("get_tasks");})
    //$socket.on("disconnected",function(data){})
    $socket.on("all_task",function(data){$scope.taskList=data})
    $socket.on("error",function(data){alert("ERROR:"+data)})
    $socket.on("active_task",
        function(data){
            $scope.current_task=data;
            $scope.target_id=$scope.error_id=-1;
        })

//    $scope.getData = function () {
//         $http.get('/api/tasks').
//            success(function (data, status, headers, config) {
//                if (data == $scope.last_result){
//                    return
//                }
//                $scope.taskList = data["data"];
//                console.log($scope.taskList)
//            }).
//            error(function (data, status, headers, config) {
//                // log error #TODO
//            });
//    }
    $scope.calculateClass=function(task_id){
        if (task_id == $scope.current_task){
            return "btn-success";
        }
        if (task_id == $scope.target_id){
            return "btn-primary"
        }
        if (task_id == $scope.error_id){
            return "btn-error"
        }
        return "btn-default"
    }
    $scope.onClick = function(target_index,task_id){
        $scope.target_id = task_id
        $scope.error_id = -1
        $scope.current_task = -1
        $socket.emit("activate_task",task_id)
//        $http.get("/api/tasks/"+task_id).
//            success(function (data,status,headers,config){
//                $scope.target_id = -1
//                $scope.current_task = task_id
//                $(target_id).removeClass("btn-primary")
//                $(target_id).addClass("btn-success")
//
//
//            }).
//            error(function(data,status,headers,config){
//                //log error #TODO
//                $scope.target_id = -1
//                $scope.error_id = task_id
//                console.log("ERROR!")
//                $(target_id).removeClass("btn-primary")
//                $(target_id).addClass("btn-error")
//            })
    }
    //$scope.connection = io.connect('http://' + document.domain + ':' + location.port+"/s");
    //$scope.bind_socket_events($scope.connection)
    //$scope.getData()
    //$scope.intervalFunction()
    //                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 $(window).on('focus', $scope.getData);

});

