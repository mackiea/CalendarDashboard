import dateutil

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
        # _status = "Loading month " + calendar.month_name[(_day_in_focus.month + 1) % 12]
        _caldash.draw()
        _caldash.day_in_focus = _caldash.day_in_focus + dateutil.relativedelta.relativedelta( months=1)
        _caldash.refresh_calendar()
    elif key == keys.LEFT:
        # _status = "Loading month " + calendar.month_name[(_day_in_focus.month + 1) % 12]
        _caldash.draw()
        _caldash.day_in_focus = _caldash.day_in_focus + dateutil.relativedelta.relativedelta(months=-1)
        _caldash.refresh_calendar()
    _status = ""

_initialized = False
_status = ""
_caldash = None

pgzrun.go()
