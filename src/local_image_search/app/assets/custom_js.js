function reload_js(src) {
    $('script[src="' + src + '"]').remove();
    $('<script>').attr('src', src).appendTo('body');
  }
var targetObj = {"index": 0, "totalimages": 0, "done": "false"}

var targetProxy = new Proxy(targetObj, {
    set: function (target,key, value) {
        target[key] = value;
        console.log(target["index"], target["totalimages"], target["done"], target["index"] == target["totalimages"])
        if (target["index"] == target["totalimages"]) {
            target["done"] = true
            console.log("done")
            reload_js('/assets/main.js')
            $('div.gallery a').on('click', openPhotoSwipe)
            slides = {}

            createSlides()
            reload_js('/assets/photoswipe.min.js')
            reload_js('/assets/photoswipe-ui-default.min.js')
            
        }
        return true;
    }
  });
document.getElementById("dirs").addEventListener("change", function(event) {
    const container = document.getElementsByClassName("col gallery")[0];
    var files = event.target.files;

    
    for (var i=0; i<10; i++) {
            //   if it is an image file
        if (files[i].type.match('image.*')) {
            targetProxy["totalimages"] +=1
            //  create a new FileReader
            var reader = new FileReader();
            //   read the file
            reader.readAsDataURL(files[i]);
            //   define the callback function
            
            reader.onload = function(e) {
                //   create a new image
                var img = new Image();
                //   set the image source
                img.src = e.target.result;
                img.onload= function() {
                    
                    //   append the image to the output
                    var link = document.createElement('a');
                    link.href = img.src;
                    link.classList.add(`gallery-photo`);
                    link.dataset.index = targetProxy["index"];
                    link.dataset.gallery = 0 ;
                    link.dataset.type = `image`; // FIXME use the actual image type
                    link.dataset.width = img.width;
                    link.dataset.height = img.height
                    //link.dataset.date = files[i].lastModifiedDate;
                    link.style.cssText = `--w: ${img.width}px; --h: ${img.height}px;`;
                    img.classList.add('thumbnail', 'rounded');
                    link.appendChild(img);
                    container.appendChild(link);
                    targetProxy["index"] +=1
                    
                }
                // wait for the image to load


            }
            
        }
    

        
    };
  }, false);
