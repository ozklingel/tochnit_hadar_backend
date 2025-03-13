from convertdate import hebrew
from hebrew import Hebrew
from pyluach import dates


from datetime import datetime as dt, date, timedelta, datetime

Ivry_month = {
    "ניסן": "1",
    "אייר": "2",
    "סיוון": "3",
    "תמוז": "4",
    "אב": "5",
    "אלול": "6",
    "תשרי": "7",
    "חשוון": "8",
    "כסליו": "9",
    "טבת": "10",
    "שבט": "11",
    "אדר א ": "12",
    "אדר": "12",
    "אדר ב": "13",
}

def hebrew_date_to_greg_date(hebrew_date):
    today = dates.HebrewDate.today()
    birthday_ivry1 = hebrew_date.split(" ")
    try:
        thisYearBirthday = dates.HebrewDate(
            today.year,
            int(Ivry_month[birthday_ivry1[1]]),
            Hebrew(birthday_ivry1[0]).gematria(),
        ).to_greg()
        thisYearBirthday = datetime(
            thisYearBirthday.year, thisYearBirthday.month, thisYearBirthday.day
        )
    except:
        thisYearBirthday=None
    return thisYearBirthday

def get_hebrew_date_from_greg_date(greg_date):
    heb=hebrew.from_gregorian(greg_date.year,greg_date.month,greg_date.day)
    return (heb[0],(heb[1]-6)%12,heb[2])

def get_last_sunday_date_greg():
    # Get the current date
    today = datetime.now()

    # Calculate the number of days since the last Sunday
    days_since_sunday = today.weekday() + 1

    # Calculate the date of the last Sunday
    last_sunday_date = today - timedelta(days=days_since_sunday)
    return last_sunday_date

def get_start_of_year_hebrew_date():
    today = dates.HebrewDate.today()
    if today.month_name()=="אלול":
        return dates.HebrewDate(
            today.year ,
            int(Ivry_month["אלול"]),
            Hebrew("א").gematria(),
        )
    return dates.HebrewDate(
        today.year-1,
        int(Ivry_month["אלול"]),
        Hebrew("א").gematria() ,
    )
def num_of_rivon_passed():
    start_of_year_greg_date_=start_of_year_greg_date()
    gap = (datetime.today() - start_of_year_greg_date_).days
    return int(gap / 90)

def num_of_shlish_passed():
    start_of_year_greg_date_=start_of_year_greg_date()
    gap = (datetime.today() - start_of_year_greg_date_).days
    return int(gap / 120)


def start_of_current_rivon():
    today = dates.HebrewDate.today()
    current_rivon=num_of_rivon_passed()
    if today.month_name()=="תשרי" or today.month_name()=="חשוון":
        HebrewDate_= dates.HebrewDate(
            today.year-1,
            int(Ivry_month["אלול"]),
            Hebrew("א").gematria(),
        ).to_greg()
    else:
        HebrewDate_= dates.HebrewDate(
            today.year,
            (current_rivon*3+6) % 12+1,
            Hebrew("א").gematria() ,
        ).to_greg()
    result=datetime(HebrewDate_.year, HebrewDate_.month, HebrewDate_.day)
    return result
def start_of_current_month():
    today = dates.HebrewDate.today()
    HebrewDate_= dates.HebrewDate(
        today.year,
        today.month,
        Hebrew("א").gematria() ,
    ).to_greg()
    result=datetime(HebrewDate_.year, HebrewDate_.month, HebrewDate_.day)
    return result

def get_start_of_year_greg_date():
    start_Of_year = start_of_year_greg_date()
    start_Of_year_loazi_ = date(start_Of_year.year, start_Of_year.month, start_Of_year.day)
    return start_Of_year_loazi_

def start_of_year_greg_date():
    start_of_year_date =get_start_of_year_hebrew_date().to_greg()
    result=datetime(start_of_year_date.year, start_of_year_date.month, start_of_year_date.day)
    return result


