==============
HugoPhotoSwipe
==============

HugoPhotoSwipe is a command line application to easily create and manage 
`PhotoSwipe <http://photoswipe.com/>`_ albums when using the `Hugo 
<https://gohugo.io/>`_ static website generator.

Why?
====

I created my personal website using Hugo, so all source documents are created 
as Markdown files. I wanted to have photo albums on the site as well, using 
the PhotoSwipe viewer. I also wanted to easily set photo descriptions, quickly 
update albums when photos change, and have responsive image sizes and 
thumbnails automatically generated. HugoPhotoSwipe makes all this easily 
possible.

See my blog post `here <https://gertjanvandenburg.com/blog/hugophotoswipe/>`_ 
for more about my motivations for making this tool.

How?
====

PhotoSwipe requires some Javascript and a specific HTML format to work, and 
Hugo generally works with Markdown files. So, this program creates a markdown 
file for Hugo to work with based on Hugo *shortcodes*. These shortcode are 
then used to create the HTML code that PhotoSwipe needs. See the ``docs`` 
directory for the shortcodes.

Installation
------------

HugoPhotoSwipe is available on PyPI, you can install it easily with pip::

    pip install hugophotoswipe

After installation, you should be left with a ``hps`` program.

Usage
-----

First, initialize a new HugoPhotoSwipe directory with::

    hps init

This creates a new HugoPhotoSwipe configuration file, called 
``hugophotoswipe.yml``. This is a `YAML file 
<https://en.wikipedia.org/wiki/YAML>`_.  In this configuration file, you need 
to set at least the ``markdown_dir`` and ``output_dir`` variables.  These are 
respectively the directory where the markdown needs to be placed and the 
directory where the processed photos need to be placed. You may also want to 
set the ``url_prefix`` variable, which is added before the path to the photo 
files.

Second, create a new album using::

    hps new

HugoPhotoSwipe will ask you for the name of the new album, and create a 
directory with that name for you. Try to keep the names short, they are not 
the final title of the album. Spaces in the name are automatically replaced 
with underscores. In the new directory you will find an ``album.yml`` file and 
an empty ``photos`` directory.

At this point, you should place some photos in the ``photos`` directory and 
set the title field of the album in the ``album.yml`` file. You can also set 
the album date, the copyright line, and the filename of the coverimage.  
Key/Value pairs you place under the ``properties`` line will be placed in the 
preamble of the markdown file, so you can use them in Hugo layouts. For 
instance, you may want to add a country field, camera details, etc.

In the main directory (where the ``hugophotoswipe.yml`` file is), you can now 
run::

    hps update

To create the markdown file, the resized photos, and will update the 
``album.yml`` file.  HugoPhotoSwipe creates large and small photo sizes, as 
well as thumbnails using `SmartCrop.py 
<https://github.com/hhatto/smartcrop.py>`_. 

If you now open the ``album.yml`` file, you'll notice that the fields for the 
photos and the hashes have been extended. Under ``photos:`` all the photos in 
the directory will be listed, with for each photo a ``file``, ``name``, 
``alt``, and ``caption`` field. The last three fields can be edited by you.  
Doing this can be useful for SEO of your photos, but is not required. The 
``hashes`` field in the ``album.yml`` file is used to detect changes in the 
photos, and don't need to be edited by you.

Finally, if you want to regenerate all the markdown and resized photos, you 
can always use::

    hps clean

to clean everything. This will of course not touch the original photo files.

Notes
=====

I've noticed that thumbnails are slightly nicer with `SmartCrop.js 
<https://github.com/jwagner/smartcrop.js>`_ than with `SmartCrop.py 
<https://github.com/hhatto/smartcrop.py>`_. So, in the ``hugophotoswipe.yml`` 
file, you can set the option ``use_smartcrop_js`` to ``True`` and the 
``smartcrop_js_path`` to the path of the `smartcrop-cli.js 
<https://github.com/jwagner/smartcrop-cli>`_ utility. This ensures thumbnails 
are created with SmartCrop.js.

HugoPhotoSwipe is free software, licensed under the GNU General Public 
License, version 3 or later (GPLv3). Copyright G.J.J. van den Burg, all rights 
reserved. 

If you have encounter any problems, please open an issue on `GitHub 
<https://github.com/GjjvdBurg/HugoPhotoSwipe>`_.  You can contact me here: 
`@GJJvandenBurg <https://twitter.com/GJJvandenBurg>`_.
