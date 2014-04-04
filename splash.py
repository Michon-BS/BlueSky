import pygame as pg   

def show():
# Show splash screen
    pg.init()
    splashimg = pg.image.load('splash.gif')
    splashwin = pg.display.set_mode(splashimg.get_size(),pg.NOFRAME)
    splashwin.blit(splashimg,(0,0))
    pg.display.flip()
    return

def destroy():
    pg.display.quit()               # Kill splash screen
    return
