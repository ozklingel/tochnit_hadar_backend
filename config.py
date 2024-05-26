SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:TH@localhost/t_h'#db/postgres
SECRET_KEY = 'test'
AWS_secret_access_key="+r/OQQDQg8LUC4uALmaVTy7VDbGGHODZKRfw9NML"
AWS_access_key_id="AKIAZ27KJ4ZSWO3I7VFD"
#melave
call_madad_date='2023-01-01'
meet_madad_date='2023-01-01'
groupMeet_madad_date='2023-01-01'
callHorim_madad_date='2023-01-01'
basis_madad_date='2023-01-01'
#mosad
doForBogrim_madad_date='2023-01-01'
matzbarmeet_madad_date='2023-01-01'
professionalMeet_madad_date='2023-01-01'
hazana_madad_date='2023-01-01'
mosadYeshiva_madad_date='2023-01-01'
#eshcol
eshcolMosadMeet_madad_date='2023-01-01'
tochnitMeet_madad_date='2023-01-01'
#ahraih tohnit
cenes_madad_date='2023-01-01'


call_report="שיחה טלפונית"
zoom_report="פגישה מקוונת"
fiveMess_report="5 הודעות"
failCall_report="נסיון כושל"
personalMeet_report="פגישה פיזית"
groupMeet_report="מפגש קבוצתי"
basis_report="ביקור בבסיס"
HorimCall_report="שיחת הורים"

matzbar_report ="ישיבת מצב”ר"#3 חודשים
hazanatMachzor_report="הזנת מחזור"
mahzorMeeting_report="מפגש מחזור"
mahzorShabat_report="שבת מחזור"
doForBogrim_report="עשיה לטובת בוגרים"
professional_report="כנס מלווים מקצועי חודשי"#2 חודשים
MelavimMeeting_report="ישיבה מוסדית"#1 חודשים

MOsadEshcolMeeting_report="ישיבת חודשית עם רכז"
tochnitMeeting_report="ישיבת מלוים ורכזים"
cenes_report="כנס מלווים שנתי"

mosad_reports=[MelavimMeeting_report,matzbar_report,hazanatMachzor_report,doForBogrim_report,professional_report]
eshcol_reports=[MOsadEshcolMeeting_report,tochnitMeeting_report,cenes_report]
reports_as_call=[call_report,zoom_report,fiveMess_report]
report_as_meet=[personalMeet_report,groupMeet_report,basis_report]
report_as_DoForBogrim=[mahzorShabat_report,mahzorMeeting_report,doForBogrim_report]
all_reports=[mahzorShabat_report,mahzorMeeting_report,tochnitMeeting_report,MOsadEshcolMeeting_report,MelavimMeeting_report,
             doForBogrim_report,hazanatMachzor_report,matzbar_report,cenes_report,professional_report,HorimCall_report
             ,basis_report,groupMeet_report,personalMeet_report,failCall_report,fiveMess_report]
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
forgotenApprentice_list= "דוח דו שבועי-חניכים נשכחים"
melave_Score_list=  "דוח  חודשי- ציון מלווים"
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
        token_expiration_date: '14/02/2026 12:40:17'
Ivry_month={"ניסן":"1",
   "אייר": "2",
   "סיוון": "3",
  "תמוז":  "4",
  "אב": "5",
   "אלול": "6",
   "תשרי": "7",
   "חשוון": "8",
   "כסליו": "9",
    "טבת": "10",
    "שבט": "11",
   "אדר א ": "12",
"אדר": "12",
    "אדר ב":"13"}


prev_otp=0