(function() {

    var endpoint = "http://0.0.0.0:5000";
    var minH = 512;
    var minW = 512;
	
    // Source:
	// https://www.w3schools.com/howto/tryit.asp?filename=tryhow_js_image_magnifier_glass

	// STEPS
	// 1. Create a canvas from the img.src
	// 2. Use the moving box as a pointer moving it around
	// 3. On click, create a new canvas with the extracted portion of the image
	// 4. Show it as an image (creating an Image element) and as binary Matrix

    function magnify(imgURL, imgW, imgH) {
        let img, glass, w, h, bw;

        // Step 1
        img = new Image();
        img.width = imgW;
        img.height = imgH;
        img.src = imgURL;

        let imgCanvas = document.createElement("canvas");
        let imgCtx = imgCanvas.getContext("2d");

        imgCanvas.width = imgW;
        imgCanvas.height = imgH;

        img.onload = function () {
        	imgCtx.drawImage(img, 0, 0, imgW, imgH);
        };

        // Step 2
        glass = document.createElement("div");
        glass.setAttribute("class", "img-magnifier-glass");

        let mainDiv = document.getElementsByClassName("img-magnifier-container")[0]; // TODO: use id instead of class
        mainDiv.appendChild(imgCanvas);
        mainDiv.insertBefore(glass, imgCanvas); 

        bw = 2; // TODO: border width not hardcoded
        w = glass.offsetWidth / 2;
        h = glass.offsetHeight / 2;

        /*execute a function when someone moves the magnifier glass over the image:*/
        glass.addEventListener("mousemove", moveMagnifier);
        imgCanvas.addEventListener("mousemove", moveMagnifier);

        // Step 3
        // TODO: click to get the selection onto which predict
        glass.addEventListener("click", clickMagnifier);

        // reduce RGB image to a gray-scaled one (by computing avg)
        function RGBToGray (pixels) {
            let grayPx = [];

            // RGBa to Gray scale
            for (let i = 0; i < pixels.length; i += 4) {
                let red = pixels[i];
                let green = pixels[i + 1];
                let blue = pixels[i + 2];
                    
                let gray = (red + green + blue) / 3;
                    
                grayPx.push(gray);
            }
            return grayPx;
        }

        function askForPrediction (pixels) {
            let xhttp = new XMLHttpRequest;
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    let response = JSON.parse(this.responseText);

                    // prepare div to visualize response
                    let output = document
                        .querySelector("div#output-img");
                    output.innerHTML = '';

                    for (let img_name in response) {
                        let outputImg = document.createElement('img');
                        outputImg.src = response[img_name]['output']
                        
                        output.appendChild(outputImg);
                    }
                }
            };
            xhttp.open("POST", endpoint + "/from_mat", true);
            xhttp.setRequestHeader("Content-type", "application/json;charset=UTF-8");

            // Send as an array of arrays
            xhttp.send(
                JSON.stringify(
                {
                    "images": [
                        pixels
                    ],
                    "normalized": false
                })
            );
        }

        function clickMagnifier (e) {
        	let gPos = glassPos(e);
        	let cropped = crop(imgCanvas, {x: gPos.x - w, y: gPos.y - h}, {x: gPos.x + w, y: gPos.y + h});
            let croppedCan = cropped.canvas;
            let croppedCanCtx = cropped.context;
        	    
    	    // Create an image for the new canvas.
    	    let image = new Image();
    	    image.src = croppedCan.toDataURL();
    	  
    	    // Put the image where you need to.
    	    $("#input-img").empty().append(image);
    	   	
    	   	let pixels = croppedCanCtx.getImageData(0, 0, croppedCan.width, croppedCan.height).data;

            // Obtain a gray-scaled image
            let pixelsGray = RGBToGray(pixels);
            // convert to regular array (use this with uIntArray from RGB canvas)
            // pixels = Array.prototype.slice.call(pixels);
            
            // Async request
            askForPrediction(pixelsGray);

            // Scroll down to notify the user
            $('html,body').animate({
                scrollTop: $("#selection-and-prediction").offset().top
            }, 'slow');

        	return false;
        }

        // get box's x/y position in the canvas
        function glassPos (e) {
        	let pos, x, y;
            
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

        // move the box on hover
        function moveMagnifier(e) {
        	// get glass position
            let gPos = glassPos(e);

            /*set the position of the magnifier glass:*/
            glass.style.left = (gPos.x - w) + "px";
            glass.style.top = (gPos.y - h) + "px";
        }

        // get cursor's x/y position in the canvas
        function getCursorPos(e) {
            let a, x = 0, y = 0;
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
		    let ctx = can.getContext('2d');
		    
		    // get the image data you want to keep.
		    let imageData = ctx.getImageData(a.x, a.y, b.x, b.y);
		  
		    // create a new cavnas same as clipped size and a context
            let newCan = document.createElement('canvas');
		    let scaleCan = document.createElement('canvas');
		    newCan.width = b.x - a.x;
		    newCan.height = b.y - a.y;
            scaleCan.width = minW;
            scaleCan.height = minH;
            let newCtx = newCan.getContext('2d');
		    let scaleCtx = scaleCan.getContext('2d');
		  
		    // put the clipped image on the new canvas.
		    newCtx.putImageData(imageData, 0, 0);

            // TODO: make this dynamic depending on the size of the selection box
            // scale x2 (256px -> minH/minW)
            scaleCtx.scale(2, 2);
            scaleCtx.drawImage(newCan, 0, 0);
		  
		    return {
                "canvas": scaleCan,
                "context": scaleCtx
            }    
		 }
    }

    // TODO: do not hardcode this...
    // init
    magnify("assets/0-5_1536x1024.png", 1536, 1024);

})();