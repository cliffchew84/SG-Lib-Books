import firebase_admin
from firebase_admin import credentials, messaging


class FirebaseMessaging:
    def __init__(self, credential: dict | None = None):
        """
        Initialize Firebase Admin SDK with credentials

        Args:
            credentials_path (str): Path to your Firebase service account key JSON file
        """
        try:
            # Check if already initialized to avoid multiple initializations
            if not firebase_admin._apps:
                cred = credentials.Certificate(credential)
                firebase_admin.initialize_app(cred)
        except Exception as e:
            raise Exception(f"Failed to initialize Firebase Admin SDK: {str(e)}")

    def send_messages(
        self, tokens: list[str], title: str, body: str, data: dict | None = None
    ) -> messaging.BatchResponse:
        """
        Send FCM message to a multiple devices

        Args:
            token (str): The FCM registration token
            title (str): Notification title
            body (str): Notification body
            data (dict, optional): Additional data payload

        Returns:
            str: Message ID if successful
        """
        messages = messaging.MulticastMessage(
            tokens=tokens,
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data if data else {},
        )

        try:
            return messaging.send_each_for_multicast(messages)
        except Exception as e:
            raise Exception(f"Failed to send FCM message: {str(e)}")
