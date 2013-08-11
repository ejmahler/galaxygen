galaxygen
=========

Randomly generate an EVE Online-esque galaxy using Python

Dependencies
-------------
Python 2.7

numpy, scipy, networkx (for graph algorithms)

PyQt4 (to generate the galaxy image)

Usage
-----
Navigate to the folder in a terminal and run "python main.py main". The primary outputs are a pickled version of the generated data called "stars.pickle", and an image called "galaxy.png"

Main.py implements Python's "argparse", so you can type "python main.py --help" to see a full list of options.

The layout algorithm (python main.py layout) is very slow. I intentionlly kept all dependencies out of it (ie networkx and numpy), and as a result, you can optionally run it with pypy for much better performance.

License
-------
Mozilla Public License Version 2.0
See http://www.mozilla.org/MPL/2.0/ for more info
