"""Boot receiver service to restore alarms after device reboot"""
from database.db_manager import ReminderDB
from services.alarm_scheduler import AlarmScheduler
from utils.date_utils import get_notification_timestamp
import platform
import os


def restore_alarms_on_boot():
    """Restore all pending alarms after device boot"""
    print("Restoring alarms after boot...")
    
    try:
        db = ReminderDB()
        scheduler = AlarmScheduler()
        
        # Get all pending reminders
        pending_reminders = db.get_pending_reminders()
        
        restored_count = 0
        for reminder in pending_reminders:
            reminder_id, event_date, reminder_date, reminder_time, note, alarm_id = reminder
            
            # Calculate timestamp
            timestamp = get_notification_timestamp(reminder_date, reminder_time)
            
            # Re-schedule alarm
            success = scheduler.schedule_alarm(alarm_id, timestamp, event_date, note)
            
            if success:
                restored_count += 1
                print(f"Restored alarm {alarm_id} for {event_date}")
        
        print(f"Successfully restored {restored_count} alarms")
        db.close()
        
    except Exception as e:
        print(f"Error restoring alarms: {e}")


# For Android BroadcastReceiver integration
def on_boot_completed():
    """Called when device boots (Android only)"""
    is_android = platform.system() == 'Linux' and 'ANDROID_ROOT' in os.environ
    
    if is_android:
        try:
            from jnius import autoclass
            
            # This function will be called by the Java BroadcastReceiver
            restore_alarms_on_boot()
            
        except ImportError:
            print("Warning: pyjnius not available")
    else:
        print("Not running on Android, skipping boot receiver")


if __name__ == '__main__':
    # For testing on desktop
    restore_alarms_on_boot()
