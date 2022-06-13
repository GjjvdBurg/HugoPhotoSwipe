# HugoPhotoSwipe Walkthrough

In this guide we will set up a simple website using Hugo and HugoPhotoSwipe. 
We will first set up our entire Hugo configuration and then set up the 
HugoPhotoSwipe configuration. You can find the complete source code for the 
final result of this tutorial 
[here](https://github.com/GjjvdBurg/HugoPhotoSwipe-Demo) with a demonstration 
page [here](https://gjjvdburg.github.io/HugoPhotoSwipe-Demo/).

Throughout the demo commands that are meant to be typed into a terminal will
be marked with a ``$`` symbol.

### Table of Contents

* [Installation](#installation)
* [Setting up Hugo](#setting-up-hugo)
  *  [Initializing our site](#initializing-our-site)
  *  [Adding layouts and shortcodes](#adding-layouts-and-shortcodes)
  *  [Adding static files](#adding-static-files)
* [Setting up HugoPhotoSwipe](#setting-up-hugophotoswipe)
  * [Initializing HugoPhotoSwipe](#initializing-hugophotoswipe)
  * [Adding our first album](#adding-our-first-album)
  * [Adding our second album](#adding-our-second-album)
  * [Adding photo descriptions](#adding-photo-descriptions)
* [Viewing the site](#viewing-the-site)
* [Extras](#extras)
  * [Optimizing JPEGs](#optimizing-jpegs)
  * [Using Javascript SmartCrop](#using-javascript-smartcrop)
  * [Custom fields in the TOML](#custom-fields-in-the-toml)


## Installation

Before we begin, make sure you install [hugo](https://gohugo.io/) using the 
[installation instructions](https://gohugo.io/overview/installing/) on the 
site. Next, make sure to install HugoPhotoSwipe with

```
$ pip install hugophotoswipe
```

Finally, download PhotoSwipe from the [PhotoSwipe 
Github](https://github.com/dimsemenov/photoswipe). The easiest way to do this 
is to either clone the repository (if you know what that is) or download the 
files using the "clone or download -> Download ZIP" button on Github. Extract 
the ZIP file to somewhere on your computer, we'll use these files later.

## Setting up Hugo

### Initializing our site

We will start by setting up a basic Hugo photo site. Create a new Hugo site 
using:

```
$ hugo new site hps_example
```

Change to the newly created website with

```
$ cd hps_example
```

The directory in which you are now should contain:

```
archetypes/
config.toml
content/
data/
layouts/
static/
themes/
```

This directory will be called the **Hugo root directory** below.

We will assume that one of the types of content on your site will be photo 
galleries. So, we start off by creating a new subdirectory in the ``content`` 
directory as follows

```
$ mkdir content/galleries
```

### Adding layouts and shortcodes

The ``layouts`` directory in the Hugo root directory contains all the 
information for how our site will look (we won't use themes in this example).
If you do have a theme with your site, you'll have to incorporate this 
configuration into the layout directory of your theme.

#### Cover images

First, we create a file called ``index.html`` in the ``layouts`` directory
for our gallery overview page (which contains the cover images). 
This file simply iterates over each of the galleries and adds a cover image
that links to to the full gallery:

```html
<html>
  <body>
    <main class="container" style="margin-left: calc((100vw - 2*600px - 2*40px)/2);margin-right: auto;">
    {{ range .Data.Pages }}
    <a href="{{ .Permalink }}" style="float: left;margin: 20px;">
        <h1 id="title">{{ .Title }}</h1>
        <img alt="{{ .Title }}" src="{{ .Params.cover }}">
      </a>
    {{ end }}
    </main>
  </body>
</html>
```

Exactly how this works will become more clear later on, but for now we can see 
that we iterate over all pages, add a title for each page and add an image for 
each page. These images will be the *cover images* of the photo albums.

#### Shortcodes

Moving on, we now add the shortcodes that Hugo will use to process the output 
of HugoPhotoSwipe. First, create a ``shortcodes`` subdirectory in the 
``layouts`` directory. Now, in this ``shortcodes`` directory we place two 
files. The first file is ``photo.html``, with the following content

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

The second file is ``wrap.html``, which simply contains

```html
{{ .Inner }}
```

#### Gallery configuration

Finally, we need to tell Hugo what HTML we want to use for the galleries 
themselves. For this, we create a subdirectory of the ``layouts`` directory 
called ``galleries``. In this subdirectory we place the file ``single.html``, 
with the content:

```html
<!DOCTYPE html>
<html lang="{{ .Site.LanguageCode }}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1" />
    <title>
      {{ if ne .URL "/" }} {{ .Title }} &middot; {{ end }} {{ .Site.Title }}
    </title>

    <link rel="stylesheet" type="text/css" href="{{ .Site.BaseURL }}css/photoswipe.css"/>
    <link rel="stylesheet" type="text/css" href="{{ .Site.BaseURL }}css/default-skin/default-skin.css"/>
    <script type="application/javascript" src="{{ .Site.BaseURL }}js/photoswipe.min.js"></script>
    <script type="application/javascript" src="{{ .Site.BaseURL }}js/photoswipe-ui-default.min.js"></script>

  </head>
  <body>

    <!-- Start copied from GitHub docs HugoPhotoSwipe -->

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
    <script type="application/javascript" src="{{ .Site.BaseURL }}js/pswp_gallery.js"></script>

    <!-- End copied from GitHub docs HugoPhotoSwipe -->

    <script src="https://code.jquery.com/jquery-3.1.1.min.js" integrity="sha256-hVVnYaiADRTO2PzUGmuLJr8BLUSjGIZsDYGmIJLv2b8=" crossorigin="anonymous"></script>
  </body>
</html>
```

Again, if you have an existing theme or layout, you may have to incorporate this into an existing file.

### Adding static files

For our PhotoSwipe galleries to actually work, we will need the CSS and 
Javascript files that come with PhotoSwipe, and one extra Javascript file. All 
these files will be placed in the ``static`` directory of your Hugo root 
directory. To keep things organized, we create two subdirectories in the 
``static`` directory:

```
$ mkdir static/{css,js}
```

In the PhotoSwipe folder you downloaded at the begining, go into the ``dist/`` directory. 

Into the ``static/css/`` folder in your hugo site, copy ``photoswipe.css`` and the entire folder ``default-skin/`` 

Into the ``static/js/`` folder in your hugo site, copy all the Javascript (``.js``) files. 

the directory structure of ``static`` is now like this:

```
├── css
│   ├── default-skin
│   │   ├── default-skin.css
│   │   ├── default-skin.png
│   │   ├── default-skin.svg
│   │   └── preloader.gif
│   └── photoswipe.css
└── js
    ├── photoswipe-ui-default.js
    ├── photoswipe-ui-default.min.js
    ├── photoswipe.js
    └── photoswipe.min.js
```

Finally, in the ``static/js`` folder create a file ``pswp_gallery.js``, with 
the following content

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

This completes the Hugo configuration.

## Setting up HugoPhotoSwipe

### Initializing HugoPhotoSwipe

In your Hugo root directory directory, create a ``src`` directory, with a 
subdirectory for the ``photos``:

```
$ mkdir -p src/photos
```

You can use the ``src`` directory also for other things (for instance for sass 
files), but we won't go into that here. Change to the newly created directory

```
$ cd src/photos
```

Now we can initialize HugoPhotoSwipe. We do this with:

```
$ hps init
```

This creates a settings file called ``hugophotoswipe.yml``. If you're not 
familiar with the YAML fileformat, you might want to quickly check out the 
[Wikipedia article about it](https://en.wikipedia.org/wiki/YAML). In the 
``hugophotoswipe.yml`` file, we first change the ``markdown_dir`` variable:

```yaml
markdown_dir: ../../content/galleries/
```

The ``markdown_dir`` variable is the place where Hugo expects to find the 
Markdown files to process. Next, we change the ``output_dir`` 
variable:

```yaml
output_dir: ../../static/pics/
```

This tells HugoPhotoSwipe where to place the resized photos that it will 
create. Finally, we change the ``url_prefix`` variable to:

```yaml
url_prefix: /pics/
```

The ``url_prefix`` variable will be used to make sure the links on your site 
actually point to the photo files. This variable is closely linked to the 
``output_dir`` variable. Because Hugo maps ``static`` to ``/`` in the final 
website, ``static/pics/`` will be mapped to ``/pics/``.

**Side-note**: The setup we're describing here is hosted on GitHub pages, at 
[gjjvdburg.github.io/HugoPhotoSwipe-Demo](https://gjjvdburg.github.io/HugoPhotoSwipe-Demo).
In that case, ``/static/pics`` is actually mapped to 
``HugoPhotoSwipe-Demo/pics`` (remember ``/`` is the root of your domain, so 
that would be ``gjjvdburg.github.io`` for me). So in the configuration you'll 
find on GitHub we use ``url_prefix: /HugoPhotoSwipe-Demo/pics``. So remember: 
if you're photos are not showing up as expected, make sure that the urls in 
the HTML that Hugo generates correspond to where the files actually are.

### Adding our first album

In the ``src/photos`` directory, we can now create a new album with

```
$ hps new cats
```

This creates a directory ``cats`` that contains an ``album.yml`` file and an 
empty ``photos`` directory. For this example, we fill the ``photos`` directory 
with photos of cats taken from 
[pexels.com](https://www.pexels.com/search/cat/), but you can also use other 
photos if you like. Now that we've added our photos, we open the ``album.yml`` 
file to set the album properties. Change the first few fields to the 
following:

```yaml
title: Cute Cats!
album_date: "2017-02-07T22:53:32-05:00"
properties:
   animal: cat
copyright:
coverimage: pexels-photo-127028.jpeg
```

Notice two details that might trip you up:

1. The quotes around the ``album_date`` field, these are important. 

2. The ``animal`` field is preceeded by **3** spaces. Using a ``tab`` (``\t``) or no spaces with result in an error at the next step.

Once you're done editing, go back to the directory with the ``hugophotoswipe.yml`` 
file, and type

```
$ hps update
```

This will create the resized photos in the output directory we specified in 
the ``hugophotoswipe.yml`` settings file, and it will create the ``cats.md`` 
file in the markdown directory we specified.  So, in the ``content/galleries`` 
folder of Hugo we see a ``cats.md`` file and in the ``static/pics`` folder we 
see a ``cats`` directory.

Let's first look at the output of the resized photos in the 
``static/pics/cats`` directory. There are a couple of things to notice here:

 1. Coverimage. The coverimage is a 600x600 cropped version of the 
    ``pexels-photo-127028.jpeg`` photo, which we specified in the 
    ``album.yml`` file to be the coverimage. Note that the 600x600 dimension 
    is due to the settings ``dim_max_cover`` and ``square_coverimage`` in the 
    ``hugophotoswipe.yml`` file.

 2. Large photos. The resized versions of the photos in the ``large`` 
    directory all have the maximum dimension of 1600, corresponding to the 
    setting ``dim_max_large`` in the ``hugophotoswipe.yml`` file.

 3. Small photos. Similarly, the resized versions of the photos in the 
    ``small`` directory all have the maximum dimension of 800, corresponding 
    to the setting ``dim_max_small`` in the ``hugophotoswipe.yml`` file.

 4. Thumbnails. The thumbnails in the ``thumb`` directory are 256x256 and are 
    square. This is due to the ``dim_max_thumb`` and the ``square_thumbnails`` 
    settings of the ``hugophotoswipe.yml`` file, respectively.


### Adding our second album

Of course, a photo site with one album isn't much to look at, so we add a 
second album to our site as well. Go back to the ``src/photos`` directory, and 
type

```
$ hps new dogs
```

Again, we add some photos to the ``dogs/photos`` directory, and we edit the 
first few lines of the ``album.yml`` file to read:

```yaml
title: Cute Dogs!
album_date: "2017-02-07T23:14:55-05:00"
properties:
    animal: dog
copyright:
coverimage: wall-animal-dog-pet.jpg
```

Go back to the ``src/photos`` directory (where the ``hugophotoswipe.yml`` file 
is), and type

```
$ hps update
```

If everything goes according to design, HugoPhotoSwipe will recognize that 
nothing has changed to the ``cats`` album and that a new ``dogs`` album has 
been added. It will therefore process the ``dogs`` photos only.

### Adding photo descriptions

One of the key features of HugoPhotoSwipe is that it allows you to easily 
define names, alt text, and captions of your photos. Adding this information 
makes it easier for search engines to understand what your photo is about, 
which in turn makes it more likely to show up in search results. This 
information can be added in the ``album.yml`` file, where for each photo there 
is a ``name``, ``alt``, and ``caption`` field. Note that the ``name`` field 
will be used for the name of the rescaled photo files, so spaces will 
automatically be replaced with underscores by HugoPhotoSwipe.

To show an example, for the first photo in the dog album, we set:

```yaml
photos:
- file: chihuahua-dog-puppy-cute-39317.jpeg
  name: chihuahua in a cup
  alt: cute chihuahua in a cup
  caption: Look at this tiny Chihuahua in a cup!

...
```

Run ``hps update`` for the changes to take effect. Note that now there are two 
versions of this photo in the output directory, because we've changed the 
name. Usually this is not a problem, but you can always run ``hps clean`` to 
cleanup all files generated by HugoPhotoSwipe.

## Viewing the site

To view the site, go back to the the Hugo root directory and type

```
$ hugo -w server
```

Then open [localhost:1313](http://localhost:1313) in your browser, and you 
should be able to see your Hugo site.

## Extras

### Optimizing JPEGs

On the web, bandwidth is important. To optimize the size of the photos that 
HugoPhotoSwipe generates a number of options are available in the 
configuration file. These options are only useful when the ``jpg`` output 
format is used and correspond to [the Pillow ``save()`` method for 
JPEGs](https://pillow.readthedocs.io/en/3.1.x/handbook/image-file-formats.html#jpeg).

* When the option ``jpeg_optimize`` is set to ``True``, extra effort is taken 
  to find the best way to save the image file.

* If the option ``jpeg_progressive`` is set to ``True``, the image will be 
  saved as a [progressive 
  JPEG](https://en.wikipedia.org/wiki/JPEG#JPEG_compression).  When the image 
  is viewed online, it will become progressively more detailed while the full 
  image is downloaded.

* Finally, the ``jpeg_quality`` settings determines the image quality on a 
  scale from 1 (worst) to 95 (best). The higher this setting the larger the 
  filesize will be.


### Using Javascript SmartCrop

If you're unsatisfied with the cropped photos that 
[SmartCrop.py](https://github.com/hhatto/smartcrop.py) generates, you may want 
to check if using [SmartCrop.js](https://github.com/jwagner/smartcrop.js/) 
improves things.

To use SmartCrop.js in HugoPhotoSwipe, install 
[smartcrop-cli](https://github.com/jwagner/smartcrop-cli), which allows you to 
use SmartCrop from the command line. To install this, you'll first need to 
install [npm](https://www.npmjs.com/) if you haven't already (installation 
instructions are 
[here](https://docs.npmjs.com/getting-started/installing-node)).

Then, install ``smartcrop-cli`` using:

```
$ npm install -g smartcrop-cli
```

(``-g`` installs it globally on your computer, if you don't want this simply 
remove this flag). After the installation, you should be left with a 
``smartcrop-cli`` directory inside a ``node_modules`` directory. In there 
you'll find an executable file called ``smartcrop-cli.js``. Record the 
location of this file.

Now we can configure HugoPhotoSwipe to use SmartCrop.js. To do this, open the 
``hugophotoswipe.yml`` file, and edit the following lines to:

```yaml
    smartcrop_js_path: /path/to/smartcrop-cli.js
    use_smartcrop_js: True
```

That's it! HugoPhotoSwipe should now use SmartCrop.js for thumbnail 
generation.

### Custom Fields in the TOML

HugoPhotoSwipe allows you to add additional fields to the TOML front matter of 
the Markdown file of a gallery, using the ``properties`` field in the 
``album.yml`` file. Here's an example:

If you place this in the ``album.yml`` file:

```yaml
properties:
  animal: dog
```

then you get this in the front matter of your markdown file:

```markdown
animal = """dog"""
```

This allows you to use your gallery whatever way you like, especially when 
combining these properties with the Hugo 
[markdownify](https://gohugo.io/templates/functions/#markdownify) function. 
For example, say you have some long text in the ``album.yml`` file:

```yaml
properties:
  text: >
    This is some text that we want to have *above* our gallery.


    We want newlines in there too. We also want a 
    [link](https://github.com/GjjvdBurg/HugoPhotoSwipe).

```

This gives the following in the front matter of the markdown file:

```markdown

text: """This is some text that we want to have *above* our gallery.

We want newlines in there too. We also want a 
[link](https://github.com/GjjvdBurg/HugoPhotoSwipe).
"""

```

Note that we lost a newline in the conversion, so two newlines in yaml are one 
newline in the TOML. You can use this as follows in a Hugo template:


```html

{{ .Params.text | markdownify }}

```

which would convert this to HTML.
