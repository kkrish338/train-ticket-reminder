"""Train Ticket Reminder Android Application"""
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
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


class HomeScreen(Screen):
    """Main screen showing list of reminders"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = ReminderDB()
        
        # Main container with FAB support
        main_layout = FloatLayout()
        
        # Add background image
        if os.path.exists('Background.png'):
            bg_image = Image(
                source='Background.png',
                fit_mode='fill',
                size_hint=(1, 1)
            )
            main_layout.add_widget(bg_image)
        
        # Content layout
        self.layout = BoxLayout(orientation='vertical', padding=0, spacing=0)
        
        # Material Design Header with semi-transparent color
        header = FloatLayout(size_hint_y=0.12)
        with header.canvas.before:
            Color(*get_color_from_hex('#1976D2'), 0.95)  # Material Blue with transparency
            header.rect = RoundedRectangle(
                pos=header.pos,
                size=header.size,
                radius=[0]
            )
        header.bind(pos=lambda i, v: setattr(i.rect, 'pos', v),
                   size=lambda i, v: setattr(i.rect, 'size', v))
        
        title = Label(
            text='🚂 Train Ticket Reminders',
            font_size='22sp',
            bold=True,
            color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        header.add_widget(title)
        self.layout.add_widget(header)
        
        # Reminders list with modern styling
        self.scroll_view = ScrollView()
        self.reminders_layout = GridLayout(
            cols=1,
            spacing=dp(12),
            size_hint_y=None,
            padding=[dp(16), dp(16), dp(16), dp(80)]  # Extra bottom padding for FAB
        )
        self.reminders_layout.bind(minimum_height=self.reminders_layout.setter('height'))
        
        self.scroll_view.add_widget(self.reminders_layout)
        self.layout.add_widget(self.scroll_view)
        
        main_layout.add_widget(self.layout)
        
        # Floating Action Button (FAB)
        fab = Button(
            text='+',
            size_hint=(None, None),
            size=(dp(56), dp(56)),
            pos_hint={'right': 0.95, 'y': 0.05},
            background_normal='',
            background_color=get_color_from_hex('#FF5722'),  # Material Orange
            font_size='28sp',
            bold=True,
            on_press=self.go_to_add_screen
        )
        
        # Make FAB circular
        with fab.canvas.before:
            Color(*get_color_from_hex('#FF5722'))
            fab.circle = RoundedRectangle(
                pos=fab.pos,
                size=fab.size,
                radius=[dp(28)]
            )
        
        # Add shadow effect
        with fab.canvas.before:
            Color(0, 0, 0, 0.3)
            fab.shadow = RoundedRectangle(
                pos=(fab.x + dp(2), fab.y - dp(2)),
                size=fab.size,
                radius=[dp(28)]
            )
        
        fab.bind(
            pos=lambda i, v: [
                setattr(i.circle, 'pos', v),
                setattr(i.shadow, 'pos', (v[0] + dp(2), v[1] - dp(2)))
            ],
            size=lambda i, v: [
                setattr(i.circle, 'size', v),
                setattr(i.shadow, 'size', v)
            ]
        )
        
        main_layout.add_widget(fab)
        self.add_widget(main_layout)
    
    def on_enter(self):
        """Called when screen is displayed"""
        self.refresh_reminders()
    
    def refresh_reminders(self):
        """Refresh the list of reminders"""
        self.reminders_layout.clear_widgets()
        
        reminders = self.db.get_all_reminders()
        
        if not reminders:
            # Modern empty state
            empty_layout = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(200),
                padding=dp(20),
                spacing=dp(10)
            )
            
            empty_icon = Label(
                text='📅',
                font_size='64sp',
                size_hint_y=0.5
            )
            
            empty_text = Label(
                text='No reminders yet',
                font_size='18sp',
                bold=True,
                size_hint_y=0.25,
                color=get_color_from_hex('#757575')
            )
            
            empty_hint = Label(
                text='Tap the + button to create your first reminder',
                font_size='14sp',
                size_hint_y=0.25,
                color=get_color_from_hex('#9E9E9E')
            )
            
            empty_layout.add_widget(empty_icon)
            empty_layout.add_widget(empty_text)
            empty_layout.add_widget(empty_hint)
            
            self.reminders_layout.add_widget(empty_layout)
        else:
            for reminder in reminders:
                reminder_id, event_date, reminder_date, note, alarm_id, is_triggered = reminder
                
                # Modern Material Design Card
                card = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=dp(140),
                    padding=dp(16),
                    spacing=dp(8)
                )
                
                # Card background with shadow and rounded corners
                with card.canvas.before:
                    # Shadow
                    Color(0, 0, 0, 0.1)
                    card.shadow = RoundedRectangle(
                        pos=(card.x + dp(2), card.y - dp(2)),
                        size=card.size,
                        radius=[dp(12)]
                    )
                    # Card background
                    Color(1, 1, 1, 1)
                    card.rect = RoundedRectangle(
                        pos=card.pos,
                        size=card.size,
                        radius=[dp(12)]
                    )
                
                card.bind(
                    pos=lambda i, v: [
                        setattr(i.rect, 'pos', v),
                        setattr(i.shadow, 'pos', (v[0] + dp(2), v[1] - dp(2)))
                    ],
                    size=lambda i, v: [
                        setattr(i.rect, 'size', v),
                        setattr(i.shadow, 'size', v)
                    ]
                )
                
                # Event date with icon
                date_label = Label(
                    text=f"🚆 {format_date_display(event_date)}",
                    bold=True,
                    size_hint_y=0.25,
                    halign='left',
                    font_size='18sp',
                    color=get_color_from_hex('#212121')
                )
                date_label.bind(size=date_label.setter('text_size'))
                
                # Note with icon
                note_label = Label(
                    text=f"📝 {note if note else 'No note'}",
                    size_hint_y=0.25,
                    halign='left',
                    font_size='14sp',
                    color=get_color_from_hex('#616161')
                )
                note_label.bind(size=note_label.setter('text_size'))
                
                # Status with color coding
                if is_triggered:
                    status_text = "✓ Alarm triggered"
                    status_color = get_color_from_hex('#4CAF50')  # Green
                else:
                    days_until = get_days_until(event_date)
                    status_text = f"⏰ Alarm in {days_until - 60} days • Journey in {days_until} days"
                    status_color = get_color_from_hex('#FF9800')  # Orange
                
                status_label = Label(
                    text=status_text,
                    size_hint_y=0.2,
                    halign='left',
                    font_size='13sp',
                    color=status_color
                )
                status_label.bind(size=status_label.setter('text_size'))
                
                # Delete button with modern style
                delete_btn = Button(
                    text='🗑️ Delete',
                    size_hint_y=0.3,
                    background_normal='',
                    background_color=get_color_from_hex('#F44336'),
                    font_size='14sp',
                    on_press=lambda x, rid=reminder_id, aid=alarm_id: self.delete_reminder(rid, aid)
                )
                
                # Rounded delete button
                with delete_btn.canvas.before:
                    Color(*get_color_from_hex('#F44336'))
                    delete_btn.btn_rect = RoundedRectangle(
                        pos=delete_btn.pos,
                        size=delete_btn.size,
                        radius=[dp(8)]
                    )
                
                delete_btn.bind(
                    pos=lambda i, v: setattr(i.btn_rect, 'pos', v),
                    size=lambda i, v: setattr(i.btn_rect, 'size', v)
                )
                
                card.add_widget(date_label)
                card.add_widget(note_label)
                card.add_widget(status_label)
                card.add_widget(delete_btn)
                
                self.reminders_layout.add_widget(card)
    
    def go_to_add_screen(self, instance):
        """Navigate to add reminder screen"""
        self.manager.current = 'add_reminder'
    
    def delete_reminder(self, reminder_id, alarm_id):
        """Delete a reminder
        
        Args:
            reminder_id: Database ID of reminder
            alarm_id: Alarm ID to cancel
        """
        # Confirm deletion
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text='Are you sure you want to delete this reminder?'))
        
        btn_layout = BoxLayout(spacing=10, size_hint_y=0.3)
        
        popup = Popup(
            title='Confirm Delete',
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        def confirm_delete(instance):
            # Cancel alarm
            scheduler = AlarmScheduler()
            scheduler.cancel_alarm(alarm_id)
            
            # Delete from database
            self.db.delete_reminder(reminder_id)
            
            # Refresh list
            self.refresh_reminders()
            popup.dismiss()
        
        cancel_btn = Button(text='Cancel', on_press=popup.dismiss)
        delete_btn = Button(
            text='Delete',
            background_color=(0.8, 0.2, 0.2, 1),
            on_press=confirm_delete
        )
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(delete_btn)
        content.add_widget(btn_layout)
        
        popup.open()


class AddReminderScreen(Screen):
    """Screen for adding new reminders"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = ReminderDB()
        self.scheduler = AlarmScheduler()
        self.selected_date = None
        
        # Main container for background support
        main_container = FloatLayout()
        
        # Add background image
        if os.path.exists('Background.png'):
            bg_image = Image(
                source='Background.png',
                fit_mode='fill',
                size_hint=(1, 1)
            )
            main_container.add_widget(bg_image)
        
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = BoxLayout(size_hint_y=0.08)
        back_btn = Button(
            text='< Back',
            size_hint_x=0.3,
            on_press=self.go_back
        )
        title = Label(
            text='Add New Reminder',
            font_size='20sp',
            bold=True,
            size_hint_x=0.7
        )
        header.add_widget(back_btn)
        header.add_widget(title)
        
        self.layout.add_widget(header)
        
        # Date selection
        date_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        date_layout.add_widget(Label(text='Journey Date:', size_hint_x=0.4))
        self.date_btn = Button(
            text='Select Date',
            size_hint_x=0.6,
            background_color=(0.2, 0.6, 0.8, 1),
            on_press=self.show_calendar
        )
        date_layout.add_widget(self.date_btn)
        
        self.layout.add_widget(date_layout)
        
        # Note input
        self.layout.add_widget(Label(text='Reminder Note:', size_hint_y=0.05))
        self.note_input = TextInput(
            hint_text='E.g., Mumbai to Delhi, 2 tickets',
            multiline=True,
            size_hint_y=0.3
        )
        self.layout.add_widget(self.note_input)
        
        # Info label
        self.info_label = Label(
            text='You will receive a reminder 60 days before\nyour journey date at 7:45 AM',
            size_hint_y=0.1,
            color=(0.7, 0.7, 0.7, 1)
        )
        self.layout.add_widget(self.info_label)
        
        # Save button
        self.save_btn = Button(
            text='Save Reminder',
            size_hint_y=0.12,
            background_color=(0.2, 0.8, 0.4, 1),
            on_press=self.save_reminder
        )
        self.layout.add_widget(self.save_btn)
        
        # Spacer
        self.layout.add_widget(Label(size_hint_y=0.25))
        
        main_container.add_widget(self.layout)
        self.add_widget(main_container)
    
    def show_calendar(self, instance):
        """Show calendar popup for date selection"""
        popup = DatePickerPopup(callback=self.on_date_selected)
        popup.open()
    
    def on_date_selected(self, date_str):
        """Handle date selection from calendar
        
        Args:
            date_str: Selected date string (YYYY-MM-DD)
        """
        # Validate date
        is_valid, error_msg = validate_future_date(date_str)
        
        if not is_valid:
            self.show_error(error_msg)
            return
        
        self.selected_date = date_str
        self.date_btn.text = format_date_display(date_str)
        
        # Update info label with specific dates
        reminder_date = calculate_reminder_date(date_str)
        self.info_label.text = (
            f'Reminder will be sent on {format_date_display(reminder_date)}\n'
            f'at 7:45 AM (60 days before journey)'
        )
    
    def save_reminder(self, instance):
        """Save the reminder"""
        # Validate inputs
        if not self.selected_date:
            self.show_error('Please select a journey date')
            return
        
        note = self.note_input.text.strip()
        if not note:
            self.show_error('Please enter a reminder note')
            return
        
        try:
            # Generate unique alarm ID
            alarm_id = random.randint(1000, 999999)
            
            # Calculate reminder timestamp
            reminder_date = calculate_reminder_date(self.selected_date)
            timestamp = get_notification_timestamp(reminder_date, '07:45')
            
            # Schedule alarm
            success = self.scheduler.schedule_alarm(
                alarm_id,
                timestamp,
                self.selected_date,
                note
            )
            
            if success:
                # Save to database
                self.db.add_reminder(self.selected_date, note, alarm_id)
                
                # Show success message
                self.show_success('Reminder saved successfully!')
                
                # Reset form and go back
                self.reset_form()
                self.go_back(None)
            else:
                self.show_error('Failed to schedule alarm')
        
        except Exception as e:
            self.show_error(f'Error saving reminder: {str(e)}')
    
    def reset_form(self):
        """Reset the form fields"""
        self.selected_date = None
        self.date_btn.text = 'Select Date'
        self.note_input.text = ''
        self.info_label.text = 'You will receive a reminder 60 days before\nyour journey date at 7:45 AM'
    
    def go_back(self, instance):
        """Navigate back to home screen"""
        self.manager.current = 'home'
    
    def show_error(self, message):
        """Show error popup
        
        Args:
            message: Error message to display
        """
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))
        
        popup = Popup(
            title='Error',
            content=content,
            size_hint=(0.8, 0.3)
        )
        
        close_btn = Button(text='OK', size_hint_y=0.3, on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()
    
    def show_success(self, message):
        """Show success popup
        
        Args:
            message: Success message to display
        """
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))
        
        popup = Popup(
            title='Success',
            content=content,
            size_hint=(0.8, 0.3)
        )
        
        close_btn = Button(text='OK', size_hint_y=0.3, on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()


class TrainBookApp(App):
    """Main application class"""
    
    def build(self):
        """Build the application UI"""
        # Set transparent background to show image backgrounds
        Window.clearcolor = (1, 1, 1, 1)
        
        # Create screen manager
        sm = ScreenManager()
        
        # Add screens
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(AddReminderScreen(name='add_reminder'))
        
        return sm
    
    def on_start(self):
        """Called when application starts"""
        print("Train Ticket Reminder App Started")
        print("=" * 50)
    
    def on_stop(self):
        """Called when application stops"""
        # Close database connection
        try:
            self.root.get_screen('home').db.close()
            self.root.get_screen('add_reminder').db.close()
        except:
            pass


if __name__ == '__main__':
    TrainBookApp().run()
