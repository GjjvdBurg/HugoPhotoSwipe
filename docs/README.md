Options
=======

The following options are available in the ``hugophotoswipe.yml`` file:

| Option | Default | Description |
| ------ | ------- | ----------- |
| markdown_dir | None | Output directory for the markdown files |
| output_dir | None | Output directory for the resized photos |
| url_prefix | '' | Prefix for urls to images in markdown |
| output_format | 'jpg' | Output format of the images |
| dirname_large | 'large' | Name of directory for large images |
| dirname_small | 'small' | Name of directory for smaller images |
| dirname_thumb | 'thumb' | Name of directory for thumbnails |
| dim_max_large | '1600' | Maximum large image size (see below) |
| dim_max_small | '800' | Maximum small image size (see below) |
| dim_max_thumb | '256x256' | Maximum thumbnail dimensions (see below) |
| dim_max_cover | '600x600' | Maximum cover image dimensions (see below) |
| cover_filename | 'coverimage.jpg' | Name of coverimage file |
| photo_dir | 'photos' | Name of directory in album where photos are stored |
| album_file | 'album.yml' | Name of YAML file with photo descriptions |
| use_smartcrop_js | False | Use ``smartcrop-cli.js`` for thumbnails |
| smartcrop_js_path | None | Path to ``smartcrop-cli.js`` executable |
| jpeg_progressive | False | Output progressive JPEGs |
| jpeg_optimize | False | Optimize JPEG output |
| jpeg_quality | 75 | JPEG quality factor |

Naturally, the jpeg options are only applied when ``output_format`` is 
``jpg``.

Maximum image size
------------------

For each of the four possible output modes, the maximum image dimension can be 
set with the respective ``dim_max_`` setting. This setting can either be an 
exact dimension (``'widthxheight'``, e.g. ``'300x400'``), a partial dimension 
(``'300x'`` or ``'x400'``) or a single number (``300`` or ``'300'``). When an 
exact dimension is given, the photo will be resized to those dimensions (with 
no regard for the aspect ratio).  When a partial dimension is given, the other 
dimension will be scaled such that the aspect ratio of the photo remains 
unchanged. When a single number is given, the *maximum* dimension of the photo 
will be reduced to the given number, and the other dimension is chosen 
according to the aspect ratio.

Shortcodes
==========

Use the following shortcodes in Hugo for parsing the Markdown.

In ``layouts/shortcodes/photo.html``::

```html
<figure itemprop="associatedMedia" itemscope
itemtype="https://schema.org/ImageObject">
  <a href="{{ .Get "href"}}" itemprop="contentUrl" data-size="{{ .Get "largeDim"}}" data-medium-url="{{ .Get "smallUrl" }}" data-medium-size="{{ .Get "smallDim" }}">
    <img alt="{{ .Get "alt"}}" data-size="{{ .Get "thumbSize"}}" itemprop="thumbnail" src="{{ .Get "thumbUrl"}}">
  </a>
  <figcaption itemprop="caption description">
    {{ .Get "caption"}}
    {{ if (not (eq (.Get "copyright") "")) }}
    <span itemprop="copyrightHolder">&#169; {{ .Get "copyright"}}</span>
    {{ end }}
  </figcaption>
</figure>
```

And in ``layouts/shortcodes/wrap.html``::

    {{ .Inner }}

The ``wrap`` shortcode is needed due to [this 
issue](https://github.com/spf13/hugo/issues/1642) in Hugo.

PhotoSwipe Javascript
=====================

HugoPhotoSwipe expects the following Javascript to be included on the gallery
pages, refer to the [PhotoSwipe 
documentation](http://photoswipe.com/documentation/getting-started.html) for 
more information. This file should be stored as ``pswp_gallery.js`` (with 
regards to the HTML code below).

```javascript
var initPhotoSwipeFromDOM = function(gallerySelector) {

    // parse slide data (url, title, size ...) from DOM elements
    // (children of gallerySelector)
    var parseThumbnailElements = function(el) {
        var thumbElements = el.childNodes,
            numNodes = thumbElements.length,
            items = [],
            figureEl,
            linkEl,
            size,
            item;

        for(var i = 0; i < numNodes; i++) {

            figureEl = thumbElements[i]; // <figure> element

            // include only element nodes
            if(figureEl.nodeType !== 1) {
                continue;
            }

            linkEl = figureEl.children[0]; // <a> element
	    if (linkEl === undefined)
		    continue;

            size = linkEl.getAttribute('data-size').split('x');
	    mediumSize = linkEl.getAttribute('data-medium-size').split('x');

            // create slide object
            item = {
		    originalImage: {
			    src: linkEl.getAttribute('href'),
                	    w: parseInt(size[0], 10),
                            h: parseInt(size[1], 10)
		    },
		    mediumImage: {
			    src: linkEl.getAttribute('data-medium-url'),
			    w: parseInt(mediumSize[0], 10),
			    h: parseInt(mediumSize[1], 10)
		    }
            };

            if(figureEl.children.length > 1) {
                // <figcaption> content
                item.title = figureEl.children[1].innerHTML;
            }

            if(linkEl.children.length > 0) {
                // <img> thumbnail element, retrieving thumbnail url
		//item.msrc = linkEl.children[0].getAttribute('src');
            }

            item.el = figureEl; // save link to element for getThumbBoundsFn
            items.push(item);
        }

        return items;
    };

    // find nearest parent element
    var closest = function closest(el, fn) {
        return el && ( fn(el) ? el : closest(el.parentNode, fn) );
    };

    // triggers when user clicks on thumbnail
    var onThumbnailsClick = function(e) {
        e = e || window.event;
        e.preventDefault ? e.preventDefault() : e.returnValue = false;

        var eTarget = e.target || e.srcElement;

        // find root element of slide
        var clickedListItem = closest(eTarget, function(el) {
            return (el.tagName && el.tagName.toUpperCase() === 'FIGURE');
        });

        if(!clickedListItem) {
            return;
        }

        // find index of clicked item by looping through all child nodes
        // alternatively, you may define index via data- attribute
        var clickedGallery = clickedListItem.parentNode,
            childNodes = clickedListItem.parentNode.childNodes,
            numChildNodes = childNodes.length,
            nodeIndex = 0,
            index;

        for (var i = 0; i < numChildNodes; i++) {
            if(childNodes[i].nodeType !== 1) {
                continue;
            }

            if(childNodes[i] === clickedListItem) {
                index = nodeIndex;
                break;
            }
            nodeIndex++;
        }



        if(index >= 0) {
            // open PhotoSwipe if valid index found
            openPhotoSwipe( index, clickedGallery );
        }
        return false;
    };

    // parse picture index and gallery index from URL (#&pid=1&gid=2)
    var photoswipeParseHash = function() {
        var hash = window.location.hash.substring(1),
        params = {};

        if(hash.length < 5) {
            return params;
        }

        var vars = hash.split('&');
        for (var i = 0; i < vars.length; i++) {
            if(!vars[i]) {
                continue;
            }
            var pair = vars[i].split('=');
            if(pair.length < 2) {
                continue;
            }
            params[pair[0]] = pair[1];
        }

        if(params.gid) {
            params.gid = parseInt(params.gid, 10);
        }

        return params;
    };

    var openPhotoSwipe = function(index, galleryElement, disableAnimation, fromURL) {
        var pswpElement = document.querySelectorAll('.pswp')[0],
            gallery,
            options,
            items;

        items = parseThumbnailElements(galleryElement);

        // define options (if needed)
        options = {

            // define gallery index (for URL)
            galleryUID: galleryElement.getAttribute('data-pswp-uid'),

            getThumbBoundsFn: function(index) {
                // See Options -> getThumbBoundsFn section of documentation for more info
                var thumbnail = items[index].el.getElementsByTagName('img')[0], // find thumbnail
                    pageYScroll = window.pageYOffset || document.documentElement.scrollTop,
                    rect = thumbnail.getBoundingClientRect();

                return {x:rect.left, y:rect.top + pageYScroll, w:rect.width};
            }

        };

        // PhotoSwipe opened from URL
        if(fromURL) {
            if(options.galleryPIDs) {
                // parse real index when custom PIDs are used
                // http://photoswipe.com/documentation/faq.html#custom-pid-in-url
                for(var j = 0; j < items.length; j++) {
                    if(items[j].pid == index) {
                        options.index = j;
                        break;
                    }
                }
            } else {
                // in URL indexes start from 1
                options.index = parseInt(index, 10) - 1;
            }
        } else {
            options.index = parseInt(index, 10);
        }

        // exit if index not found
        if( isNaN(options.index) ) {
            return;
        }

        if(disableAnimation) {
            options.showAnimationDuration = 0;
        }

	// Gertjan: this was added because thumbnails are square and pictures
	// are typically not.
	options.showHideOpacity = true;

	// Pass data to PhotoSwipe and initialize it
        gallery = new PhotoSwipe( pswpElement, PhotoSwipeUI_Default, items, options);

	// Added by Gertjan
	var realViewportWidth,
	    useLargeImages = false,
	    firstResize = true,
	    imageSrcWillChange;

	gallery.listen('beforeResize', function() {
		// gallery.viewportSize.x - width of PhotoSwipe viewport
		// gallery.viewportSize.y - height of PhotoSwipe viewport
		// window.devicePixelRatio - ratio between physical pixels and
		// device independent pixels (Number). 1 (regular display), 2
		// (@2x, retina), ...

		// calculate real pixels when size changes
		realViewportWidth = gallery.viewportSize.x * window.devicePixelRatio;

		// Code below is needed if you want to switch dynamically on
		// window.resize

		// Find out if current images need to be changed
		if (useLargeImages && realViewportWidth< 1000) {
			useLargeImages = false;
			imageSrcWillChange = true;
		} else if (!useLargeImages && realViewportWidth >= 1000) {
			useLargeImages = true;
			imageSrcWillChange = true;
		}

		// Invalidate items only when source is changed and when it's
		// not the first update
		if (imageSrcWillChange && !firstResize) {
			// invalidateCurrItems sets a flag on slides that are
			// in DOM, which will force update of content (image)
			// on window.resize
			gallery.invalidateCurrItems();
		}

		if (firstResize) {
			firstResize = false;
		}

		imageSrcWillChange = false;
	});

	// gettingData event fires each time PhotoSwipe retrieves image source
	// and size
	gallery.listen('gettingData', function(index, item) {

		// set image source & size based on real viewport width
		if (useLargeImages) {
			item.src = item.originalImage.src;
			item.w = item.originalImage.w;
			item.h = item.originalImage.h;
		} else {
			item.src = item.mediumImage.src;
			item.w = item.mediumImage.w;
			item.h = item.mediumImage.h;
		}
	});

        gallery.init();
    };

    // loop through all gallery elements and bind events
    var galleryElements = document.querySelectorAll( gallerySelector );

    for(var i = 0, l = galleryElements.length; i < l; i++) {
        galleryElements[i].setAttribute('data-pswp-uid', i+1);
        galleryElements[i].onclick = onThumbnailsClick;
    }

    // Parse URL and open gallery if it contains #&pid=3&gid=1
    var hashData = photoswipeParseHash();
    if(hashData.pid && hashData.gid) {
        openPhotoSwipe( hashData.pid ,  galleryElements[ hashData.gid - 1 ], true, true );
    }
};

// execute above function
initPhotoSwipeFromDOM('.gallery');
```

PhotoSwipe HTML
===============

And finally, the following HTML is needed for the PhotoSwipe gallery. Note 
that the ``{{ .Content }}`` is filled by Hugo, so this HTML should be used as 
a Hugo layout.

```html
<main class="container">
  <h1 class="text-primary">{{ .Title }}</h1>
  <div class="gallery" itemscope itemtype="https://schema.org/ImageGallery">
    {{ .Content }}
  </div>

  <div class="pswp" role="dialog" aria-hidden="true" tabindex="-1">
    <div class="pswp__bg"></div>
    <div class="pswp__scroll-wrap">
      <div class="pswp__container">
        <div class="pswp__item"></div>
        <div class="pswp__item"></div>
        <div class="pswp__item"></div>
      </div>
      <div class="pswp__ui pswp__ui--hidden">
        <div class="pswp__top-bar">
          <div class="pswp__counter"></div>
          <button class="pswp__button pswp__button--close" title="Close (Esc)"></button>
          <button class="pswp__button pswp__button--share" title="Share"></button>
          <button class="pswp__button pswp__button--fs" title="Toggle fullscreen"></button>
          <button class="pswp__button pswp__button--zoom" title="Zoom in/out"></button>
          <div class="pswp__preloader">
            <div class="pswp__preloader__icn">
              <div class="pswp__preloader__cut">
                <div class="pswp__preloader__donut"></div>
              </div>
            </div>
          </div>
        </div>
        <div class="pswp__share-modal pswp__share-modal--hidden pswp__single-tap">
          <div class="pswp__share-tooltip"></div>
        </div>
        <button class="pswp__button pswp__button--arrow--left" title="Previous (arrow left)"></button>
        <button class="pswp__button pswp__button--arrow--right" title="Next (arrow right)"></button>
        <div class="pswp__caption">
          <div class="pswp__caption__center"></div>
        </div>
      </div>
    </div>
  </div>
</main>
<script src="{{ .Site.BaseURL }}js/pswp_gallery.js"></script>
```
