var endpoint = "http://0.0.0.0:5000"
var pageReady = "DOMContentLoaded";

Dropzone.options.myDropzone = {

	// Prevents Dropzone from uploading dropped files immediately
	autoProcessQueue: false,
	url: endpoint + "/from_img",
	method: "post",
	uploadMultiple: true,
	maxFiles: 3,

	init: function() {
		var submitButton = document.querySelector("#submit-all")
		myDropzone = this; // closure

		submitButton.addEventListener("click", function() {
			myDropzone.processQueue(); // Tell Dropzone to process all queued files.
		});

		// You might want to show the submit button only when 
		// files are dropped here:
		this.on("addedfile", function() {
			// Show submit button here and/or inform user to click it.
			submitButton.disabled = false;
		});
		// TODO: check for "zero" files to upload to deactivate the "predict" button again...

		this.on("sending", function(file) {
			// alert('Sending the file' +  file.name);
			// TODO
		});

		document
			.querySelector("button#clear-dropzone")
			.addEventListener("click", function() {
			// Using "myDropzone" here, because "this" doesn't point to the dropzone anymore
			myDropzone.removeAllFiles();
		});

	}
};



/**
	Events
*/

// pageReady
$(document).ready((e) => {
	console.log(pageReady);
});
