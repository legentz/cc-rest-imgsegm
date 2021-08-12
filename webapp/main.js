(function () {
	var pageReady = "DOMContentLoaded";
	var imageDropzone = document.getElementById("image-to-process");
	var sendImageBtn = document.getElementById("send-multipart-request");

	/**
		Events
	*/

	// pageReady
	document.addEventListener(pageReady, function (e) {
		console.log(pageReady);
	});

	/**
		Actions
	*/

	// Send image to process
	sendImageBtn.onclick = function (e) {	
		console.log("Clicked on sendImageBtn");
		// console.log(payload);
	};

})();