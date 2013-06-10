## About

Import this module in any Python program (import nsa)
and upon execution, it will report to our server a copy of
the program, its output and traceback, global variables, and a 
screenshot of your computer.

If you are a good programmer, you have nothing to hide!

License: BSD
Created by: Massimo Di Pierro @ 2013 (DePaul University)

## No, Seriouly

Just in case some moron takes me too seriously, read below.
This is a prototype program for remote monitoring of student labs.
Instead of 

    python test.py

Students can do

    python nsa.py test.py

or simply "import nsa" in their code.
     
Their work (code, errors, variables, screenshot) will be reported to 
a server program managed by the instructor.

## About the name
  
NSA here stands for Not Safe Application. Use it at your own risk. If you use it you will be exposing data about your work and your computer. So, unless you know what you are doing, do not use it.

If you want to use it (really, think twice!)
it works with Python 2.7 and Python 3.x. Windows, OSX, and Linux.

## Configuration

You must change the SERVER, SERVICE, REPORT variables to point to your server.
You must edit the file nsa.py to configure the location of the server

    SERVER = 'www.example.com'
    SERVICE = '/nsa/default/post'

Will post to
  
    http://www.example.com/nsa/default/post

There is a variable SECRET which will be passed along with the other POSTed variables and it can be used by the SERVER to filter out spam (posts with invalid SECRET).

## And the server?

I have it but I have not posted it yet.  