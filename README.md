Automatic die tester
====================

Some code that repeatedly rolls a die and determines the result
using image processing. The result is then logged to a file for
postprocessing, e.g. statistical analysis of the die's quality.

To use this, create a template for each of the die sides and place
it in the files 1.png, 2.png, etc.

The arduino code is set up to control a stepper motor through
a stepstick motor driver, and the image grabbing currently uses
gphoto2 to get an image from my DSLR - if your setup is different,
you'll have to adapt the code to reflect that.
