"""Train Ticket Reminder Android Application — Modern UI"""
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
import random
import os

from database.db_manager import ReminderDB
from widgets.calendar_widget import DatePickerPopup
from services.alarm_scheduler import AlarmScheduler
from services.notification_service import NotificationService
from utils.date_utils import (
    calculate_reminder_date,
    get_notification_timestamp,
    format_date_display,
    validate_future_date,
    get_days_until
)

# ── Colour Palette ──────────────────────────────────────────────
THEME = {
    'primary':       '#0D47A1',   # Deep indigo‑blue
    'primary_light': '#1565C0',
    'primary_dark':  '#0A2E6B',
    'accent':        '#00BFA5',   # Teal accent
    'accent_dark':   '#00897B',
    'danger':        '#E53935',   # Red
    'danger_light':  '#FFCDD2',
    'success':       '#43A047',
    'success_light': '#C8E6C9',
    'warning':       '#FB8C00',
    'warning_light': '#FFF3E0',
    'bg':            '#F4F6FA',   # Soft off‑white
    'card':          '#FFFFFF',
    'text_primary':  '#1A1A2E',
    'text_secondary':'#5A5A7A',
    'text_hint':     '#9E9EAF',
    'divider':       '#E8EAF0',
    'overlay':       '#00000066',
}


def _hex(name):
    """Shorthand to get a colour tuple from the palette."""
    return get_color_from_hex(THEME[name])


def _rounded_bg(widget, color_key, radius=12, alpha=1.0):
    """Attach a rounded-rect background to *widget*; updates on pos/size."""
    c = list(_hex(color_key))
    if alpha != 1.0:
        c[3] = alpha
    with widget.canvas.before:
        Color(*c)
        widget._bg_rect = RoundedRectangle(pos=widget.pos, size=widget.size,
                                            radius=[dp(radius)])
    widget.bind(
        pos=lambda w, v: setattr(w._bg_rect, 'pos', v),
        size=lambda w, v: setattr(w._bg_rect, 'size', v),
    )


def _shadow(widget, radius=12, offset=3, alpha=0.12):
    """Add a subtle drop‑shadow behind *widget*."""
    with widget.canvas.before:
        Color(0, 0, 0, alpha)
        widget._shadow_rect = RoundedRectangle(
            pos=(widget.x + dp(offset), widget.y - dp(offset)),
            size=widget.size, radius=[dp(radius)])
    widget.bind(
        pos=lambda w, v: setattr(w._shadow_rect, 'pos',
                                  (v[0] + dp(offset), v[1] - dp(offset))),
        size=lambda w, v: setattr(w._shadow_rect, 'size', v),
    )


# ── Reusable styled button ─────────────────────────────────────
class StyledButton(Button):
    """A Button with rounded background, optional shadow."""
    def __init__(self, color_key='accent', radius=10, shadow=False, **kw):
        kw.setdefault('background_normal', '')
        kw.setdefault('background_color', (0, 0, 0, 0))  # transparent; we draw our own
        kw.setdefault('color', (1, 1, 1, 1))
        kw.setdefault('bold', True)
        super().__init__(**kw)
        if shadow:
            _shadow(self, radius=radius)
        _rounded_bg(self, color_key, radius=radius)


# ── Home Screen ─────────────────────────────────────────────────
class HomeScreen(Screen):
    """Main screen showing list of reminders."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = ReminderDB()

        root = FloatLayout()

        # -- Soft gradient‑like background
        bg_widget = Widget(size_hint=(1, 1))
        with bg_widget.canvas:
            # top stripe – deep primary
            Color(*_hex('primary'))
            bg_widget._top = Rectangle(pos=(0, 0), size=(100, 100))
            # bottom body – light BG
            Color(*_hex('bg'))
            bg_widget._bot = Rectangle(pos=(0, 0), size=(100, 100))
        def _resize_bg(w, *a):
            w._top.pos  = (w.x, w.top - w.height * 0.28)
            w._top.size = (w.width, w.height * 0.28)
            w._bot.pos  = (w.x, w.y)
            w._bot.size = (w.width, w.height * 0.72)
        bg_widget.bind(pos=_resize_bg, size=_resize_bg)
        root.add_widget(bg_widget)

        # Optional user background image (layered on top)
        if os.path.exists('Background.png'):
            root.add_widget(Image(source='Background.png', fit_mode='fill',
                                  size_hint=(1, 1), opacity=0.08))

        content = BoxLayout(orientation='vertical', padding=0, spacing=0)

        # ── Header ──────────────────────────────────────────────
        header = BoxLayout(size_hint_y=None, height=dp(110), padding=[dp(24), dp(18), dp(24), dp(8)])
        header_inner = BoxLayout(orientation='vertical', spacing=dp(2))

        greeting = Label(text='Your Journeys', font_size=sp(14),
                         color=(1, 1, 1, 0.7), halign='left', valign='bottom',
                         size_hint_y=0.35, bold=False)
        greeting.bind(size=greeting.setter('text_size'))

        title = Label(text='Train Ticket Reminders', font_size=sp(24),
                      color=(1, 1, 1, 1), halign='left', valign='top',
                      size_hint_y=0.65, bold=True)
        title.bind(size=title.setter('text_size'))

        header_inner.add_widget(greeting)
        header_inner.add_widget(title)
        header.add_widget(header_inner)
        content.add_widget(header)

        # ── Scrollable reminders ────────────────────────────────
        self.scroll_view = ScrollView(do_scroll_x=False)
        self.reminders_layout = GridLayout(
            cols=1, spacing=dp(14), size_hint_y=None,
            padding=[dp(18), dp(18), dp(18), dp(90)]
        )
        self.reminders_layout.bind(minimum_height=self.reminders_layout.setter('height'))
        self.scroll_view.add_widget(self.reminders_layout)
        content.add_widget(self.scroll_view)

        root.add_widget(content)

        # ── FAB ─────────────────────────────────────────────────
        fab = Button(
            text='+', size_hint=(None, None), size=(dp(60), dp(60)),
            pos_hint={'right': 0.93, 'y': 0.04},
            background_normal='', background_color=(0, 0, 0, 0),
            font_size=sp(30), bold=True, color=(1, 1, 1, 1),
            on_press=self.go_to_add_screen
        )
        _shadow(fab, radius=30, offset=4, alpha=0.25)
        _rounded_bg(fab, 'accent', radius=30)
        root.add_widget(fab)

        self.add_widget(root)

    # ── helpers ──────────────────────────────────────────────────
    def on_enter(self):
        self.refresh_reminders()

    def refresh_reminders(self):
        self.reminders_layout.clear_widgets()
        reminders = self.db.get_all_reminders()

        if not reminders:
            self._show_empty_state()
        else:
            for r in reminders:
                self._build_card(*r)

    def _show_empty_state(self):
        wrapper = BoxLayout(orientation='vertical', size_hint_y=None,
                            height=dp(300), padding=[dp(32), dp(48)], spacing=dp(14))

        icon = Label(text='\U0001F687', font_size=sp(72), size_hint_y=0.4)

        msg = Label(text='No reminders yet', font_size=sp(20), bold=True,
                    color=_hex('text_secondary'), size_hint_y=0.2,
                    halign='center')
        msg.bind(size=msg.setter('text_size'))

        hint = Label(text='Tap  +  to schedule your first\nticket booking reminder',
                     font_size=sp(14), color=_hex('text_hint'),
                     size_hint_y=0.25, halign='center', valign='top')
        hint.bind(size=hint.setter('text_size'))

        wrapper.add_widget(icon)
        wrapper.add_widget(msg)
        wrapper.add_widget(hint)
        self.reminders_layout.add_widget(wrapper)

    def _build_card(self, reminder_id, event_date, reminder_date, note,
                    alarm_id, is_triggered):
        card = BoxLayout(orientation='vertical', size_hint_y=None,
                         height=dp(152), padding=[dp(18), dp(14)], spacing=dp(6))
        _shadow(card, radius=16, offset=3, alpha=0.08)
        _rounded_bg(card, 'card', radius=16)

        # ── top row: date + delete icon ─────────────────────────
        top_row = BoxLayout(size_hint_y=0.28, spacing=dp(8))
        date_lbl = Label(
            text=f"\U0001F686  {format_date_display(event_date)}",
            font_size=sp(17), bold=True, halign='left',
            color=_hex('text_primary'), size_hint_x=0.82)
        date_lbl.bind(size=date_lbl.setter('text_size'))

        del_btn = Button(
            text='\U0001F5D1', font_size=sp(18),
            size_hint_x=0.18, background_normal='',
            background_color=(0, 0, 0, 0),
            color=_hex('danger'),
            on_press=lambda x, rid=reminder_id, aid=alarm_id:
                self.delete_reminder(rid, aid))
        top_row.add_widget(date_lbl)
        top_row.add_widget(del_btn)
        card.add_widget(top_row)

        # ── divider line ────────────────────────────────────────
        divider = Widget(size_hint_y=None, height=dp(1))
        with divider.canvas:
            Color(*_hex('divider'))
            divider._r = Rectangle(pos=divider.pos, size=divider.size)
        divider.bind(pos=lambda w, v: setattr(w._r, 'pos', v),
                     size=lambda w, v: setattr(w._r, 'size', v))
        card.add_widget(divider)

        # ── note ────────────────────────────────────────────────
        note_lbl = Label(
            text=note if note else 'No note added',
            font_size=sp(14), halign='left', valign='top',
            color=_hex('text_secondary'), size_hint_y=0.30,
            shorten=True, shorten_from='right', max_lines=2)
        note_lbl.bind(size=note_lbl.setter('text_size'))
        card.add_widget(note_lbl)

        # ── status chip ─────────────────────────────────────────
        chip_row = BoxLayout(size_hint_y=0.26, padding=[0, dp(4), 0, 0])
        chip = BoxLayout(size_hint=(None, None), size=(dp(260), dp(28)),
                         padding=[dp(10), dp(2)])

        if is_triggered:
            chip_text = '\u2714  Alarm triggered'
            chip_bg_key = 'success_light'
            chip_fg = _hex('success')
        else:
            days = get_days_until(event_date)
            alarm_days = max(days - 60, 0)
            chip_text = f'\u23F0  Alarm in {alarm_days}d  \u2022  Journey in {days}d'
            chip_bg_key = 'warning_light'
            chip_fg = _hex('warning')

        _rounded_bg(chip, chip_bg_key, radius=14)
        chip_label = Label(text=chip_text, font_size=sp(12), bold=True,
                           color=chip_fg, halign='left')
        chip_label.bind(size=chip_label.setter('text_size'))
        chip.add_widget(chip_label)
        chip_row.add_widget(chip)
        chip_row.add_widget(Widget())  # spacer
        card.add_widget(chip_row)

        self.reminders_layout.add_widget(card)

    def go_to_add_screen(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'add_reminder'

    # ── Delete confirmation ─────────────────────────────────────
    def delete_reminder(self, reminder_id, alarm_id):
        body = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(16))
        _rounded_bg(body, 'card', radius=16)

        icon = Label(text='\u26A0\uFE0F', font_size=sp(40), size_hint_y=0.35)
        msg = Label(text='Delete this reminder?\nThis action cannot be undone.',
                    font_size=sp(15), halign='center',
                    color=_hex('text_secondary'), size_hint_y=0.30)
        msg.bind(size=msg.setter('text_size'))

        btns = BoxLayout(spacing=dp(12), size_hint_y=0.35, padding=[dp(8), 0])

        popup = Popup(title='', separator_height=0, content=body,
                      size_hint=(0.82, 0.38),
                      background='', background_color=(0, 0, 0, 0.5))

        cancel = StyledButton(text='Cancel', color_key='bg', font_size=sp(15),
                              radius=10)
        cancel.color = _hex('text_primary')
        cancel.bind(on_press=popup.dismiss)

        confirm = StyledButton(text='Delete', color_key='danger',
                               font_size=sp(15), radius=10)

        def _do_delete(inst):
            AlarmScheduler().cancel_alarm(alarm_id)
            self.db.delete_reminder(reminder_id)
            self.refresh_reminders()
            popup.dismiss()

        confirm.bind(on_press=_do_delete)

        btns.add_widget(cancel)
        btns.add_widget(confirm)
        body.add_widget(icon)
        body.add_widget(msg)
        body.add_widget(btns)
        popup.open()


# ── Add Reminder Screen ─────────────────────────────────────────
class AddReminderScreen(Screen):
    """Screen for adding new reminders."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = ReminderDB()
        self.scheduler = AlarmScheduler()
        self.selected_date = None

        root = FloatLayout()

        # background
        bg_w = Widget(size_hint=(1, 1))
        with bg_w.canvas:
            Color(*_hex('bg'))
            bg_w._r = Rectangle(pos=bg_w.pos, size=bg_w.size)
        bg_w.bind(pos=lambda w, v: setattr(w._r, 'pos', v),
                  size=lambda w, v: setattr(w._r, 'size', v))
        root.add_widget(bg_w)

        if os.path.exists('Background.png'):
            root.add_widget(Image(source='Background.png', fit_mode='fill',
                                  size_hint=(1, 1), opacity=0.06))

        form = BoxLayout(orientation='vertical',
                         padding=[dp(22), dp(20), dp(22), dp(20)],
                         spacing=dp(16))

        # ── Header bar ──────────────────────────────────────────
        hdr = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(8))

        back_btn = Button(
            text='\u276E', font_size=sp(22), bold=True,
            size_hint=(None, None), size=(dp(44), dp(44)),
            background_normal='', background_color=(0, 0, 0, 0),
            color=_hex('primary'), on_press=self.go_back,
            pos_hint={'center_y': 0.5})

        hdr_title = Label(text='New Reminder', font_size=sp(22), bold=True,
                          color=_hex('text_primary'), halign='left')
        hdr_title.bind(size=hdr_title.setter('text_size'))

        hdr.add_widget(back_btn)
        hdr.add_widget(hdr_title)
        form.add_widget(hdr)

        # ── Date card ────────────────────────────────────────────
        date_card = BoxLayout(orientation='vertical', size_hint_y=None,
                              height=dp(100), padding=dp(16), spacing=dp(8))
        _shadow(date_card, radius=14, alpha=0.06)
        _rounded_bg(date_card, 'card', radius=14)

        date_heading = Label(text='Journey Date', font_size=sp(12), bold=True,
                             color=_hex('text_hint'), halign='left',
                             size_hint_y=0.3)
        date_heading.bind(size=date_heading.setter('text_size'))

        self.date_btn = StyledButton(
            text='\U0001F4C5   Tap to select date', color_key='primary',
            font_size=sp(15), radius=10, size_hint_y=0.7,
            on_press=self.show_calendar)

        date_card.add_widget(date_heading)
        date_card.add_widget(self.date_btn)
        form.add_widget(date_card)

        # ── Note card ────────────────────────────────────────────
        note_card = BoxLayout(orientation='vertical', size_hint_y=None,
                              height=dp(180), padding=dp(16), spacing=dp(8))
        _shadow(note_card, radius=14, alpha=0.06)
        _rounded_bg(note_card, 'card', radius=14)

        note_heading = Label(text='Reminder Note', font_size=sp(12), bold=True,
                             color=_hex('text_hint'), halign='left',
                             size_hint_y=0.12)
        note_heading.bind(size=note_heading.setter('text_size'))

        self.note_input = TextInput(
            hint_text='e.g.  Mumbai \u2192 Delhi, 2 tickets, Sleeper class',
            multiline=True, size_hint_y=0.88,
            background_normal='', background_active='',
            background_color=_hex('bg'),
            foreground_color=_hex('text_primary'),
            hint_text_color=_hex('text_hint'),
            cursor_color=_hex('primary'),
            padding=[dp(14), dp(12)],
            font_size=sp(15))

        note_card.add_widget(note_heading)
        note_card.add_widget(self.note_input)
        form.add_widget(note_card)

        # ── Info banner ──────────────────────────────────────────
        info_box = BoxLayout(size_hint_y=None, height=dp(58),
                             padding=[dp(14), dp(8)], spacing=dp(8))
        _rounded_bg(info_box, 'primary', radius=12, alpha=0.08)

        info_icon = Label(text='\u2139\uFE0F', font_size=sp(20),
                          size_hint_x=0.1)
        self.info_label = Label(
            text='Reminder fires 60 days before journey at 7:45 AM',
            font_size=sp(13), color=_hex('primary'), halign='left',
            valign='center', size_hint_x=0.9)
        self.info_label.bind(size=self.info_label.setter('text_size'))

        info_box.add_widget(info_icon)
        info_box.add_widget(self.info_label)
        form.add_widget(info_box)

        # ── Save button ─────────────────────────────────────────
        self.save_btn = StyledButton(
            text='\u2714   Save Reminder', color_key='accent',
            font_size=sp(17), radius=14, shadow=True,
            size_hint_y=None, height=dp(54),
            on_press=self.save_reminder)
        form.add_widget(self.save_btn)

        # spacer
        form.add_widget(Widget())

        root.add_widget(form)
        self.add_widget(root)

    # ── Calendar ─────────────────────────────────────────────────
    def show_calendar(self, instance):
        DatePickerPopup(callback=self.on_date_selected).open()

    def on_date_selected(self, date_str):
        is_valid, err = validate_future_date(date_str)
        if not is_valid:
            self._popup('Error', err, 'danger')
            return
        self.selected_date = date_str
        self.date_btn.text = f'\U0001F4C5   {format_date_display(date_str)}'
        r_date = calculate_reminder_date(date_str)
        self.info_label.text = (
            f'Reminder on {format_date_display(r_date)} at 7:45 AM'
        )

    # ── Save ─────────────────────────────────────────────────────
    def save_reminder(self, instance):
        if not self.selected_date:
            self._popup('Missing Date', 'Please select a journey date first.', 'warning')
            return
        note = self.note_input.text.strip()
        if not note:
            self._popup('Missing Note', 'Please enter a reminder note.', 'warning')
            return
        try:
            alarm_id = random.randint(1000, 999999)
            r_date = calculate_reminder_date(self.selected_date)
            ts = get_notification_timestamp(r_date, '07:45')
            ok = self.scheduler.schedule_alarm(alarm_id, ts,
                                               self.selected_date, note)
            if ok:
                self.db.add_reminder(self.selected_date, note, alarm_id)
                self._popup('Done!', 'Reminder saved successfully.', 'success')
                self.reset_form()
                Clock.schedule_once(lambda dt: self.go_back(None), 0.8)
            else:
                self._popup('Error', 'Failed to schedule alarm.', 'danger')
        except Exception as e:
            self._popup('Error', str(e), 'danger')

    def reset_form(self):
        self.selected_date = None
        self.date_btn.text = '\U0001F4C5   Tap to select date'
        self.note_input.text = ''
        self.info_label.text = 'Reminder fires 60 days before journey at 7:45 AM'

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'

    # ── Themed popup helper ──────────────────────────────────────
    def _popup(self, title, message, style='primary'):
        body = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(14))
        _rounded_bg(body, 'card', radius=16)

        emoji_map = {'danger': '\u274C', 'warning': '\u26A0\uFE0F',
                     'success': '\u2705', 'primary': '\u2139\uFE0F'}
        icon = Label(text=emoji_map.get(style, ''), font_size=sp(38),
                     size_hint_y=0.3)

        lbl = Label(text=message, font_size=sp(15), halign='center',
                    color=_hex('text_secondary'), size_hint_y=0.35)
        lbl.bind(size=lbl.setter('text_size'))

        ok_btn = StyledButton(text='OK',
                              color_key=style if style != 'warning' else 'accent',
                              font_size=sp(15), radius=10, size_hint_y=0.35)

        p = Popup(title='', separator_height=0, content=body,
                  size_hint=(0.78, 0.34),
                  background='', background_color=(0, 0, 0, 0.45))
        ok_btn.bind(on_press=p.dismiss)

        body.add_widget(icon)
        body.add_widget(lbl)
        body.add_widget(ok_btn)
        p.open()


# ── Application ──────────────────────────────────────────────────
class TrainBookApp(App):
    """Main application class."""

    def build(self):
        Window.clearcolor = _hex('bg')
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(AddReminderScreen(name='add_reminder'))
        return sm

    def on_start(self):
        print("Train Ticket Reminder App Started")
        print("=" * 50)

    def on_stop(self):
        try:
            self.root.get_screen('home').db.close()
            self.root.get_screen('add_reminder').db.close()
        except Exception:
            pass


if __name__ == '__main__':
    TrainBookApp().run()
