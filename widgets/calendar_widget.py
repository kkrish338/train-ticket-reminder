"""Calendar widget for date selection"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from datetime import datetime, timedelta
import calendar


class CalendarWidget(BoxLayout):
    """Custom calendar widget for date selection"""
    
    def __init__(self, callback=None, **kwargs):
        """Initialize calendar widget
        
        Args:
            callback: Function to call when date is selected (receives date string)
        """
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.callback = callback
        # Start calendar from 60 days in the future
        self.current_date = datetime.now() + timedelta(days=60)
        self.selected_date = None
        # Store the minimum selectable date (60 days from today)
        self.min_date = (datetime.now() + timedelta(days=60)).date()
        
        self._build_ui()
    
    def _build_ui(self):
        """Build calendar UI"""
        # Header with month/year and navigation
        header = BoxLayout(size_hint_y=0.15, padding=10)
        
        self.prev_btn = Button(
            text='<',
            size_hint_x=0.2,
            on_press=self._prev_month
        )
        
        self.month_label = Label(
            text=self._get_month_year_text(),
            size_hint_x=0.6,
            font_size='18sp',
            bold=True
        )
        
        self.next_btn = Button(
            text='>',
            size_hint_x=0.2,
            on_press=self._next_month
        )
        
        header.add_widget(self.prev_btn)
        header.add_widget(self.month_label)
        header.add_widget(self.next_btn)
        
        self.add_widget(header)
        
        # Day names header
        day_names = BoxLayout(size_hint_y=0.1)
        for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
            day_names.add_widget(Label(text=day, bold=True))
        self.add_widget(day_names)
        
        # Calendar grid
        self.calendar_grid = GridLayout(cols=7, spacing=5, padding=5)
        self.add_widget(self.calendar_grid)
        
        self._update_calendar()
    
    def _get_month_year_text(self):
        """Get formatted month and year text"""
        return self.current_date.strftime('%B %Y')
    
    def _prev_month(self, instance):
        """Navigate to previous month"""
        # Don't allow navigation before the minimum date's month
        prev_month_date = self.current_date.replace(day=1)
        if self.current_date.month == 1:
            prev_month_date = prev_month_date.replace(year=self.current_date.year - 1, month=12)
        else:
            prev_month_date = prev_month_date.replace(month=self.current_date.month - 1)
        
        # Check if previous month contains any valid dates (>= min_date)
        min_date_month_start = self.min_date.replace(day=1)
        if prev_month_date.date() >= min_date_month_start:
            if self.current_date.month == 1:
                self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month - 1)
            
            self.month_label.text = self._get_month_year_text()
            self._update_calendar()
    
    def _next_month(self, instance):
        """Navigate to next month"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        
        self.month_label.text = self._get_month_year_text()
        self._update_calendar()
    
    def _update_calendar(self):
        """Update calendar grid with days"""
        self.calendar_grid.clear_widgets()
        
        year = self.current_date.year
        month = self.current_date.month
        
        # Get calendar data
        cal = calendar.monthcalendar(year, month)
        
        for week in cal:
            for day in week:
                if day == 0:
                    # Empty cell
                    self.calendar_grid.add_widget(Label(text=''))
                else:
                    date_obj = datetime(year, month, day).date()
                    
                    # Only enable dates that are >= min_date (60 days from today)
                    is_selectable = date_obj >= self.min_date
                    
                    # Create button for day
                    day_btn = Button(
                        text=str(day),
                        background_normal='',
                        background_color=(0.2, 0.6, 0.8, 1) if is_selectable else (0.5, 0.5, 0.5, 0.3)
                    )
                    
                    if is_selectable:
                        day_btn.bind(on_press=lambda x, d=date_obj: self._on_date_select(d))
                    else:
                        day_btn.disabled = True
                    
                    self.calendar_grid.add_widget(day_btn)
    
    def _on_date_select(self, date_obj):
        """Handle date selection
        
        Args:
            date_obj: Selected date object
        """
        self.selected_date = date_obj.strftime('%Y-%m-%d')
        
        if self.callback:
            self.callback(self.selected_date)


class DatePickerPopup(Popup):
    """Popup dialog for date selection"""
    
    def __init__(self, callback=None, **kwargs):
        """Initialize date picker popup
        
        Args:
            callback: Function to call when date is selected
        """
        self.callback = callback
        
        # Create content
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Calendar widget
        self.calendar = CalendarWidget(callback=self._on_date_selected)
        content.add_widget(self.calendar)
        
        # Buttons
        btn_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        
        cancel_btn = Button(
            text='Cancel',
            on_press=self.dismiss
        )
        btn_layout.add_widget(cancel_btn)
        
        content.add_widget(btn_layout)
        
        super().__init__(
            title='Select Journey Date (Min: 60 days ahead)',
            content=content,
            size_hint=(0.9, 0.8),
            **kwargs
        )
    
    def _on_date_selected(self, date_str):
        """Handle date selection from calendar
        
        Args:
            date_str: Selected date string (YYYY-MM-DD)
        """
        if self.callback:
            self.callback(date_str)
        self.dismiss()
