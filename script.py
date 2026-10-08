from CalendarDashboard import CalendarDashboard

import pgzrun


def draw():
    _caldash.draw()

def update():
    global _initialized, _caldash
    if not _initialized:
        _caldash = CalendarDashboard(screen, clock)
        _initialized = True
    else:
        _caldash.update()

def on_key_down(key):
    global _day_in_focus, _status
    if key == keys.RIGHT:
        _caldash.draw()
        _caldash.skip(1)
        _caldash.refresh_calendar()
    elif key == keys.LEFT:
        _caldash.draw()
        _caldash.skip(-1)
        _caldash.refresh_calendar()
    elif key == keys.UP:
        _caldash.next_mode()
    _status = ""

_initialized = False
_status = ""
_caldash = None

pgzrun.go()
