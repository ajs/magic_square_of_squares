# magic_square_of_squares
A tool for searching for magic squares of squared values

#Concept of a "step"
The command-line-argument `--step` (`-s`) allows you to set a starting point.
By defualt, the program starts at step 9, meaning that the highest value in
the resulting square will be 9*9 or 81. This is an easily searched result,
so it finishes quickly and moves on to 10.

For each step, every square checked will have the square of the current step
in it (because all other squares have either already been checked, or
were deliberately skipped by use of the `--step` flag.

#Examples

    $ python mss_finder.py -u 10
    At step 9
    At step 10
    At step 11
    At step 12
    10 seconds in, after 2412783 tests
    Current square is:
                       /= 166
          1     4    49  = 54
          9    81   100  = 190
         36    25   144  = 205
       ---------------- \= 226
         46   110   293

     Rows work:
                        /= 189
          4    25   144  = 173
         16    36   121  = 173
          9    64   100  = 173
       ---------------- \= 140
         29   125   365

     This is the last row-only update.
     20 seconds in, after 4830536 tests
     Current square is:
                        /= 74
          4   144    16  = 164
         64    49    25  = 138
          9   121    81  = 211
       ---------------- \= 134
         77   314   122

     ... and so on


Here are some other interesting command-lines:

##Search starting from 1000

    $ python mss_finder.py --step 1000

##Search starting from 1000, randomly

    $ python mss_finder.py -s 1000 -r

##Print a status update every second

    $ python mss_finder.py -u 1

##Using the `-t` flag

This flag lets you exit after a set number of permutations are checked.

    $ while true ; do python mss_finder.py -u 60 -t 1000000 -s $RANDOM -r || continue; echo "WE DID IT\!\!\!"; break; done
    At step 17629
    At step 6091
    At step 14787
    At step 23375
    At step 10218

This particular command-line relies on features of the bash shell, but most command-line environments can do something similar.

#As a library

The mss_finder.py file is a valid python module. If imported, it can be used like so:

    import mss_finder

    finder = mss_finder.SquareSquareFinder(
      random_combinations=False,
      update=0,
      quiet=True,
      verbose=False)
    finished_square = finder.find(step=9)
    # and wait a few centuries...

