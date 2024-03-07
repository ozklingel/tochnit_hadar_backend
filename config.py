SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:TH@localhost/t_h'
SECRET_KEY = 'test'
AWS_secret_access_key="+r/OQQDQg8LUC4uALmaVTy7VDbGGHODZKRfw9NML"
AWS_access_key_id="AKIAZ27KJ4ZSWO3I7VFD"

eshcolMosadMeet_madad_date='2024-01-01'
tochnitMeet_madad_date='2024-01-01'
doForBogrim_madad_date='2024-01-01'
matzbarmeet_madad_date='2024-01-01'
professionalMeet_madad_date='2024-01-01'
callHorim_madad_date='2024-01-01'
groupMeet_madad_date='2024-01-01'
meet_madad_date='2024-01-01'
call_madad_date='2024-01-01'

call_report="שיחה"
personalMeet_report="מפגש"
groupMeet_report="מפגש_קבוצתי"
basis_report="ביקור בבסיס"
HorimCall_report="שיחת_הורים"
failCall_report="נסיון_כושל"
professional_report="מפגש_מקצועי"#2 חודשים
cenes_report="כנס_שנתי"
matzbar_report ="ישיבת_מצבר"#3 חודשים
hazanatMachzor_report="הזנת_מחזור"
doForBogrim_report="עשייה_לבוגרים"
MelavimMeeting_report="ישיבה_מוסדית"#1 חודשים
MOsadEshcolMeeting_report="ישיבת_מוסד_אשכול"
tochnitMeeting_report="מפגש תוכנית"

#דוחות
mosad_racaz_meeting="mosad_racaz_meeting"
horim_meeting="horim_meeting"
cenes_presence="cenes_presence"
proffesionalMeet_presence="proffesionalMeet_presence"
forgotenApprentice_cnt="forgotenApprentice_cnt"
visitmeets_melave_avg="visitmeets_melave_avg"
visitcalls_melave_avg="visitcalls_melave_avg"
apprenticeMeeting_gap="apprenticeMeeting_gap"
apprenticeCall_gap="apprenticeCall_gap"
matzbarMeeting_gap="matzbarMeeting_gap"
melave_Score="melave_Score"


class SendMessages:
    class Whatsapp:
        joni_text: str = "text"
        joni_to: str = "to"
        messagePrefix: str = "הודעה מאת: "
        webhook: str = "https://tohnithadar-a7d1e-default-rtdb.firebaseio.com//joni/send.json"

    class Sms:
        error_message_019: str = "unverified source number - you can verify this number with verify_phone request"
        at_least_one_error: str = "At least one error cause"
        message_add_to_019: str = "numbers to add to 019 api: "
        problem_sms_wasnt_sent: str = "problem, message wasn't sent, please handle this problem"
        url: str = 'https://019sms.co.il/api'
        url_test: str = "https://019sms.co.il/api/test"
        username: str = "lirangrovas"
        token: str = (
            'eyJ0eXAiOiJqd3QiLCJhbGciOiJIUzI1NiJ9.eyJmaXJzdF9rZXkiOiI2MjI5MiIsInNlY29uZF9rZXkiOiIzNTM2NDc4IiwiaXNzdWVkQ'
            'XQiOiIxNS0wMi0yMDI0IDEyOjQwOjE3IiwidHRsIjo2MzA3MjAwMH0.1DoH8hc3aS3xI-FdT7hc_E0fBW05rtlcuPdsYfGGoUw')
