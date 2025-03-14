from src.models.report_model import call_report, personalMeet_report, HorimCall_report, matzbar_report, \
    MOsadEshcolMeeting_report

GROUP_MEET_DETAILS = "שלום {0} היקר,יש לבצע פגישה קבוצתית אחת ל60 יום"
PERSONAL_MEET_DETAILS = "שלום {0} היקר,יש לבצע פגישה עם {1}"#not in use
PERSONAL_CALL_DETAILS = "שלום {0} היקר,יש לבצע שיחה עם {1}"#not in use
HORIML_MEET_DETAILS = "שלום {0} היקר,יש לבצע פגישת הורים עם {1}"
BASIS_VISIT_DETAILS = "תזכורת לסבב בסיסים - 3 פעמים בשנה\n\nשלום {0} היקר,יש לבצע 3 סבבי בסיסים בשנה.אין כמו לראות את החניך בבסיס שלו, זה מחבר ומרומם את החניך!  "
EVENT_DETAILS = "משימה שיצרת-{2}\n\nשלום {0} היקר,בתאריך {1} יחול אירוע {2} ל{3}"
BIRTHDAY_DETAILS = "תזכורת יום הולדת בקרוב\n\nשלום {0} היקר,בתאריך {1} יחול יומהולדת  ל{2}.שים לב, שיש לך יכולת להזין לו מתנה בשק״מ של הבסיס, ובכלל להרים טלפון לחניך פשוט מחבר!"

MELAVIM_LOW_SCORE_DETAILS = "שלום {0} היקר,ציון המלוים חשןב להצלחת התוכנית.מלוים עם ציון מתחת ל65 הוא סימן לך {0} בכדי לחנוך אותם מקצועית. \n\nרשימת המלוים:\n\n"
HAZANAT_MAHZOR_DETAILS = "שלום {0} היקר,יש להזין מחזור חדש של תוכנית הדר למערכת"
DO_FOR_BOGRIM_DETAILS = "תזכורת לעשייה לטובת הבוגרים\n\nשלום {0} היקר,יש לבצע בחודש זה עשייה לטובת בוגרים.העשייה בשביל הבוגרים מחברת ומרוממת!"
MATZBAR_DETAILS = "שלום {0} היקר,יש לבצע מפגש עם רכז  עם {1}"#not in use
YESHIVAT_MELAVIM_DETAILS = "תזכורת למפגש מלווים \n\nשלום {0} היקר,יש לבצע בחודש זה ישיבת מלוים מקצועית"
FORGOTTEN_APPRENTICE_DETAILS = "שלום {0} היקר,חניכים נשכחים הם חניכים שלא נוצר איתם קשר ב100 הימים האחרונים.הקשר עם החניך שומר עליו!\n\nרשימת החניכים:\n\n"
LOW_SCORE_MOSDOT_DETAILS = "שלום {0} היקר,ציון המוסדות חשוב להצלחת התוכנית!מוסדות עם ציון מתחת ל65 הן סימן לך {0} בכדי לחנוך מקצועית את רכז המוסד והמלוים.\n\nרשימת המוסדות:\n\n"
CLUSTER_COORD_LOW_SCORE_DETAILS = "שלום {0} היקר,ציון רכזים חשןב להצלחת התוכנית.רכזים עם ציון מתחת ל65 הוא סימן לך {0} בכדי לחנוך אותם מקצועית. \n\nרשימת הרכזים:\n\n"
MOSAD_ESCHOL_MEETING_DETAILS = "שלום {0} היקר,יש לבצע מפגש עם רכז  עם {1}"#not in use
TOCHNIT_MEETING_DETAILS = "שלום {0} היקר,יש לבצע בחודש זה ישיבה עם רכזים ומלוים"

collated_notification_datils={
call_report:"תזכורת שיחה טלפונית לחניכים\n\nשלום {0} היקר,יש לבצע שיחה עם החניכים הבאים:\n",
personalMeet_report:"תזכורת פגישה עם חניכים\n\nשלום {0} היקר,יש לבצע פגישה עם החניכים הבאים:\n",
HorimCall_report:"תזכורת שיחה טפלונית להורים של חניכים\n\nשלום {0} היקר,יש לבצע שיחה טלפונית להורים של החניכים הבאים:\n",
matzbar_report:"תזכורת ישיבת מצב״ר עם מלווים\n\nשלום {0} היקר,יש לבצע כל שלושה חודשים  ישיבת מצב רוחני של כלל החניכים יחד עם המלווים.\n עם מלווים אלה עדיין לא ביצעת:\n",
MOsadEshcolMeeting_report:"תזכורת לישיבה עם רכזים באשכול\n\nשלום {0} היקר,יש לבצע בחודש זה ישיבת רכזים.\n עם רכזים אלה עדיין לא ביצעת:\n"

}