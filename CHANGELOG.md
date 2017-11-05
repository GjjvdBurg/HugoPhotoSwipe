# Change Log

## Version 0.2.0

- Don't sort photos when writing to YAML (fixes #22).

## Version 0.1.1

- Fix issue #17, bug in cover image path on Windows

## Version 0.1.0

- Update versioning scheme to major/minor/hotfix. In the future the last field 
  will only be used for hotfixes, the minor field for small changes and 
  features, and the major field for backward-incompatible changes.
- Extend unit tests for ``Photo.resize_dims()`` to catch the bug fixed by 
  version 0.0.16.
- Added some documentation to the classes and methods

## Version 0.0.16

- Hotfix for ``resize_dims`` for Python 2, where round returns float instead 
  of int.

## Version 0.0.15

- Changed ``dim_max_`` settings to using a string input field which can take 
  different size specifications. This allows for setting constant width, 
  constant height, or specific size of photos. Updated the documentation to 
  reflect this change.
- Removed the now obsolete ``square_thumbnails`` and ``square_coverimage`` 
  settings
- Added unit test for the ``resize_dims`` method of the ``Photo`` class.

## Version 0.0.14

- Added optional fast mode, with which SmartCrop.py consider less potential 
  crops (closes issue #10)
- Ensure operational flags (verbose, fast) aren't stored in settings file.

## Version 0.0.13

- Added verbose mode

## Version 0.0.12

- Use triple-quoted strings in TOML front matter property fields

## Version 0.0.11

- Speed improvements by using cached_property
- Cosmetic improvements (progressbar, copyright field)
- Documentation improvements (photo shortcode)

## Version 0.0.10

- Bugfix for Windows paths
- Don't include extension in photo name
- Bugfixes for default configurations

Thanks to @halogenica for identifying and fixing these bugs!

## Version 0.0.9

- Allow for non-album directories
- Add settings file validation

## Version 0.0.8

- Added all dependencies to setup.py
- updated installation instructions in readme

## Version 0.0.7

- Added options for non-square coverimages and thumbnails.
- Fix for recognizing EXIF rotation for SmartCrop.js
- Save ``hugophotoswipe.yml`` file on every run.
