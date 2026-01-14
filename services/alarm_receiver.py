"""Broadcast receiver service for handling alarm triggers"""
from services.notification_service import NotificationService
from database.db_manager import ReminderDB
import platform
import os


def on_alarm_triggered(alarm_id: int, event_date: str, note: str):
    """Called when an alarm is triggered
    
    Args:
        alarm_id: The alarm ID that was triggered
        event_date: Date of the train journey
        note: User's reminder note
    """
    print(f"Alarm {alarm_id} triggered for event on {event_date}")
    
    try:
        # Show notification
        notification_service = NotificationService()
        notification_service.show_notification(alarm_id, event_date, note)
        
        # Mark as triggered in database
        db = ReminderDB()
        db.mark_as_triggered(alarm_id)
        db.close()
        
        print(f"Notification sent and alarm {alarm_id} marked as triggered")
        
    except Exception as e:
        print(f"Error handling alarm trigger: {e}")


# For Android integration
def handle_broadcast_receiver():
    """Handle broadcast receiver intent (Android only)"""
    is_android = platform.system() == 'Linux' and 'ANDROID_ROOT' in os.environ
    
    if is_android:
        try:
            from jnius import autoclass
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            
            # Get the intent that triggered this receiver
            activity = PythonActivity.mActivity
            intent = activity.getIntent()
            
            # Extract alarm data from intent
            alarm_id = intent.getIntExtra('alarm_id', -1)
            event_date = intent.getStringExtra('event_date')
            note = intent.getStringExtra('note')
            
            if alarm_id != -1 and event_date:
                on_alarm_triggered(alarm_id, event_date, note)
            
        except Exception as e:
            print(f"Error in broadcast receiver: {e}")
    else:
        print("Not running on Android, skipping broadcast receiver")


if __name__ == '__main__':
    # For testing on desktop
    print("Broadcast receiver module loaded")
