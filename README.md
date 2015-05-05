# Tankoid

Tankoid is a simple clone of the popular Arkanoid/Breakout game. It uses SFML
for almost everything.

The plan for this project is to start with a prototype and improve over time.
It's part of a series of game development experiments. Read more about that
[here](http://bit.ly/1HtltaN). For following the progress, you might want to
visit [the blog](http://bit.ly/1yvEpnE).

## Building

Tankoid comes in two flavors: Python and C++. The following paragraphs contain
instructions for both versions. Choose the one you like!

### Python version

* A Unix-like operating system (sorry Windows peeps; support for your OS will
  come later)
* Python 3.4
* [SFML 2.2](http://www.sfml-dev.org/)
* [PySFML from GitHub](https://github.com/bastienleonard/pysfml-cython),
  installation covered in this readme.

Clone Tankoid:

    git clone https://github.com/TankOs/tankoid
    cd tankoid

I recommend creating a virtual environment, as it eases things, doesn't pollute
your system and doesn't require root access:

    pyvenv virtenv

Now activate the virtual environment (you will have to do this everytime you
want to develop or play Tankoid) and build and install PySFML, which also
requires Cython:

    source virtenv/bin/activate
    pip install cython git+https://github.com/bastienleonard/pysfml-cython

Run the game: (**important:** do not type `./tankoid.py`, as it will invoke the
system's Python interpreter, not the virtual environment's one)

    python tankoid.py

### C++ version

* [CMake 3.2](http://www.cmake.org/)
* [SFML 2.2](http://www.sfml-dev.org/)
* C++11-compliant compiler (for example Clang, GCC or Visual C)

Clone Tankoid:

    git clone https://github.com/TankOs/tankoid
    cd tankoid

Create a dedicated build directory (you can add this directory to your
.git/info/exclude file to prevent adding stuff to the repository) and run
CMake:

    mkdir build && cd build
    cmake ..

Build and run Tankoid:

    clear; make -j && ./tankoid
