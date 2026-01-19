# HSR Booking Assistant Configuration
# This file reads values from .env

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# HSR Base URL
BASE_URL = os.getenv("HSR_BASE_URL", "https://irs.thsrc.com.tw/IMINT/")

# Booking Parameters
START_STATION = os.getenv("START_STATION", "1")  # Default: Nangang
END_STATION = os.getenv("END_STATION", "12")     # Default: Zuoying
TRAVEL_DATE = os.getenv("TRAVEL_DATE", "")
TRAVEL_TIME = os.getenv("TRAVEL_TIME", "")

# Ticket Count
ADULT_COUNT = int(os.getenv("ADULT_COUNT", "1"))
CHILD_COUNT = int(os.getenv("CHILD_COUNT", "0"))
DISABLED_COUNT = int(os.getenv("DISABLED_COUNT", "0"))
ELDER_COUNT = int(os.getenv("ELDER_COUNT", "0"))
STUDENT_COUNT = int(os.getenv("STUDENT_COUNT", "0"))

# Passenger Info
PASSENGER_ID = os.getenv("PASSENGER_ID", "")
PASSENGER_PHONE = os.getenv("PASSENGER_PHONE", "")
PASSENGER_EMAIL = os.getenv("PASSENGER_EMAIL", "")

# Browser Settings
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
SLOW_MO = int(os.getenv("SLOW_MO", "500"))

# Trigger Time (optional, empty means immediate execution)
TRIGGER_TIME = os.getenv("TRIGGER_TIME", "")

# Station Mapping (code -> name)
STATIONS = {
    "1": "南港",
    "2": "台北",
    "3": "板橋",
    "4": "桃園",
    "5": "新竹",
    "6": "苗栗",
    "7": "台中",
    "8": "彰化",
    "9": "雲林",
    "10": "嘉義",
    "11": "台南",
    "12": "左營",
}

# ===========================================
# SELECTORS (Parsed from booking page HTML)
# ===========================================

class Selectors:
    """CSS Selectors for HSR booking form elements."""
    
    # Form
    FORM = "#BookingS1Form"
    
    # Stations
    START_STATION = 'select[name="selectStartStation"]'
    END_STATION = 'select[name="selectDestinationStation"]'
    
    # Date & Time
    DEPARTURE_DATE = "#toTimeInputField"
    RETURN_DATE = "#backTimeInputField"
    DEPARTURE_TIME = 'select[name="toTimeTable"]'
    RETURN_TIME = 'select[name="backTimeTable"]'
    
    # Trip Type
    TRIP_TYPE = 'select[name="tripCon:typesoftrip"]'  # 0=單程, 1=去回
    CAR_TYPE = 'select[name="trainCon:trainRadioGroup"]'  # 0=標準, 1=商務
    SEAT_PREFERENCE = 'select[name="seatCon:seatRadioGroup"]'  # 0=無, 1=靠窗, 2=走道
    
    # Ticket Amounts
    ADULT_TICKETS = 'select[name="ticketPanel:rows:0:ticketAmount"]'
    CHILD_TICKETS = 'select[name="ticketPanel:rows:1:ticketAmount"]'
    DISABLED_TICKETS = 'select[name="ticketPanel:rows:2:ticketAmount"]'
    ELDER_TICKETS = 'select[name="ticketPanel:rows:3:ticketAmount"]'
    STUDENT_TICKETS = 'select[name="ticketPanel:rows:4:ticketAmount"]'
    TEEN_TICKETS = 'select[name="ticketPanel:rows:5:ticketAmount"]'
    
    # Captcha
    CAPTCHA_IMAGE = "#BookingS1Form_homeCaptcha_passCode"
    CAPTCHA_INPUT = "#securityCode"
    CAPTCHA_REFRESH = "#BookingS1Form_homeCaptcha_reCodeLink"
    
    # Submit
    SUBMIT_BUTTON = "#SubmitButton"
    
    # Error Message
    ERROR_MESSAGE = "#feedMSG"
    
    # ===========================================
    # STEP 2: Train Selection Page
    # ===========================================
    
    # Step 2 Form
    STEP2_FORM = "#BookingS2Form"
    
    # Train List
    TRAIN_LIST = ".result-listing"
    TRAIN_RADIO = 'input[name="TrainQueryDataViewPanel:TrainGroup"]'
    FIRST_TRAIN = 'input[name="TrainQueryDataViewPanel:TrainGroup"]:first-of-type'
    
    # Earlier/Later trains
    EARLIER_TRAINS = "#BookingS2Form_TrainQueryDataViewPanel_PreAndLaterTrainContainer_preTrainLink"
    LATER_TRAINS = "#BookingS2Form_TrainQueryDataViewPanel_PreAndLaterTrainContainer_laterTrainLink"
    
    # Confirm button
    CONFIRM_TRAIN = 'input[name="SubmitButton"]'
    
    # ===========================================
    # STEP 3: Passenger Info Page
    # ===========================================
    
    # Step 3 Form
    STEP3_FORM = "#BookingS3FormSP"
    
    # Passenger Info
    PASSENGER_ID_TYPE = "#idInputRadio"  # 0=身分證, 1=護照
    PASSENGER_ID = "#idNumber"
    PASSENGER_PHONE = "#mobilePhone"
    PASSENGER_EMAIL = "#email"
    
    # Agreement
    AGREE_CHECKBOX = 'input[name="agree"]'
    
    # Submit
    CONFIRM_BOOKING = "#isSubmit"


# Time Value Mapping (display -> form value)
TIME_VALUES = {
    "00:00": "1201A", "00:30": "1230A",
    "05:00": "500A", "05:30": "530A",
    "06:00": "600A", "06:30": "630A",
    "07:00": "700A", "07:30": "730A",
    "08:00": "800A", "08:30": "830A",
    "09:00": "900A", "09:30": "930A",
    "10:00": "1000A", "10:30": "1030A",
    "11:00": "1100A", "11:30": "1130A",
    "12:00": "1200N", "12:30": "1230P",
    "13:00": "100P", "13:30": "130P",
    "14:00": "200P", "14:30": "230P",
    "15:00": "300P", "15:30": "330P",
    "16:00": "400P", "16:30": "430P",
    "17:00": "500P", "17:30": "530P",
    "18:00": "600P", "18:30": "630P",
    "19:00": "700P", "19:30": "730P",
    "20:00": "800P", "20:30": "830P",
    "21:00": "900P", "21:30": "930P",
    "22:00": "1000P", "22:30": "1030P",
    "23:00": "1100P", "23:30": "1130P",
}
