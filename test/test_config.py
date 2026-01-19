import pytest
import os


class TestConfig:
    """Test cases for config module."""

    def test_default_values_when_env_not_set(self, monkeypatch):
        """Test that default values are used when environment variables are not set."""
        # Clear all environment variables
        for key in ["HSR_BASE_URL", "START_STATION", "END_STATION", "TRAVEL_DATE",
                    "TRAVEL_TIME", "ADULT_COUNT", "CHILD_COUNT", "DISABLED_COUNT",
                    "ELDER_COUNT", "STUDENT_COUNT", "PASSENGER_ID", "PASSENGER_PHONE",
                    "PASSENGER_EMAIL", "HEADLESS", "SLOW_MO"]:
            monkeypatch.delenv(key, raising=False)

        # Test that getenv returns default values
        assert os.getenv("HSR_BASE_URL", "https://irs.thsrc.com.tw/IMINT/") == "https://irs.thsrc.com.tw/IMINT/"
        assert os.getenv("START_STATION", "1") == "1"
        assert os.getenv("END_STATION", "12") == "12"
        assert os.getenv("TRAVEL_DATE", "") == ""
        assert os.getenv("TRAVEL_TIME", "") == ""
        assert int(os.getenv("ADULT_COUNT", "1")) == 1
        assert int(os.getenv("CHILD_COUNT", "0")) == 0
        assert int(os.getenv("DISABLED_COUNT", "0")) == 0
        assert int(os.getenv("ELDER_COUNT", "0")) == 0
        assert int(os.getenv("STUDENT_COUNT", "0")) == 0
        assert os.getenv("PASSENGER_ID", "") == ""
        assert os.getenv("PASSENGER_PHONE", "") == ""
        assert os.getenv("PASSENGER_EMAIL", "") == ""
        assert os.getenv("HEADLESS", "false").lower() == "false"
        assert int(os.getenv("SLOW_MO", "500")) == 500

    def test_env_values_override_defaults(self, mock_env):
        """Test that environment variables override default values."""
        assert os.getenv("HSR_BASE_URL") == "https://irs.thsrc.com.tw/IMINT/"
        assert os.getenv("START_STATION") == "1"
        assert os.getenv("END_STATION") == "12"
        assert os.getenv("TRAVEL_DATE") == "2024/03/15"
        assert os.getenv("TRAVEL_TIME") == "08:00"
        assert int(os.getenv("ADULT_COUNT")) == 2
        assert int(os.getenv("CHILD_COUNT")) == 0
        assert int(os.getenv("DISABLED_COUNT")) == 0
        assert int(os.getenv("ELDER_COUNT")) == 0
        assert int(os.getenv("STUDENT_COUNT")) == 0
        assert os.getenv("PASSENGER_ID") == "A123456789"
        assert os.getenv("PASSENGER_PHONE") == "0912345678"
        assert os.getenv("PASSENGER_EMAIL") == "test@example.com"
        assert os.getenv("HEADLESS").lower() == "true"
        assert int(os.getenv("SLOW_MO")) == 100

    def test_headless_false(self, monkeypatch):
        """Test HEADLESS set to false."""
        monkeypatch.setenv("HEADLESS", "false")
        assert os.getenv("HEADLESS").lower() == "false"

    def test_headless_mixed_case(self, monkeypatch):
        """Test HEADLESS with mixed case."""
        monkeypatch.setenv("HEADLESS", "TrUe")
        assert os.getenv("HEADLESS").lower() == "true"

    def test_stations_dict(self):
        """Test STATIONS dictionary contains all stations."""
        from src.config import STATIONS

        assert len(STATIONS) == 12
        assert STATIONS["1"] == "南港"
        assert STATIONS["2"] == "台北"
        assert STATIONS["3"] == "板橋"
        assert STATIONS["4"] == "桃園"
        assert STATIONS["5"] == "新竹"
        assert STATIONS["6"] == "苗栗"
        assert STATIONS["7"] == "台中"
        assert STATIONS["8"] == "彰化"
        assert STATIONS["9"] == "雲林"
        assert STATIONS["10"] == "嘉義"
        assert STATIONS["11"] == "台南"
        assert STATIONS["12"] == "左營"

    def test_time_values_dict(self):
        """Test TIME_VALUES dictionary contains correct mappings."""
        from src.config import TIME_VALUES

        assert TIME_VALUES["00:00"] == "1201A"
        assert TIME_VALUES["06:00"] == "600A"
        assert TIME_VALUES["08:00"] == "800A"
        assert TIME_VALUES["12:00"] == "1200N"
        assert TIME_VALUES["13:00"] == "100P"
        assert TIME_VALUES["18:00"] == "600P"
        assert TIME_VALUES["23:30"] == "1130P"

    def test_selectors_class_attributes(self):
        """Test Selectors class has all required CSS selectors."""
        from src.config import Selectors

        # Form
        assert Selectors.FORM == "#BookingS1Form"

        # Stations
        assert Selectors.START_STATION == 'select[name="selectStartStation"]'
        assert Selectors.END_STATION == 'select[name="selectDestinationStation"]'

        # Date & Time
        assert Selectors.DEPARTURE_DATE == "#toTimeInputField"
        assert Selectors.RETURN_DATE == "#backTimeInputField"
        assert Selectors.DEPARTURE_TIME == 'select[name="toTimeTable"]'
        assert Selectors.RETURN_TIME == 'select[name="backTimeTable"]'

        # Trip Type
        assert Selectors.TRIP_TYPE == 'select[name="tripCon:typesoftrip"]'
        assert Selectors.CAR_TYPE == 'select[name="trainCon:trainRadioGroup"]'
        assert Selectors.SEAT_PREFERENCE == 'select[name="seatCon:seatRadioGroup"]'

        # Ticket Amounts
        assert Selectors.ADULT_TICKETS == 'select[name="ticketPanel:rows:0:ticketAmount"]'
        assert Selectors.CHILD_TICKETS == 'select[name="ticketPanel:rows:1:ticketAmount"]'
        assert Selectors.DISABLED_TICKETS == 'select[name="ticketPanel:rows:2:ticketAmount"]'
        assert Selectors.ELDER_TICKETS == 'select[name="ticketPanel:rows:3:ticketAmount"]'
        assert Selectors.STUDENT_TICKETS == 'select[name="ticketPanel:rows:4:ticketAmount"]'
        assert Selectors.TEEN_TICKETS == 'select[name="ticketPanel:rows:5:ticketAmount"]'

        # Captcha
        assert Selectors.CAPTCHA_IMAGE == "#BookingS1Form_homeCaptcha_passCode"
        assert Selectors.CAPTCHA_INPUT == "#securityCode"
        assert Selectors.CAPTCHA_REFRESH == "#BookingS1Form_homeCaptcha_reCodeLink"

        # Submit
        assert Selectors.SUBMIT_BUTTON == "#SubmitButton"

        # Error Message
        assert Selectors.ERROR_MESSAGE == "#feedMSG"

        # Step 2
        assert Selectors.STEP2_FORM == "#BookingS2Form"
        assert Selectors.TRAIN_LIST == ".result-listing"
        assert Selectors.TRAIN_RADIO == 'input[name="TrainQueryDataViewPanel:TrainGroup"]'
        assert Selectors.FIRST_TRAIN == 'input[name="TrainQueryDataViewPanel:TrainGroup"]:first-of-type'
        assert Selectors.EARLIER_TRAINS == "#BookingS2Form_TrainQueryDataViewPanel_PreAndLaterTrainContainer_preTrainLink"
        assert Selectors.LATER_TRAINS == "#BookingS2Form_TrainQueryDataViewPanel_PreAndLaterTrainContainer_laterTrainLink"
        assert Selectors.CONFIRM_TRAIN == 'input[name="SubmitButton"]'

        # Step 3
        assert Selectors.STEP3_FORM == "#BookingS3FormSP"
        assert Selectors.PASSENGER_ID_TYPE == "#idInputRadio"
        assert Selectors.PASSENGER_ID == "#idNumber"
        assert Selectors.PASSENGER_PHONE == "#mobilePhone"
        assert Selectors.PASSENGER_EMAIL == "#email"
        assert Selectors.AGREE_CHECKBOX == 'input[name="agree"]'
        assert Selectors.CONFIRM_BOOKING == "#isSubmit"

    def test_config_module_loaded(self):
        """Test that config module loads successfully."""
        from src import config

        # Verify module has expected attributes
        assert hasattr(config, 'BASE_URL')
        assert hasattr(config, 'START_STATION')
        assert hasattr(config, 'END_STATION')
        assert hasattr(config, 'STATIONS')
        assert hasattr(config, 'TIME_VALUES')
        assert hasattr(config, 'Selectors')
