from distutils.core import setup
import matplotlib
import py2exe


##opts = {
##     'py2exe': { "includes" : ["sip", "matplotlib.backends",  "matplotlib.backends.backend_qt4agg",
##                                "matplotlib.figure","pylab", "numpy", "matplotlib.numerix.fft",
##                                "matplotlib.numerix.linear_algebra", "matplotlib.numerix.random_array",
##                                "matplotlib.backends.backend_tkagg"],
##                 'excludes': ['_gtkagg', '_tkagg', '_agg2', '_cairo', '_cocoaagg',
##                              '_fltkagg', '_gtk', '_gtkcairo', ],
##                'dll_excludes': ['libgdk-win32-2.0-0.dll',
##                                  'libgobject-2.0-0.dll']
##               }
##        }

setup(console=['Bluesky.py'],data_files=matplotlib.get_py2exe_datafiles())

##
##
##      \
##      options={ \
##          r'py2exe': {\
##            r'includes': r'ElementConfig', 
##            r'includes': r'ColorConv', 
##            r'includes': r'Tkinter', 
##            r'includes': r're', 
##            r'includes': r'math', 
##            r'includes': r'sys', 
##            r'includes': r'matplotlib', 
##            r'includes': r'mpl_toolkits',
##            r'includes': r'matplotlib.backends.backend_wx')
