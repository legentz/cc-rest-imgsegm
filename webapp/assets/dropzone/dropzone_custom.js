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

		this.on("reset", function() {
			submitButton.disabled = true;
		});

		this.on("successmultiple", function(obj, response) {
			var input = document
				.querySelector("div#input-img");
			var output = document
				.querySelector("div#output-img");

			for (var img_name in response) {
				inputImg = document.createElement('img');
				outputImg = document.createElement('img');
				inputImg.src = response[img_name]['input']
				outputImg.src = response[img_name]['output']

				input.appendChild(inputImg);
				output.appendChild(outputImg);
			}
		});

		document
			.querySelector("button#clear-dropzone")
			.addEventListener("click", function() {
			// Using "myDropzone" here, because "this" doesn't point to the dropzone anymore
			myDropzone.removeAllFiles();
		});

	}
};