(function() {
	// Source:
	// https://www.w3schools.com/howto/tryit.asp?filename=tryhow_js_image_magnifier_glass

	// STEPS
	// 1. Create a canvas from the img.src
	// 2. Use the moving box as a pointer moving it around
	// 3. On click, create a new canvas with the extracted portion of the image
	// 4. Show it as an image (creating an Image element) and as binary Matrix

    function magnify(imgURL, imgW, imgH) {
        var img, glass, w, h, bw;

        // Step 1
        img = new Image();
        img.width = imgW;
        img.height = imgH;
        img.src = imgURL;

        imgCanvas = document.createElement("canvas");
        imgCtx = imgCanvas.getContext("2d");

        imgCanvas.width = imgW;
        imgCanvas.height = imgH;

        img.onload = function () {
        	imgCtx.drawImage(img, 0, 0, imgW, imgH);
        };

        // Step 2
        glass = document.createElement("div");
        glass.setAttribute("class", "img-magnifier-glass");

        mainDiv = document.getElementsByClassName("img-magnifier-container")[0]; // TODO: use id instead of class
        mainDiv.appendChild(imgCanvas);
        mainDiv.insertBefore(glass, imgCanvas); 

        bw = 2; // TODO: border width not hardcoded
        w = glass.offsetWidth / 2;
        h = glass.offsetHeight / 2;

        /*execute a function when someone moves the magnifier glass over the image:*/
        glass.addEventListener("mousemove", moveMagnifier);
        imgCanvas.addEventListener("mousemove", moveMagnifier);

        // Step 3
        // TODO: click to get the matrix
        glass.addEventListener("click", clickMagnifier);

        function clickMagnifier (e) {
        	gPos = glassPos(e);
        	croppedCan = crop(imgCanvas, {x: gPos.x - w, y: gPos.y - h}, {x: gPos.x + w, y: gPos.y + h});
        	croppedCanCtx = croppedCan.getContext("2d");
        	    
    	    // Create an image for the new canvas.
    	    var image = new Image();
    	    image.src = croppedCan.toDataURL();
    	  
    	    // Put the image where you need to.
    	    $("#selection-and-prediction").html("<h3>Selection</h3><br>").append(image);
    	   	
    	   	pixels = croppedCanCtx.getImageData(0, 0, glass.offsetWidth, glass.offsetHeight).data;
    	   	reducedPixels = [];

    	   	// RGBa to Gray scale
        	for (var i = 0; i < pixels.length; i += 4) {
        		red = pixels[i];
        		green = pixels[i + 1];
        		blue = pixels[i + 2];
        		    
        		gray = (red + green + blue) / 3;
        		    
        		reducedPixels.push(gray);
        	}

        	// TODO: prediction
        	console.log("reducedPixels", reducedPixels);
        	$("#selection-and-prediction").append("<h3>Prediction</h3><br>" + reducedPixels);

        	return {
        		reducedPixels: reducedPixels,
        		w: glass.offsetWidth,
        		h: glass.offsetHeight
        	};
        }

        function glassPos (e) {
        	var pos, x, y;
            
            /*prevent any other actions that may occur when moving over the image*/
            e.preventDefault();
            
            /*get the cursor's x and y positions:*/
            pos = getCursorPos(e);
            x = pos.x;
            y = pos.y;

            /*prevent the magnifier glass from being positioned outside the image:*/
            if (x > imgCanvas.width - w) {
                x = imgCanvas.width - w;
            }
            if (x < w) {
                x = w;
            }
            if (y > imgCanvas.height - h) {
                y = imgCanvas.height - h;
            }
            if (y < h) {
                y = h;
            }

            return {
            	x: x,
            	y: y
            }
        }

        function moveMagnifier(e) {
        	// get glass position
            gPos = glassPos(e);

            /*set the position of the magnifier glass:*/
            glass.style.left = (gPos.x - w) + "px";
            glass.style.top = (gPos.y - h) + "px";
        }

        function getCursorPos(e) {
            var a, x = 0, y = 0;
            e = e || window.event;
            
            /*get the x and y positions of the image:*/
            a = imgCanvas.getBoundingClientRect();

            /*calculate the cursor's x and y coordinates, relative to the image:*/
            x = e.pageX - a.left;
            y = e.pageY - a.top;
            
            /*consider any page scrolling:*/
            x = x - window.pageXOffset;
            y = y - window.pageYOffset;
            
            return {
                x: x,
                y: y
            };
        }

        // Crop
		// Returns a cropped canvas given a cavnas and crop region.
		//
		// Inputs:
		// can, canvas
		// a, {x: number, y: number} - left top corner
		// b, {x: number, y: number} - bottom right corner
        // 
        // Source:
        // https://stackoverflow.com/questions/35188022/how-to-cut-an-image-html-canvas-in-half-via-javascript

		function crop(can, a, b) {
		    // get your canvas and a context for it
		    var ctx = can.getContext('2d');
		    
		    // get the image data you want to keep.
		    var imageData = ctx.getImageData(a.x, a.y, b.x, b.y);
		  
		    // create a new cavnas same as clipped size and a context
		    var newCan = document.createElement('canvas');
		    newCan.width = b.x - a.x;
		    newCan.height = b.y - a.y;
		    var newCtx = newCan.getContext('2d');
		  
		    // put the clipped image on the new canvas.
		    newCtx.putImageData(imageData, 0, 0);
		  
		    return newCan;    
		 }
    }

    // Init
    magnify("assets/temp_image.png", 500, 500);

})();