import firebase_admin
from firebase_admin import credentials, messaging

# Initialize Firebase Admin SDK
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)


def send_push_notification(token, title, body, notification_type, notification_id, extra):
    """
    Sends a push notification to a specific device using FCM token.

    Args:
        token (str): The device token to which the notification will be sent.
        title (str): The title of the notification.
        body (str): The body message of the notification.
        notification_type (str): Type of the notification.
        notification_id (str): ID of the notification.
        extra (dict): Additional data to send with the notification.

    Returns:
        response: Firebase messaging response.
    """
    # Create the message payload, including both notification and data
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
        data={
            'notification_type': notification_type,
            'notification_id': notification_id,
            **extra  # Include the extra data
        }
    )

    try:
        # Send the notification
        response = messaging.send(message)
        print(f'Successfully sent message: {response}')
        return response
    except Exception as e:
        print(f'Error sending message: {e}')
        return None