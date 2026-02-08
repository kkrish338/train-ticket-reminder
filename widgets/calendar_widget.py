"""Modern calendar widget for date selection."""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from datetime import datetime, timedelta
import calendar

# ── Palette (mirrors main.py THEME) ────────────────────────────
_P = {
    'primary':       '#0D47A1',
    'primary_light': '#1565C0',
    'accent':        '#00BFA5',
    'bg':            '#F4F6FA',
    'card':          '#FFFFFF',
    'text_primary':  '#1A1A2E',
    'text_secondary':'#5A5A7A',
    'text_hint':     '#9E9EAF',
    'divider':       '#E8EAF0',
    'disabled_bg':   '#ECECF0',
    'disabled_fg':   '#B0B0C0',
    'today':         '#E3F2FD',
    'selected':      '#0D47A1',
}

def _c(key):
    return get_color_from_hex(_P[key])


class CalendarWidget(BoxLayout):
    """Custom calendar widget with modern styling."""

    def __init__(self, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(6)
        self.callback = callback
        self.current_date = datetime.now() + timedelta(days=60)
        self.selected_date = None
        self.min_date = (datetime.now() + timedelta(days=60)).date()
        self.today = datetime.now().date()
        self._build_ui()

    # ── Build ────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Month / year navigation ─────────────────────────────
        nav = BoxLayout(size_hint_y=None, height=dp(48), padding=[dp(4), 0])

        self.prev_btn = Button(
            text='\u276E', font_size=sp(20), bold=True,
            size_hint_x=0.15, background_normal='',
            background_color=(0, 0, 0, 0), color=_c('primary'),
            on_press=self._prev_month)

        self.month_label = Label(
            text=self._month_year(), size_hint_x=0.7,
            font_size=sp(17), bold=True, color=_c('text_primary'))

        self.next_btn = Button(
            text='\u276F', font_size=sp(20), bold=True,
            size_hint_x=0.15, background_normal='',
            background_color=(0, 0, 0, 0), color=_c('primary'),
            on_press=self._next_month)

        nav.add_widget(self.prev_btn)
        nav.add_widget(self.month_label)
        nav.add_widget(self.next_btn)
        self.add_widget(nav)

        # ── Weekday header row ──────────────────────────────────
        days_row = GridLayout(cols=7, size_hint_y=None, height=dp(32),
                              padding=[dp(4), 0])
        for d in ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']:
            lbl = Label(text=d, font_size=sp(12), bold=True,
                        color=_c('text_hint'))
            days_row.add_widget(lbl)
        self.add_widget(days_row)

        # thin divider
        div = Widget(size_hint_y=None, height=dp(1))
        with div.canvas:
            Color(*_c('divider'))
            div._r = Rectangle(pos=div.pos, size=div.size)
        div.bind(pos=lambda w, v: setattr(w._r, 'pos', v),
                 size=lambda w, v: setattr(w._r, 'size', v))
        self.add_widget(div)

        # ── Calendar grid ───────────────────────────────────────
        self.calendar_grid = GridLayout(
            cols=7, spacing=dp(6), padding=[dp(4), dp(6)],
            size_hint_y=1)
        self.add_widget(self.calendar_grid)

        self._update_calendar()

    # ── Navigation helpers ──────────────────────────────────────
    def _month_year(self):
        return self.current_date.strftime('%B %Y')

    def _prev_month(self, _):
        first = self.current_date.replace(day=1)
        if self.current_date.month == 1:
            prev = first.replace(year=first.year - 1, month=12)
        else:
            prev = first.replace(month=first.month - 1)
        if prev.date() >= self.min_date.replace(day=1):
            self.current_date = prev
            self.month_label.text = self._month_year()
            self._update_calendar()

    def _next_month(self, _):
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(
                year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(
                month=self.current_date.month + 1)
        self.month_label.text = self._month_year()
        self._update_calendar()

    # ── Render day grid ─────────────────────────────────────────
    def _update_calendar(self):
        self.calendar_grid.clear_widgets()
        year  = self.current_date.year
        month = self.current_date.month
        cal   = calendar.monthcalendar(year, month)

        for week in cal:
            for day in week:
                if day == 0:
                    self.calendar_grid.add_widget(Label(text=''))
                    continue

                d = datetime(year, month, day).date()
                selectable = d >= self.min_date
                is_selected = (self.selected_date and
                               d == self.selected_date)

                btn = Button(
                    text=str(day), font_size=sp(14), bold=selectable,
                    background_normal='', background_color=(0, 0, 0, 0))

                if is_selected:
                    # filled primary circle
                    btn.color = (1, 1, 1, 1)
                    self._attach_circle(btn, 'selected')
                elif selectable:
                    btn.color = _c('text_primary')
                    btn.bind(on_press=lambda x, dt=d: self._on_select(dt))
                else:
                    btn.color = _c('disabled_fg')
                    btn.disabled = True

                self.calendar_grid.add_widget(btn)

    def _attach_circle(self, btn, color_key):
        """Draw a coloured circle behind a day button."""
        with btn.canvas.before:
            Color(*_c(color_key))
            btn._circ = RoundedRectangle(pos=btn.pos, size=btn.size,
                                          radius=[dp(20)])
        btn.bind(pos=lambda w, v: setattr(w._circ, 'pos', v),
                 size=lambda w, v: setattr(w._circ, 'size', v))

    def _on_select(self, date_obj):
        self.selected_date = date_obj
        self._update_calendar()          # re-draw to highlight
        if self.callback:
            self.callback(date_obj.strftime('%Y-%m-%d'))


# ── Date picker popup ────────────────────────────────────────────
class DatePickerPopup(Popup):
    """Modern popup wrapping CalendarWidget."""

    def __init__(self, callback=None, **kwargs):
        self.ext_callback = callback

        body = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10))

        # rounded card background
        with body.canvas.before:
            Color(*_c('card'))
            body._bg = RoundedRectangle(pos=body.pos, size=body.size,
                                         radius=[dp(18)])
        body.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                  size=lambda w, v: setattr(w._bg, 'size', v))

        # sub-title
        hint = Label(text='Select a date at least 60 days ahead',
                     font_size=sp(12), color=_c('text_hint'),
                     size_hint_y=None, height=dp(24), halign='center')
        hint.bind(size=hint.setter('text_size'))
        body.add_widget(hint)

        # calendar
        self.cal = CalendarWidget(callback=self._on_date)
        body.add_widget(self.cal)

        # button row
        btn_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(12),
                            padding=[dp(4), dp(4)])

        cancel = Button(text='Cancel', font_size=sp(14), bold=True,
                        background_normal='', background_color=(0, 0, 0, 0),
                        color=_c('text_secondary'),
                        on_press=self.dismiss)
        btn_row.add_widget(cancel)
        body.add_widget(btn_row)

        super().__init__(
            title='', separator_height=0, content=body,
            size_hint=(0.92, 0.72),
            background='', background_color=(0, 0, 0, 0.45),
            **kwargs)

    def _on_date(self, date_str):
        if self.ext_callback:
            self.ext_callback(date_str)
        self.dismiss()
