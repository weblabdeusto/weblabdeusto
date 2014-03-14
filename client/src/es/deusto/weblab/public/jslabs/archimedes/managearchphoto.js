var state;
var response;
var remainingTime;


PhotoManage = new function(){

	 this.takePhoto = function (){
	 		Weblab.sendCommand("IMAGE", 
			function(data) {
				$("body").append('<img src="data:image/jpg;base64,' + data + '"/>');
			},
			function(error) {
				console.error("Error: " + error);
			});
	 }
}

$(document).ready(function(){
	PhotoManage.takePhoto();
});