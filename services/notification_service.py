"""Notification service for displaying reminders"""
import platform
import os


class NotificationService:
    """Manages notification display on Android"""
    
    def __init__(self):
        """Initialize notification service"""
        self.is_android = platform.system() == 'Linux' and 'ANDROID_ROOT' in os.environ
        self.channel_id = 'train_reminders'
        self.channel_name = 'Train Ticket Reminders'
        
        if self.is_android:
            try:
                from jnius import autoclass
                self.PythonActivity = autoclass('org.kivy.android.PythonActivity')
                self.NotificationBuilder = autoclass('android.app.Notification$Builder')
                self.NotificationManager = autoclass('android.app.NotificationManager')
                self.NotificationChannel = autoclass('android.app.NotificationChannel')
                self.Context = autoclass('android.content.Context')
                self.PendingIntent = autoclass('android.app.PendingIntent')
                self.Intent = autoclass('android.content.Intent')
                
                # Create notification channel (required for Android 8.0+)
                self._create_notification_channel()
                
            except ImportError:
                print("Warning: pyjnius not available. Notifications disabled.")
                self.is_android = False
    
    def _create_notification_channel(self):
        """Create notification channel for Android 8.0+"""
        try:
            from jnius import autoclass
            
            context = self.PythonActivity.mActivity
            notification_manager = context.getSystemService(self.Context.NOTIFICATION_SERVICE)
            
            # Create high-priority alarm channel
            channel = self.NotificationChannel(
                self.channel_id,
                self.channel_name,
                self.NotificationManager.IMPORTANCE_HIGH
            )
            channel.setDescription('Train ticket booking alarms')
            channel.enableVibration(True)
            channel.enableLights(True)
            
            # Set vibration pattern for alarm (vibrate: 0ms wait, 1000ms vibrate, 500ms wait, 1000ms vibrate)
            vibration_pattern = [0, 1000, 500, 1000]
            channel.setVibrationPattern(vibration_pattern)
            
            # Enable sound
            channel.setSound(
                autoclass('android.media.RingtoneManager').getDefaultUri(
                    autoclass('android.media.RingtoneManager').TYPE_ALARM
                ),
                autoclass('android.media.AudioAttributes$Builder')()
                    .setUsage(autoclass('android.media.AudioAttributes').USAGE_ALARM)
                    .setContentType(autoclass('android.media.AudioAttributes').CONTENT_TYPE_SONIFICATION)
                    .build()
            )
            
            notification_manager.createNotificationChannel(channel)
            
        except Exception as e:
            print(f"Error creating notification channel: {e}")
    
    def show_notification(self, alarm_id: int, event_date: str, note: str):
        """Display high-priority alarm notification for train ticket booking
        
        Args:
            alarm_id: Unique ID for this notification
            event_date: Date of train journey
            note: User's reminder note
        """
        title = "⚠️ TRAIN TICKET BOOKING ALARM"
        message = f"Book train ticket NOW for {event_date}\n{note}"
        
        if not self.is_android:
            print(f"\n{'='*50}")
            print(f"[ALARM NOTIFICATION {alarm_id}]")
            print(f"Title: {title}")
            print(f"Message: {message}")
            print(f"{'='*50}\n")
            return
        
        try:
            from jnius import autoclass
            
            context = self.PythonActivity.mActivity
            notification_manager = context.getSystemService(self.Context.NOTIFICATION_SERVICE)
            
            # Create full-screen intent to show alarm even when phone is locked
            full_screen_intent = self.Intent(context, self.PythonActivity)
            full_screen_intent.setFlags(
                self.Intent.FLAG_ACTIVITY_NEW_TASK | 
                self.Intent.FLAG_ACTIVITY_CLEAR_TASK |
                self.Intent.FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS
            )
            
            full_screen_pending_intent = self.PendingIntent.getActivity(
                context,
                alarm_id,
                full_screen_intent,
                self.PendingIntent.FLAG_UPDATE_CURRENT | self.PendingIntent.FLAG_IMMUTABLE
            )
            
            # Create regular intent for when notification is tapped
            tap_intent = self.Intent(context, self.PythonActivity)
            tap_intent.setFlags(self.Intent.FLAG_ACTIVITY_NEW_TASK | self.Intent.FLAG_ACTIVITY_CLEAR_TASK)
            
            tap_pending_intent = self.PendingIntent.getActivity(
                context,
                alarm_id + 1,
                tap_intent,
                self.PendingIntent.FLAG_UPDATE_CURRENT | self.PendingIntent.FLAG_IMMUTABLE
            )
            
            # Build high-priority alarm notification
            builder = self.NotificationBuilder(context, self.channel_id)
            builder.setContentTitle(title)
            builder.setContentText(message)
            builder.setSmallIcon(context.getApplicationInfo().icon)
            builder.setContentIntent(tap_pending_intent)
            builder.setFullScreenIntent(full_screen_pending_intent, True)  # Show as full-screen alarm
            builder.setAutoCancel(True)
            builder.setPriority(self.NotificationBuilder.PRIORITY_MAX)
            builder.setCategory(self.NotificationBuilder.CATEGORY_ALARM)
            
            # Make it persistent and ongoing until dismissed
            builder.setOngoing(False)
            
            # Set alarm sound
            RingtoneManager = autoclass('android.media.RingtoneManager')
            alarm_sound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
            builder.setSound(alarm_sound)
            
            # Set vibration pattern (longer and more insistent)
            builder.setVibrate([0, 1000, 500, 1000, 500, 1000])
            
            # LED lights
            builder.setLights(0xFFFF0000, 1000, 500)  # Red light, 1s on, 0.5s off
            
            # For long text, use big text style
            BigTextStyle = autoclass('android.app.Notification$BigTextStyle')
            big_text_style = BigTextStyle()
            big_text_style.bigText(message)
            big_text_style.setBigContentTitle(title)
            builder.setStyle(big_text_style)
            
            # Show notification
            notification_manager.notify(alarm_id, builder.build())
            
            print(f"Alarm notification {alarm_id} displayed successfully")
            
        except Exception as e:
            print(f"Error showing alarm notification: {e}")
