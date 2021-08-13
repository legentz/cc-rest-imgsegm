(() => {
	var endpoint = "http://0.0.0.0:5000"

	var pageReady = "DOMContentLoaded";
	// var imageDropzone = $("#image-to-process");
	// var sendImageBtn = $("#send-multipart-request");

	// Dropzone init
	$(document).ready((e) => {
		var formDropzone = $("div#form-dropzone").dropzone({
			url: endpoint + "/predict-from-img",
			method: "post",
			paramName: "imgs",
			maxFiles: 3
		});
	});

	/**
		Events
	*/

	// pageReady
	$(document).ready((e) => {
		console.log(pageReady);
	});

	/**
		Actions
	*/

	// Send image to process
	// sendImageBtn.onClick((e) => {	
	// 	console.log("Clicked on sendImageBtn");

	// 	$.ajax({
 //        url: endpoint + '/upload',
 //        dataType: 'json',
 //        data: imageDropzone.data(),                         
 //        type: 'post',
 //        success: function(php_script_response){
 //            alert(php_script_response); // display response from the PHP script, if any
 //        }
 //     });
	// });

})();