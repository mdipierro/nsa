"""
## About

Import this module in any Pyhton program (import nsa)
and upon execution, it will report to our server a copy of
the program, its traceback, global variables, and a 
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

    python nsa.py test,py

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
"""
from __future__ import print_function # for Python 2.x compatibility
import sys, traceback, urllib, socket, os, time, datetime
import uuid, inspect, webbrowser, getpass
if sys.version[0]=='2': # for Python 2.x
    import httplib 
    urlencode = urllib.urlencode
else: # for Python 3.x
    import http.client as httplib
    urlencode = urllib.parse.urlencode

SECRET = 'abc'
SERVER = 'www.example.com'
SERVICE = '/nsa/default/post'
REPORT = '/nsa/default/report'
MAXCHARS = 100000
SCREENSHOT = True
VERBOSE = True
WARNING = True
OPENWEB = False

def take_screenshot():
    if sys.platform=='darwin':
        os.system("screencapture .screenshot.png")
        return ('png',open('.screenshot.png','rb').read())
    elif 'linux'  in sys.platform:
        import gtk.gdk
        w = gtk.gdk.get_default_root_window()
        sz = w.get_size()
        pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,
                            8,sz[0],sz[1])
        pb = pb.get_from_drawable(w,w.get_colormap(),
                                  0,0,0,0,sz[0],sz[1])
        if (pb != None):
            pb.save(".screenshot.png","png")
        return ('png',open('.screenshot.png','rb').read())
    else: # windows
        try:
            import win32gui, win32ui, win32con, win32api
        except:
            return (None, None)
        hwin = win32gui.GetDesktopWindow()
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
        hwindc = win32gui.GetWindowDC(hwin)
        srcdc = win32ui.CreateDCFromHandle(hwindc)
        memdc = srcdc.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(srcdc, width, height)
        memdc.SelectObject(bmp)
        memdc.BitBlt((0, 0), (width, height), srcdc, 
                     (left, top), win32con.SRCCOPY)
        bmp.SaveBitmapFile(memdc, '.screenshot.bmp')
        return ('bmp',open('.screenshot.bmp','rb').read())

class Writer(object):
    def __init__(self,stdout):
        self.output = ''
        self.stdout = stdout
    def write(self,data):
        self.output+=data
        self.stdout.write(data)

if __name__ == '__main__':
    filename = sys.argv[1]
elif not __file__.endswith(sys.argv[0]):
    try: 
        filename = sys.modules['__main__'].__file__
    except AttributeError:
        filename = '<shell>'
else:
    filename = None

if filename:

    run = dict(
        secret=SECRET,
        username=getpass.getuser(),
        timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        ip=socket.gethostbyname_ex('')[2][0],
        folder=os.getcwd(),
        filename=filename,
        source=open(filename).read() if filename!='<shell>' else '',
        uuid=str(uuid.uuid4()),
        platform=sys.platform,
        version=sys.version,
        traceback='',
        f_locals='[]',
        running_time='',
        screenshot_extension='',
        screenshot_data='',
        stdout='',
        stderr='',
        )
    
    fullname = os.path.join(run['folder'],run['filename'])

    if filename!='<shell>':
        try:
            t0 = time.time()
            sys.stdout = Writer(sys.stdout)
            sys.stderr = Writer(sys.stderr)
            if WARNING: 
                print("WARNING!!!")
                print("the helpme module sendd your code")
                print("and a screenshot to %s" % SERVER)
                print("="*60)
            if VERBOSE: 
                print("Running file: %s" % run['filename'])
                print("Output:")
                print("="*60)
            code = compile(run['source'], run['filename'], "exec")
            exec(code,{},{})
        except:
            run['traceback'] = traceback.format_exc()
            frames = inspect.getinnerframes(sys.exc_info()[2])
            
            if VERBOSE: 
                print("\n"+"="*60)
                print("There was an error:")
                print(run['traceback'])
        if VERBOSE: 
            print("="*60)
        run['running_time'] = time.time()-t0
        run['stdout'] = sys.stdout.output[:MAXCHARS]
        run['stderr'] = sys.stderr.output[:MAXCHARS]
        if VERBOSE:
            print("Execution time: %ssec" % run['running_time'])
        sys.stdout = sys.stdout.stdout
        sys.stderr = sys.stderr.stdout

    if filename=='<shell>':
        frame = inspect.currentframe()
        run['f_locals'] = ', '.join(frame.f_locals.keys())
    elif run['traceback']:
        run['f_locals'] = ', '.join(frames[-1][0].f_locals.keys())

    if SCREENSHOT:
        run['screenshot_extension'],run['screenshot_data'] = \
            take_screenshot()

    try:
        params = urlencode(run)
        headers = {"Content-type":"application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        conn = httplib.HTTPConnection(SERVER)
        conn.request("POST", SERVICE, params, headers)
        response = conn.getresponse()
        if VERBOSE:
            print("Ticket reported %s" % run['uuid'])
        if OPENWEB:
            webbrowser.open_new_tab('http://%s%s/%s' %
                                    (SERVER, REPORT, run['uuid']))
    except:
        if VERBOSE:
            print("Unable to report ticket")
    if run['filename']!='<shell>':
        sys.exit(0)
