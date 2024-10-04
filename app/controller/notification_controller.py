import firebase_admin
from firebase_admin import credentials, messaging
from fastapi import HTTPException

# Initialize Firebase Admin SDK
cred = credentials.Certificate("./expense.json")
firebase_admin.initialize_app(cred)

class NotificationController:
    async def send_notification(request):
        try:
            request_data = await request.json()
            token = request_data.get('token')
            print(firebase_admin.get_app())
            print(f"Token: {token}")
            print(f"Sender ID: {firebase_admin.get_app().project_id}")

            message = messaging.Message(
                notification=messaging.Notification(
                    title="hello",
                    body="Hello rahul here !!",
                ),
                token=token,
            )
            print(message)

            response = messaging.send(messaging.Message(
                notification=messaging.Notification(
                    title="fsfs",
                    body="Hello erqerqe herqwerre !!",
                ),
                token=token,
            ))
            return {"message": "Notification sent", "response": response}

        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail=str(e))
