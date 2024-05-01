import warnings

from GUI import PalilaApp


warnings.simplefilter('always', DeprecationWarning)

if __name__ == '__main__':
    PalilaApp('gui_dev').run()
