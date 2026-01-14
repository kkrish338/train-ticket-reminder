"""Alarm scheduler using Android AlarmManager"""
import platform


class AlarmScheduler:
    """Manages alarm scheduling using Android AlarmManager"""
    
    def __init__(self):
        """Initialize alarm scheduler"""
        self.is_android = platform.system() == 'Linux' and 'ANDROID_ROOT' in os.environ
        
        if self.is_android:
            try:
                from jnius import autoclass
                self.PythonActivity = autoclass('org.kivy.android.PythonActivity')
                self.AlarmManager = autoclass('android.app.AlarmManager')
                self.PendingIntent = autoclass('android.app.PendingIntent')
                self.Intent = autoclass('android.content.Intent')
                self.Context = autoclass('android.content.Context')
            except ImportError:
                print("Warning: pyjnius not available. Alarm scheduling disabled.")
                self.is_android = False
    
    def schedule_alarm(self, alarm_id: int, timestamp_millis: int, event_date: str, note: str) -> bool:
        """Schedule an exact alarm using AlarmManager
        
        Args:
            alarm_id: Unique ID for this alarm
            timestamp_millis: Time to trigger alarm (milliseconds since epoch)
            event_date: Date of the train journey
            note: User's reminder note
        
        Returns:
            True if scheduling successful, False otherwise
        """
        if not self.is_android:
            print(f"[Desktop Mode] Would schedule alarm {alarm_id} for {timestamp_millis}")
            print(f"  Event date: {event_date}")
            print(f"  Note: {note}")
            return True
        
        try:
            context = self.PythonActivity.mActivity
            alarm_manager = context.getSystemService(self.Context.ALARM_SERVICE)
            
            # Create intent with reminder data
            intent = self.Intent()
            intent.setAction('org.trainbook.ALARM_TRIGGERED')
            intent.putExtra('alarm_id', alarm_id)
            intent.putExtra('event_date', event_date)
            intent.putExtra('note', note)
            
            # Create pending intent
            pending_intent = self.PendingIntent.getBroadcast(
                context,
                alarm_id,
                intent,
                self.PendingIntent.FLAG_UPDATE_CURRENT | self.PendingIntent.FLAG_IMMUTABLE
            )
            
            # Schedule exact alarm (requires SCHEDULE_EXACT_ALARM permission on Android 12+)
            alarm_manager.setExactAndAllowWhileIdle(
                self.AlarmManager.RTC_WAKEUP,
                timestamp_millis,
                pending_intent
            )
            
            print(f"Alarm {alarm_id} scheduled successfully for {timestamp_millis}")
            return True
            
        except Exception as e:
            print(f"Error scheduling alarm: {e}")
            return False
    
    def cancel_alarm(self, alarm_id: int) -> bool:
        """Cancel a scheduled alarm
        
        Args:
            alarm_id: ID of the alarm to cancel
        
        Returns:
            True if cancellation successful, False otherwise
        """
        if not self.is_android:
            print(f"[Desktop Mode] Would cancel alarm {alarm_id}")
            return True
        
        try:
            context = self.PythonActivity.mActivity
            alarm_manager = context.getSystemService(self.Context.ALARM_SERVICE)
            
            # Create intent matching the scheduled alarm
            intent = self.Intent()
            intent.setAction('org.trainbook.ALARM_TRIGGERED')
            
            pending_intent = self.PendingIntent.getBroadcast(
                context,
                alarm_id,
                intent,
                self.PendingIntent.FLAG_UPDATE_CURRENT | self.PendingIntent.FLAG_IMMUTABLE
            )
            
            # Cancel the alarm
            alarm_manager.cancel(pending_intent)
            pending_intent.cancel()
            
            print(f"Alarm {alarm_id} cancelled successfully")
            return True
            
        except Exception as e:
            print(f"Error cancelling alarm: {e}")
            return False
    
    def can_schedule_exact_alarms(self) -> bool:
        """Check if app has permission to schedule exact alarms (Android 12+)
        
        Returns:
            True if permission granted, False otherwise
        """
        if not self.is_android:
            return True
        
        try:
            context = self.PythonActivity.mActivity
            alarm_manager = context.getSystemService(self.Context.ALARM_SERVICE)
            
            # Check if canScheduleExactAlarms method exists (Android 12+)
            if hasattr(alarm_manager, 'canScheduleExactAlarms'):
                return alarm_manager.canScheduleExactAlarms()
            
            return True  # Pre-Android 12, no permission needed
            
        except Exception as e:
            print(f"Error checking alarm permission: {e}")
            return False


import os
