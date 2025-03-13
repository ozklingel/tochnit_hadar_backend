import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="/home/ubuntu/flaskapp/.env")
load_dotenv()

SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
print ("SQLALCHEMY_DATABASE_URI",SQLALCHEMY_DATABASE_URI)  #
SECRET_KEY = os.getenv("SECRET_KEY")# #
AWS_secret_access_key =os.getenv("AWS_secret_access_key")  
AWS_access_key_id =os.getenv("AWS_access_key_id") 
BUCKET = os.getenv("BUCKET") 
BUCKET_PATH=os.getenv("BUCKET_PATH") 
TH_PNG=os.getenv("TH_PNG")
GREENAPI_FILE=os.getenv("GREENAPI_FILE")
GREENAPI_NO_FILE=os.getenv("GREENAPI_NO_FILE")
GREENAPI_INSTANCE=os.getenv("GREENAPI_INSTANCE")
GREENAPI_TOKEN=os.getenv("GREENAPI_TOKEN")

class SendMessages:
    class Whatsapp:
        joni_text: str = "text"
        joni_to: str = "to"
        messagePrefix: str = "הודעה מאת: "
        webhook: str = os.getenv("WEB_HOOK")

    class Sms:
        error_message_019: str = (
            "unverified source number - you can verify this number with verify_phone request"
        )
        at_least_one_error: str = "At least one error cause"
        message_add_to_019: str = "numbers to add to 019 api: "
        problem_sms_wasnt_sent: str = (
            "problem, message wasn't sent, please handle this problem"
        )
        url: str = "https://019sms.co.il/api"
        url_test: str = "https://019sms.co.il/api/test"
        username: str = os.getenv("SMS_USER_NAME")

        token: str = os.getenv("SMS_TOKEN")
        token_expiration_date: "14/02/2026 12:40:17" # type: ignore


Authorization_is_On = False