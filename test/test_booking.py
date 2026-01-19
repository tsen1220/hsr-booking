import pytest
from unittest.mock import Mock, patch, MagicMock, call
from src.booking import BookingAssistant
from playwright.sync_api import TimeoutError as PlaywrightTimeout


class TestBookingAssistant:
    """Test cases for BookingAssistant class."""

    @pytest.fixture
    def assistant(self):
        """Create a BookingAssistant instance with mocked dependencies."""
        with patch('src.booking.CaptchaSolver'):
            return BookingAssistant()

    @pytest.fixture
    def mock_playwright_env(self):
        """Create a fully mocked Playwright environment."""
        mock_page = Mock()
        mock_context = Mock()
        mock_context.new_page.return_value = mock_page
        mock_browser = Mock()
        mock_browser.new_context.return_value = mock_context
        mock_playwright = Mock()
        mock_playwright.chromium.launch.return_value = mock_browser

        return {
            'playwright': mock_playwright,
            'browser': mock_browser,
            'context': mock_context,
            'page': mock_page
        }

    def test_init(self, assistant):
        """Test BookingAssistant initialization."""
        assert assistant.solver is not None
        assert assistant.playwright is None
        assert assistant.browser is None
        assert assistant.context is None
        assert assistant.page is None

    def test_start(self, assistant, mock_playwright_env, capsys):
        """Test start method launches browser successfully."""
        with patch('src.booking.sync_playwright') as mock_sync_playwright:
            mock_sync_playwright.return_value.start.return_value = mock_playwright_env['playwright']

            assistant.start()

            assert assistant.playwright is not None
            assert assistant.browser is not None
            assert assistant.context is not None
            assert assistant.page is not None

            captured = capsys.readouterr()
            assert "Launching browser..." in captured.out
            assert "Browser launched successfully." in captured.out

    def test_open_booking_page_success(self, assistant, capsys):
        """Test open_booking_page with successful page load."""
        assistant.page = Mock()
        assistant.page.goto.return_value = None
        assistant.page.wait_for_load_state.return_value = None

        result = assistant.open_booking_page()

        assert result is True
        assistant.page.goto.assert_called_once()
        assistant.page.wait_for_load_state.assert_called_once_with("domcontentloaded")

        captured = capsys.readouterr()
        assert "Navigating to" in captured.out
        assert "Page loaded successfully!" in captured.out

    def test_open_booking_page_timeout(self, assistant, capsys):
        """Test open_booking_page with timeout error."""
        assistant.page = Mock()
        assistant.page.goto.side_effect = PlaywrightTimeout("Timeout")

        result = assistant.open_booking_page()

        assert result is False
        captured = capsys.readouterr()
        assert "Timeout error" in captured.out

    def test_open_booking_page_exception(self, assistant, capsys):
        """Test open_booking_page with general exception."""
        assistant.page = Mock()
        assistant.page.goto.side_effect = Exception("Network error")

        result = assistant.open_booking_page()

        assert result is False
        captured = capsys.readouterr()
        assert "Error opening page" in captured.out

    def test_dismiss_cookie_dialog_visible(self, assistant, capsys):
        """Test dismiss_cookie_dialog when dialog is visible."""
        assistant.page = Mock()
        mock_cookie_btn = Mock()
        mock_cookie_btn.is_visible.return_value = True
        assistant.page.locator.return_value = mock_cookie_btn

        assistant.dismiss_cookie_dialog()

        mock_cookie_btn.click.assert_called_once()
        captured = capsys.readouterr()
        assert "Cookie dialog dismissed." in captured.out

    def test_dismiss_cookie_dialog_not_visible(self, assistant):
        """Test dismiss_cookie_dialog when dialog is not visible."""
        assistant.page = Mock()
        mock_cookie_btn = Mock()
        mock_cookie_btn.is_visible.return_value = False
        assistant.page.locator.return_value = mock_cookie_btn

        assistant.dismiss_cookie_dialog()

        mock_cookie_btn.click.assert_not_called()

    def test_dismiss_cookie_dialog_exception(self, assistant):
        """Test dismiss_cookie_dialog when exception occurs."""
        assistant.page = Mock()
        assistant.page.locator.side_effect = Exception("Element not found")

        assistant.dismiss_cookie_dialog()

    def test_fill_booking_form(self, assistant, capsys):
        """Test fill_booking_form with all parameters."""
        assistant.page = Mock()

        # Set config values to include date and time
        assistant.config["travel_date"] = "2024/03/15"
        assistant.config["travel_time"] = "08:00"

        with patch('src.booking.TIME_VALUES', {'08:00': '800A'}):
            assistant.fill_booking_form()

            assert assistant.page.select_option.call_count >= 3
            assistant.page.evaluate.assert_called()

            captured = capsys.readouterr()
            assert "Filling Booking Form" in captured.out
            assert "Form filled successfully!" in captured.out

    def test_fill_booking_form_without_date_time(self, assistant, monkeypatch):
        """Test fill_booking_form without date and time."""
        assistant.page = Mock()

        # Mock config values to be empty
        with patch('src.booking.TRAVEL_DATE', ''), \
             patch('src.booking.TRAVEL_TIME', ''):
            assistant.fill_booking_form()

        # When no date/time, evaluate should not be called for date
        # but may still be called for other reasons, so we just check it completed

    def test_get_captcha_image(self, assistant, sample_image_bytes):
        """Test get_captcha_image returns image bytes."""
        assistant.page = Mock()
        mock_captcha = Mock()
        mock_captcha.screenshot.return_value = sample_image_bytes
        assistant.page.locator.return_value = mock_captcha

        result = assistant.get_captcha_image()

        assert result == sample_image_bytes
        mock_captcha.screenshot.assert_called_once()

    def test_solve_and_fill_captcha(self, assistant, sample_image_bytes, capsys):
        """Test solve_and_fill_captcha solves and fills captcha."""
        assistant.page = Mock()

        # Mock get_captcha_image
        mock_captcha_img = Mock()
        mock_captcha_img.screenshot.return_value = sample_image_bytes
        assistant.page.locator.return_value = mock_captcha_img

        # Mock captcha input
        mock_captcha_input = Mock()
        mock_captcha_input.input_value.return_value = "ABC123"

        def locator_side_effect(selector):
            from src.config import Selectors
            if selector == Selectors.CAPTCHA_IMAGE:
                return mock_captcha_img
            elif selector == Selectors.CAPTCHA_INPUT:
                return mock_captcha_input
            return Mock()

        assistant.page.locator.side_effect = locator_side_effect

        # Mock solver
        assistant.solver.solve_bytes.return_value = "ABC123"

        with patch('src.booking.time.sleep'):
            result = assistant.solve_and_fill_captcha()

        assert result == "ABC123"
        mock_captcha_input.fill.assert_called_once_with("ABC123")

        captured = capsys.readouterr()
        assert "Solving Captcha" in captured.out
        assert "Captcha recognized: ABC123" in captured.out

    def test_refresh_captcha(self, assistant):
        """Test refresh_captcha clicks refresh button."""
        assistant.page = Mock()

        with patch('src.booking.time.sleep'):
            assistant.refresh_captcha()

        assistant.page.click.assert_called_once()

    def test_submit_form(self, assistant, capsys):
        """Test submit_form clicks submit button."""
        assistant.page = Mock()

        assistant.submit_form()

        assistant.page.click.assert_called_once()
        assistant.page.wait_for_load_state.assert_called_once_with("domcontentloaded")

        captured = capsys.readouterr()
        assert "Submitting Form" in captured.out

    def test_check_for_errors_visible(self, assistant):
        """Test check_for_errors when error message is visible."""
        assistant.page = Mock()
        mock_error = Mock()
        mock_error.is_visible.return_value = True
        mock_error.inner_text.return_value = "驗證碼錯誤"
        assistant.page.locator.return_value = mock_error

        result = assistant.check_for_errors()

        assert result == "驗證碼錯誤"

    def test_check_for_errors_not_visible(self, assistant):
        """Test check_for_errors when no error message."""
        assistant.page = Mock()
        mock_error = Mock()
        mock_error.is_visible.return_value = False
        assistant.page.locator.return_value = mock_error

        result = assistant.check_for_errors()

        assert result == ""

    def test_check_for_errors_exception(self, assistant):
        """Test check_for_errors when exception occurs."""
        assistant.page = Mock()
        assistant.page.locator.side_effect = Exception("Element not found")

        result = assistant.check_for_errors()

        assert result == ""

    def test_close(self, assistant):
        """Test close method cleans up resources."""
        assistant.browser = Mock()
        assistant.playwright = Mock()

        assistant.close()

        assistant.browser.close.assert_called_once()
        assistant.playwright.stop.assert_called_once()

    def test_close_with_none_values(self, assistant):
        """Test close when browser and playwright are None."""
        assistant.browser = None
        assistant.playwright = None

        assistant.close()

    def test_is_on_step2_true(self, assistant):
        """Test is_on_step2 when on step 2."""
        assistant.page = Mock()
        mock_form = Mock()
        mock_form.is_visible.return_value = True
        assistant.page.locator.return_value = mock_form

        result = assistant.is_on_step2()

        assert result is True

    def test_is_on_step2_false(self, assistant):
        """Test is_on_step2 when not on step 2."""
        assistant.page = Mock()
        mock_form = Mock()
        mock_form.is_visible.return_value = False
        assistant.page.locator.return_value = mock_form

        result = assistant.is_on_step2()

        assert result is False

    def test_is_on_step2_exception(self, assistant):
        """Test is_on_step2 when exception occurs."""
        assistant.page = Mock()
        assistant.page.locator.side_effect = Exception("Element not found")

        result = assistant.is_on_step2()

        assert result is False

    def test_select_first_train_success(self, assistant, capsys):
        """Test select_first_train with available trains."""
        assistant.page = Mock()

        mock_train = Mock()
        mock_train.is_checked.return_value = False
        mock_train.get_attribute.side_effect = lambda attr: {
            "QueryCode": "123",
            "QueryDeparture": "08:00",
            "QueryArrival": "10:00"
        }.get(attr)

        mock_trains = Mock()
        mock_trains.count.return_value = 3
        mock_trains.first = mock_train

        assistant.page.locator.return_value = mock_trains

        result = assistant.select_first_train()

        assert result is True
        mock_train.click.assert_called_once()

        captured = capsys.readouterr()
        assert "Selecting Train" in captured.out
        assert "Found 3 available trains" in captured.out

    def test_select_first_train_no_trains(self, assistant, capsys):
        """Test select_first_train when no trains available."""
        assistant.page = Mock()

        mock_trains = Mock()
        mock_trains.count.return_value = 0

        assistant.page.locator.return_value = mock_trains

        result = assistant.select_first_train()

        assert result is False

        captured = capsys.readouterr()
        assert "No trains available!" in captured.out

    def test_select_first_train_already_checked(self, assistant):
        """Test select_first_train when first train is already selected."""
        assistant.page = Mock()

        mock_train = Mock()
        mock_train.is_checked.return_value = True
        mock_train.get_attribute.side_effect = lambda attr: {
            "QueryCode": "123",
            "QueryDeparture": "08:00",
            "QueryArrival": "10:00"
        }.get(attr)

        mock_trains = Mock()
        mock_trains.count.return_value = 1
        mock_trains.first = mock_train

        assistant.page.locator.return_value = mock_trains

        result = assistant.select_first_train()

        assert result is True
        mock_train.click.assert_not_called()

    def test_confirm_train_selection(self, assistant, capsys):
        """Test confirm_train_selection clicks confirm button."""
        assistant.page = Mock()

        with patch('src.booking.time.sleep'):
            assistant.confirm_train_selection()

        assistant.page.click.assert_called_once()
        assistant.page.wait_for_load_state.assert_called_once_with("domcontentloaded")

        captured = capsys.readouterr()
        assert "Confirming train selection..." in captured.out
        assert "Train confirmed!" in captured.out

    def test_is_on_step3_true(self, assistant):
        """Test is_on_step3 when on step 3."""
        assistant.page = Mock()
        mock_form = Mock()
        mock_form.is_visible.return_value = True
        assistant.page.locator.return_value = mock_form

        result = assistant.is_on_step3()

        assert result is True

    def test_is_on_step3_false(self, assistant):
        """Test is_on_step3 when not on step 3."""
        assistant.page = Mock()
        mock_form = Mock()
        mock_form.is_visible.return_value = False
        assistant.page.locator.return_value = mock_form

        result = assistant.is_on_step3()

        assert result is False

    def test_is_on_step3_exception(self, assistant):
        """Test is_on_step3 when exception occurs."""
        assistant.page = Mock()
        assistant.page.locator.side_effect = Exception("Element not found")

        result = assistant.is_on_step3()

        assert result is False

    def test_fill_passenger_info(self, assistant, mock_env, capsys):
        """Test fill_passenger_info fills all fields."""
        assistant.page = Mock()

        mock_agree_box = Mock()
        mock_agree_box.is_checked.return_value = False
        assistant.page.locator.return_value = mock_agree_box

        # Set passenger info in config
        assistant.config["passenger_id"] = "A123456789"
        assistant.config["passenger_phone"] = "0912345678"
        assistant.config["passenger_email"] = "test@example.com"

        assistant.fill_passenger_info()

        # Should fill ID, phone, and email (3 calls)
        assert assistant.page.fill.call_count == 3
        mock_agree_box.click.assert_called_once()

        captured = capsys.readouterr()
        assert "Filling Passenger Info" in captured.out
        assert "Passenger info filled!" in captured.out

    def test_fill_passenger_info_already_checked(self, assistant, mock_env):
        """Test fill_passenger_info when checkbox already checked."""
        assistant.page = Mock()

        mock_agree_box = Mock()
        mock_agree_box.is_checked.return_value = True
        assistant.page.locator.return_value = mock_agree_box

        # Set passenger info in config
        assistant.config["passenger_id"] = "A123456789"
        assistant.config["passenger_phone"] = "0912345678"
        assistant.config["passenger_email"] = "test@example.com"

        assistant.fill_passenger_info()

        mock_agree_box.click.assert_not_called()

    def test_fill_passenger_info_without_phone(self, assistant, capsys):
        """Test fill_passenger_info when phone is not provided."""
        assistant.page = Mock()

        mock_agree_box = Mock()
        mock_agree_box.is_checked.return_value = False
        assistant.page.locator.return_value = mock_agree_box

        # Set passenger info in config (phone is empty)
        assistant.config["passenger_id"] = "A123456789"
        assistant.config["passenger_phone"] = ""
        assistant.config["passenger_email"] = "test@example.com"

        assistant.fill_passenger_info()

        # Should only fill ID and email (2 calls, not 3)
        assert assistant.page.fill.call_count == 2

    def test_confirm_booking(self, assistant, capsys):
        """Test confirm_booking clicks confirm button."""
        assistant.page = Mock()

        with patch('src.booking.time.sleep'):
            assistant.confirm_booking()

        assistant.page.click.assert_called_once()
        assistant.page.wait_for_load_state.assert_called_once_with("domcontentloaded")

        captured = capsys.readouterr()
        assert "Confirming Booking" in captured.out
        assert "Booking confirmed!" in captured.out

    def test_run_success_complete_flow(self, assistant, mock_env, capsys):
        """Test run method with successful complete booking flow."""
        with patch.object(assistant, 'start'), \
             patch.object(assistant, 'open_booking_page', return_value=True), \
             patch.object(assistant, 'dismiss_cookie_dialog'), \
             patch.object(assistant, 'fill_booking_form'), \
             patch.object(assistant, 'solve_and_fill_captcha', return_value="ABC123"), \
             patch.object(assistant, 'submit_form'), \
             patch.object(assistant, 'is_on_step2', return_value=True), \
             patch.object(assistant, 'select_first_train', return_value=True), \
             patch.object(assistant, 'confirm_train_selection'), \
             patch.object(assistant, 'is_on_step3', return_value=True), \
             patch.object(assistant, 'fill_passenger_info'), \
             patch.object(assistant, 'confirm_booking'), \
             patch.object(assistant, 'close'), \
             patch('src.booking.time.sleep'), \
             patch('builtins.input'):

            assistant.run(max_captcha_retries=5)

        captured = capsys.readouterr()
        assert "BOOKING COMPLETE!" in captured.out

    def test_run_page_load_failure(self, assistant, capsys):
        """Test run when page fails to load."""
        with patch.object(assistant, 'start'), \
             patch.object(assistant, 'open_booking_page', return_value=False), \
             patch.object(assistant, 'close'):

            assistant.run()

        captured = capsys.readouterr()
        assert "Failed to load page. Exiting..." in captured.out

    def test_run_captcha_retry_success(self, assistant, capsys):
        """Test run with captcha retry that eventually succeeds."""
        with patch.object(assistant, 'start'), \
             patch.object(assistant, 'open_booking_page', return_value=True), \
             patch.object(assistant, 'dismiss_cookie_dialog'), \
             patch.object(assistant, 'fill_booking_form'), \
             patch.object(assistant, 'solve_and_fill_captcha', return_value="ABC123"), \
             patch.object(assistant, 'submit_form'), \
             patch.object(assistant, 'is_on_step2', side_effect=[False, False, True]), \
             patch.object(assistant, 'check_for_errors', side_effect=["驗證碼錯誤", "驗證碼錯誤", ""]), \
             patch.object(assistant, 'refresh_captcha'), \
             patch.object(assistant, 'select_first_train', return_value=True), \
             patch.object(assistant, 'confirm_train_selection'), \
             patch.object(assistant, 'is_on_step3', return_value=True), \
             patch.object(assistant, 'fill_passenger_info'), \
             patch.object(assistant, 'confirm_booking'), \
             patch.object(assistant, 'close'), \
             patch('src.booking.time.sleep'), \
             patch('builtins.input'):

            assistant.run(max_captcha_retries=5)

        captured = capsys.readouterr()
        assert "Attempt 1/5" in captured.out
        assert "Attempt 2/5" in captured.out
        assert "Captcha error - refreshing and retrying..." in captured.out

    def test_run_max_captcha_retries_exceeded(self, assistant, capsys):
        """Test run when max captcha retries exceeded."""
        with patch.object(assistant, 'start'), \
             patch.object(assistant, 'open_booking_page', return_value=True), \
             patch.object(assistant, 'dismiss_cookie_dialog'), \
             patch.object(assistant, 'fill_booking_form'), \
             patch.object(assistant, 'solve_and_fill_captcha', return_value="ABC123"), \
             patch.object(assistant, 'submit_form'), \
             patch.object(assistant, 'is_on_step2', return_value=False), \
             patch.object(assistant, 'check_for_errors', return_value="驗證碼錯誤"), \
             patch.object(assistant, 'refresh_captcha'), \
             patch.object(assistant, 'close'), \
             patch('src.booking.time.sleep'):

            assistant.run(max_captcha_retries=3)

        captured = capsys.readouterr()
        assert "Failed after 3 captcha attempts" in captured.out

    def test_run_non_captcha_error(self, assistant, capsys):
        """Test run when non-captcha error occurs."""
        with patch.object(assistant, 'start'), \
             patch.object(assistant, 'open_booking_page', return_value=True), \
             patch.object(assistant, 'dismiss_cookie_dialog'), \
             patch.object(assistant, 'fill_booking_form'), \
             patch.object(assistant, 'solve_and_fill_captcha', return_value="ABC123"), \
             patch.object(assistant, 'submit_form'), \
             patch.object(assistant, 'is_on_step2', return_value=False), \
             patch.object(assistant, 'check_for_errors', return_value="系統錯誤"), \
             patch.object(assistant, 'close'), \
             patch('src.booking.time.sleep'):

            assistant.run(max_captcha_retries=5)

        captured = capsys.readouterr()
        assert "Non-captcha error:" in captured.out and "stopping" in captured.out

    def test_run_unknown_error(self, assistant, capsys):
        """Test run when unknown error occurs (no error message)."""
        with patch.object(assistant, 'start'), \
             patch.object(assistant, 'open_booking_page', return_value=True), \
             patch.object(assistant, 'dismiss_cookie_dialog'), \
             patch.object(assistant, 'fill_booking_form'), \
             patch.object(assistant, 'solve_and_fill_captcha', return_value="ABC123"), \
             patch.object(assistant, 'submit_form'), \
             patch.object(assistant, 'is_on_step2', return_value=False), \
             patch.object(assistant, 'check_for_errors', return_value=""), \
             patch.object(assistant, 'close'), \
             patch('src.booking.time.sleep'):

            assistant.run(max_captcha_retries=5)

        captured = capsys.readouterr()
        assert "Unknown error after form submission" in captured.out

    def test_run_train_selection_failure(self, assistant, capsys):
        """Test run when train selection fails."""
        with patch.object(assistant, 'start'), \
             patch.object(assistant, 'open_booking_page', return_value=True), \
             patch.object(assistant, 'dismiss_cookie_dialog'), \
             patch.object(assistant, 'fill_booking_form'), \
             patch.object(assistant, 'solve_and_fill_captcha', return_value="ABC123"), \
             patch.object(assistant, 'submit_form'), \
             patch.object(assistant, 'is_on_step2', return_value=True), \
             patch.object(assistant, 'select_first_train', return_value=False), \
             patch.object(assistant, 'close'), \
             patch('src.booking.time.sleep'):

            assistant.run(max_captcha_retries=5)

        captured = capsys.readouterr()
        assert "No available trains to select" in captured.out

    def test_run_step3_not_reached(self, assistant, capsys):
        """Test run when step 3 is not reached."""
        with patch.object(assistant, 'start'), \
             patch.object(assistant, 'open_booking_page', return_value=True), \
             patch.object(assistant, 'dismiss_cookie_dialog'), \
             patch.object(assistant, 'fill_booking_form'), \
             patch.object(assistant, 'solve_and_fill_captcha', return_value="ABC123"), \
             patch.object(assistant, 'submit_form'), \
             patch.object(assistant, 'is_on_step2', return_value=True), \
             patch.object(assistant, 'select_first_train', return_value=True), \
             patch.object(assistant, 'confirm_train_selection'), \
             patch.object(assistant, 'is_on_step3', return_value=False), \
             patch.object(assistant, 'close'), \
             patch('src.booking.time.sleep'):

            assistant.run(max_captcha_retries=5)

        captured = capsys.readouterr()
        assert "Failed to reach passenger info page (Step 3)" in captured.out

    def test_run_exception_handling(self, assistant, capsys):
        """Test run when exception occurs during execution."""
        import traceback

        with patch.object(assistant, 'start', side_effect=Exception("Test error")), \
             patch.object(assistant, 'close') as mock_close, \
             patch.object(traceback, 'print_exc') as mock_print_exc:

            assistant.run()

        captured = capsys.readouterr()
        assert "An error occurred: Test error" in captured.out
        mock_close.assert_called_once()
        mock_print_exc.assert_called_once()

    def test_init_with_custom_config(self):
        """Test initialization with custom config (GUI mode)."""
        custom_config = {
            "base_url": "https://test.com",
            "start_station": "1",
            "end_station": "12",
            "travel_date": "2026/01/25",
            "travel_time": "08:00",
            "adult_count": 2,
            "passenger_id": "A123456789",
            "passenger_email": "test@test.com",
            "passenger_phone": "",
            "headless": True,
            "slow_mo": 100,
        }

        assistant = BookingAssistant(config=custom_config)

        assert assistant.config == custom_config
        assert assistant.on_success is None
        assert assistant.on_error is None

    def test_run_with_callbacks_success(self):
        """Test run with on_success callback (GUI mode)."""
        success_called = []

        def on_success():
            success_called.append(True)

        custom_config = {
            "base_url": "https://irs.thsrc.com.tw/IMINT/",
            "start_station": "2",
            "end_station": "12",
            "travel_date": "2026/01/25",
            "travel_time": "08:00",
            "adult_count": 1,
            "child_count": 0,
            "disabled_count": 0,
            "elder_count": 0,
            "student_count": 0,
            "passenger_id": "A123456789",
            "passenger_email": "test@test.com",
            "passenger_phone": "",
            "headless": False,
            "slow_mo": 300,
        }

        assistant = BookingAssistant(config=custom_config, on_success=on_success)

        with patch.object(assistant, 'start'), \
             patch.object(assistant, 'open_booking_page', return_value=True), \
             patch.object(assistant, 'dismiss_cookie_dialog'), \
             patch.object(assistant, 'fill_booking_form'), \
             patch.object(assistant, 'solve_and_fill_captcha'), \
             patch.object(assistant, 'submit_form'), \
             patch.object(assistant, 'is_on_step2', return_value=True), \
             patch.object(assistant, 'select_first_train', return_value=True), \
             patch.object(assistant, 'confirm_train_selection'), \
             patch.object(assistant, 'is_on_step3', return_value=True), \
             patch.object(assistant, 'fill_passenger_info'), \
             patch.object(assistant, 'confirm_booking'), \
             patch.object(assistant, 'close'), \
             patch('src.booking.time.sleep'):

            assistant.run()

        assert success_called == [True]

    def test_run_with_callbacks_error_page_load(self):
        """Test run with on_error callback when page load fails (GUI mode)."""
        error_messages = []

        def on_error(msg):
            error_messages.append(msg)

        custom_config = {
            "base_url": "https://irs.thsrc.com.tw/IMINT/",
            "start_station": "2",
            "end_station": "12",
            "travel_date": "2026/01/25",
            "travel_time": "08:00",
            "adult_count": 1,
            "child_count": 0,
            "disabled_count": 0,
            "elder_count": 0,
            "student_count": 0,
            "passenger_id": "A123456789",
            "passenger_email": "test@test.com",
            "passenger_phone": "",
            "headless": False,
            "slow_mo": 300,
        }

        assistant = BookingAssistant(config=custom_config, on_error=on_error)

        with patch.object(assistant, 'start'), \
             patch.object(assistant, 'open_booking_page', return_value=False), \
             patch.object(assistant, 'close'):

            assistant.run()

        assert error_messages == ["Failed to load page"]

    def test_run_with_callbacks_error_captcha(self):
        """Test run with on_error callback when captcha fails (GUI mode)."""
        error_messages = []

        def on_error(msg):
            error_messages.append(msg)

        custom_config = {
            "base_url": "https://irs.thsrc.com.tw/IMINT/",
            "start_station": "2",
            "end_station": "12",
            "travel_date": "2026/01/25",
            "travel_time": "08:00",
            "adult_count": 1,
            "child_count": 0,
            "disabled_count": 0,
            "elder_count": 0,
            "student_count": 0,
            "passenger_id": "A123456789",
            "passenger_email": "test@test.com",
            "passenger_phone": "",
            "headless": False,
            "slow_mo": 300,
        }

        assistant = BookingAssistant(config=custom_config, on_error=on_error)

        with patch.object(assistant, 'start'), \
             patch.object(assistant, 'open_booking_page', return_value=True), \
             patch.object(assistant, 'dismiss_cookie_dialog'), \
             patch.object(assistant, 'fill_booking_form'), \
             patch.object(assistant, 'solve_and_fill_captcha'), \
             patch.object(assistant, 'submit_form'), \
             patch.object(assistant, 'is_on_step2', return_value=False), \
             patch.object(assistant, 'check_for_errors', return_value="系統錯誤"), \
             patch.object(assistant, 'close'), \
             patch('src.booking.time.sleep'):

            assistant.run()

        assert "Non-captcha error: 系統錯誤" in error_messages[0]

    def test_run_with_callbacks_error_no_trains(self):
        """Test run with on_error callback when no trains available (GUI mode)."""
        error_messages = []

        def on_error(msg):
            error_messages.append(msg)

        custom_config = {
            "base_url": "https://irs.thsrc.com.tw/IMINT/",
            "start_station": "2",
            "end_station": "12",
            "travel_date": "2026/01/25",
            "travel_time": "08:00",
            "adult_count": 1,
            "child_count": 0,
            "disabled_count": 0,
            "elder_count": 0,
            "student_count": 0,
            "passenger_id": "A123456789",
            "passenger_email": "test@test.com",
            "passenger_phone": "",
            "headless": False,
            "slow_mo": 300,
        }

        assistant = BookingAssistant(config=custom_config, on_error=on_error)

        with patch.object(assistant, 'start'), \
             patch.object(assistant, 'open_booking_page', return_value=True), \
             patch.object(assistant, 'dismiss_cookie_dialog'), \
             patch.object(assistant, 'fill_booking_form'), \
             patch.object(assistant, 'solve_and_fill_captcha'), \
             patch.object(assistant, 'submit_form'), \
             patch.object(assistant, 'is_on_step2', return_value=True), \
             patch.object(assistant, 'select_first_train', return_value=False), \
             patch.object(assistant, 'close'), \
             patch('src.booking.time.sleep'):

            assistant.run()

        assert error_messages == ["No available trains to select"]

    def test_run_with_callbacks_error_step3(self):
        """Test run with on_error callback when Step 3 not reached (GUI mode)."""
        error_messages = []

        def on_error(msg):
            error_messages.append(msg)

        custom_config = {
            "base_url": "https://irs.thsrc.com.tw/IMINT/",
            "start_station": "2",
            "end_station": "12",
            "travel_date": "2026/01/25",
            "travel_time": "08:00",
            "adult_count": 1,
            "child_count": 0,
            "disabled_count": 0,
            "elder_count": 0,
            "student_count": 0,
            "passenger_id": "A123456789",
            "passenger_email": "test@test.com",
            "passenger_phone": "",
            "headless": False,
            "slow_mo": 300,
        }

        assistant = BookingAssistant(config=custom_config, on_error=on_error)

        with patch.object(assistant, 'start'), \
             patch.object(assistant, 'open_booking_page', return_value=True), \
             patch.object(assistant, 'dismiss_cookie_dialog'), \
             patch.object(assistant, 'fill_booking_form'), \
             patch.object(assistant, 'solve_and_fill_captcha'), \
             patch.object(assistant, 'submit_form'), \
             patch.object(assistant, 'is_on_step2', return_value=True), \
             patch.object(assistant, 'select_first_train', return_value=True), \
             patch.object(assistant, 'confirm_train_selection'), \
             patch.object(assistant, 'is_on_step3', return_value=False), \
             patch.object(assistant, 'close'), \
             patch('src.booking.time.sleep'):

            assistant.run()

        assert error_messages == ["Failed to reach passenger info page (Step 3)"]

    def test_run_with_callbacks_exception(self):
        """Test run with on_error callback when exception occurs (GUI mode)."""
        error_messages = []

        def on_error(msg):
            error_messages.append(msg)

        custom_config = {
            "base_url": "https://irs.thsrc.com.tw/IMINT/",
            "start_station": "2",
            "end_station": "12",
            "travel_date": "2026/01/25",
            "travel_time": "08:00",
            "adult_count": 1,
            "child_count": 0,
            "disabled_count": 0,
            "elder_count": 0,
            "student_count": 0,
            "passenger_id": "A123456789",
            "passenger_email": "test@test.com",
            "passenger_phone": "",
            "headless": False,
            "slow_mo": 300,
        }

        assistant = BookingAssistant(config=custom_config, on_error=on_error)

        with patch.object(assistant, 'start', side_effect=Exception("Test exception")), \
             patch.object(assistant, 'close'):

            assistant.run()

        assert error_messages == ["Test exception"]

    def test_run_with_callbacks_max_retries(self):
        """Test run with on_error callback when max captcha retries exceeded (GUI mode)."""
        error_messages = []

        def on_error(msg):
            error_messages.append(msg)

        custom_config = {
            "base_url": "https://irs.thsrc.com.tw/IMINT/",
            "start_station": "2",
            "end_station": "12",
            "travel_date": "2026/01/25",
            "travel_time": "08:00",
            "adult_count": 1,
            "child_count": 0,
            "disabled_count": 0,
            "elder_count": 0,
            "student_count": 0,
            "passenger_id": "A123456789",
            "passenger_email": "test@test.com",
            "passenger_phone": "",
            "headless": False,
            "slow_mo": 300,
        }

        assistant = BookingAssistant(config=custom_config, on_error=on_error)

        with patch.object(assistant, 'start'), \
             patch.object(assistant, 'open_booking_page', return_value=True), \
             patch.object(assistant, 'dismiss_cookie_dialog'), \
             patch.object(assistant, 'fill_booking_form'), \
             patch.object(assistant, 'solve_and_fill_captcha'), \
             patch.object(assistant, 'submit_form'), \
             patch.object(assistant, 'is_on_step2', return_value=False), \
             patch.object(assistant, 'check_for_errors', return_value="驗證碼錯誤"), \
             patch.object(assistant, 'refresh_captcha'), \
             patch.object(assistant, 'close'), \
             patch('src.booking.time.sleep'):

            assistant.run(max_captcha_retries=3)

        assert error_messages == ["Failed after 3 captcha attempts"]

    def test_run_with_callbacks_unknown_error(self):
        """Test run with on_error callback when unknown error occurs (GUI mode)."""
        error_messages = []

        def on_error(msg):
            error_messages.append(msg)

        custom_config = {
            "base_url": "https://irs.thsrc.com.tw/IMINT/",
            "start_station": "2",
            "end_station": "12",
            "travel_date": "2026/01/25",
            "travel_time": "08:00",
            "adult_count": 1,
            "child_count": 0,
            "disabled_count": 0,
            "elder_count": 0,
            "student_count": 0,
            "passenger_id": "A123456789",
            "passenger_email": "test@test.com",
            "passenger_phone": "",
            "headless": False,
            "slow_mo": 300,
        }

        assistant = BookingAssistant(config=custom_config, on_error=on_error)

        with patch.object(assistant, 'start'), \
             patch.object(assistant, 'open_booking_page', return_value=True), \
             patch.object(assistant, 'dismiss_cookie_dialog'), \
             patch.object(assistant, 'fill_booking_form'), \
             patch.object(assistant, 'solve_and_fill_captcha'), \
             patch.object(assistant, 'submit_form'), \
             patch.object(assistant, 'is_on_step2', return_value=False), \
             patch.object(assistant, 'check_for_errors', return_value=""), \
             patch.object(assistant, 'close'), \
             patch('src.booking.time.sleep'):

            assistant.run()

        assert error_messages == ["Unknown error after form submission"]

    def test_parse_trigger_time_valid_format_with_seconds(self, assistant):
        """Test _parse_trigger_time with valid format including seconds."""
        from datetime import datetime, timedelta

        # Create a future time
        future_time = datetime.now() + timedelta(hours=1)
        time_str = future_time.strftime("%Y-%m-%dT%H:%M:%S")

        result = assistant._parse_trigger_time(time_str)

        assert isinstance(result, datetime)
        assert result.year == future_time.year
        assert result.month == future_time.month
        assert result.day == future_time.day
        assert result.hour == future_time.hour
        assert result.minute == future_time.minute
        assert result.second == future_time.second

    def test_parse_trigger_time_valid_format_without_seconds(self, assistant):
        """Test _parse_trigger_time with valid format without seconds."""
        from datetime import datetime, timedelta

        # Create a future time
        future_time = datetime.now() + timedelta(hours=1)
        time_str = future_time.strftime("%Y-%m-%dT%H:%M")

        result = assistant._parse_trigger_time(time_str)

        assert isinstance(result, datetime)
        assert result.year == future_time.year
        assert result.month == future_time.month
        assert result.day == future_time.day
        assert result.hour == future_time.hour
        assert result.minute == future_time.minute
        assert result.second == 0  # Default to 0 when not specified

    def test_parse_trigger_time_invalid_format(self, assistant):
        """Test _parse_trigger_time with invalid format."""
        with pytest.raises(ValueError, match="Invalid trigger time format"):
            assistant._parse_trigger_time("2026/01/29 00:00:00")

    def test_parse_trigger_time_past_time(self, assistant):
        """Test _parse_trigger_time with past time."""
        from datetime import datetime, timedelta

        # Create a past time
        past_time = datetime.now() - timedelta(hours=1)
        time_str = past_time.strftime("%Y-%m-%dT%H:%M:%S")

        with pytest.raises(ValueError, match="has already passed"):
            assistant._parse_trigger_time(time_str)

    def test_wait_until_trigger_time_short_wait(self, assistant, capsys):
        """Test _wait_until_trigger_time with short wait time (CLI mode)."""
        from datetime import datetime, timedelta

        # Set a future time 2 seconds from now
        original_now = datetime.now()
        future_time = original_now + timedelta(seconds=2)
        time_str = future_time.strftime("%Y-%m-%dT%H:%M:%S")

        call_count = [0]
        def mock_now():
            call_count[0] += 1
            if call_count[0] <= 2:
                return original_now
            else:
                return future_time + timedelta(seconds=1)  # Past trigger time

        with patch('src.booking.time.sleep') as mock_sleep, \
             patch('src.booking.time.time', return_value=0), \
             patch('datetime.datetime') as mock_datetime:

            mock_datetime.now.side_effect = mock_now
            mock_datetime.strptime.side_effect = lambda *args, **kwargs: datetime.strptime(*args, **kwargs)

            assistant._wait_until_trigger_time(time_str)

            # Should have called sleep at least once
            assert mock_sleep.called

        captured = capsys.readouterr()
        assert "Scheduled Execution Mode" in captured.out
        assert "Trigger time:" in captured.out
        assert "Press Ctrl+C to cancel" in captured.out

    def test_wait_until_trigger_time_with_reminder(self, assistant, capsys):
        """Test _wait_until_trigger_time with 60-second reminder (CLI mode)."""
        from datetime import datetime, timedelta

        # Set a future time 2.5 minutes from now
        original_now = datetime.now()
        future_time = original_now + timedelta(seconds=150)
        time_str = future_time.strftime("%Y-%m-%dT%H:%M:%S")

        # Mock datetime.now to simulate time progression
        call_count = [0]

        def mock_now():
            call_count[0] += 1
            if call_count[0] == 1:
                return original_now
            elif call_count[0] == 2:
                return original_now + timedelta(seconds=60)
            elif call_count[0] == 3:
                return original_now + timedelta(seconds=120)
            else:
                return future_time + timedelta(seconds=1)  # Past trigger time

        # Provide enough return values for time.time() calls
        time_values = [0] + [70] * 10  # Initial time + multiple reminder checks

        with patch('datetime.datetime') as mock_datetime, \
             patch('src.booking.time.sleep') as mock_sleep, \
             patch('src.booking.time.time', side_effect=time_values):

            mock_datetime.now.side_effect = mock_now
            mock_datetime.strptime.side_effect = lambda *args, **kwargs: datetime.strptime(*args, **kwargs)

            assistant._wait_until_trigger_time(time_str)

        captured = capsys.readouterr()
        assert "Scheduled Execution Mode" in captured.out
        assert "Time remaining:" in captured.out

    def test_wait_until_trigger_time_keyboard_interrupt_cli(self, assistant, capsys):
        """Test _wait_until_trigger_time with Ctrl+C in CLI mode."""
        from datetime import datetime, timedelta

        future_time = datetime.now() + timedelta(hours=1)
        time_str = future_time.strftime("%Y-%m-%dT%H:%M:%S")

        with patch('src.booking.time.sleep', side_effect=KeyboardInterrupt), \
             patch('src.booking.time.time', return_value=0):

            with pytest.raises(KeyboardInterrupt):
                assistant._wait_until_trigger_time(time_str)

        captured = capsys.readouterr()
        assert "Cancelled by user" in captured.out

    def test_wait_until_trigger_time_keyboard_interrupt_gui(self, assistant):
        """Test _wait_until_trigger_time with Ctrl+C in GUI mode."""
        from datetime import datetime, timedelta

        future_time = datetime.now() + timedelta(hours=1)
        time_str = future_time.strftime("%Y-%m-%dT%H:%M:%S")

        error_messages = []
        def on_error(msg):
            error_messages.append(msg)

        assistant.on_error = on_error

        with patch('src.booking.time.sleep', side_effect=KeyboardInterrupt), \
             patch('src.booking.time.time', return_value=0):

            with pytest.raises(KeyboardInterrupt):
                assistant._wait_until_trigger_time(time_str)

        assert any("Cancelled by user" in msg for msg in error_messages)

    def test_wait_until_trigger_time_gui_mode(self, assistant):
        """Test _wait_until_trigger_time in GUI mode displays waiting status."""
        from datetime import datetime, timedelta

        future_time = datetime.now() + timedelta(seconds=2)
        time_str = future_time.strftime("%Y-%m-%dT%H:%M:%S")

        error_messages = []
        def on_error(msg):
            error_messages.append(msg)

        assistant.on_error = on_error

        with patch('src.booking.time.sleep') as mock_sleep, \
             patch('src.booking.time.time', return_value=0):

            assistant._wait_until_trigger_time(time_str)

        # Should display waiting status in GUI mode
        assert any("Waiting until" in msg for msg in error_messages)

    def test_run_with_trigger_time_immediate(self, assistant):
        """Test run method skips waiting when trigger_time is empty."""
        assistant.config["trigger_time"] = ""

        with patch.object(assistant, '_wait_until_trigger_time') as mock_wait, \
             patch.object(assistant, 'start'), \
             patch.object(assistant, 'open_booking_page', return_value=True), \
             patch.object(assistant, 'dismiss_cookie_dialog'), \
             patch.object(assistant, 'fill_booking_form'), \
             patch.object(assistant, 'solve_and_fill_captcha'), \
             patch.object(assistant, 'submit_form'), \
             patch.object(assistant, 'is_on_step2', return_value=True), \
             patch.object(assistant, 'select_first_train', return_value=True), \
             patch.object(assistant, 'confirm_train_selection'), \
             patch.object(assistant, 'is_on_step3', return_value=True), \
             patch.object(assistant, 'fill_passenger_info'), \
             patch.object(assistant, 'confirm_booking'), \
             patch.object(assistant, 'close'), \
             patch('src.booking.time.sleep'), \
             patch('builtins.input'):

            assistant.run()

        # Should not call wait method
        mock_wait.assert_not_called()

    def test_run_with_trigger_time_waits(self, assistant):
        """Test run method waits when trigger_time is set."""
        from datetime import datetime, timedelta

        future_time = datetime.now() + timedelta(seconds=2)
        time_str = future_time.strftime("%Y-%m-%dT%H:%M:%S")
        assistant.config["trigger_time"] = time_str

        with patch.object(assistant, '_wait_until_trigger_time') as mock_wait, \
             patch.object(assistant, 'start'), \
             patch.object(assistant, 'open_booking_page', return_value=True), \
             patch.object(assistant, 'dismiss_cookie_dialog'), \
             patch.object(assistant, 'fill_booking_form'), \
             patch.object(assistant, 'solve_and_fill_captcha'), \
             patch.object(assistant, 'submit_form'), \
             patch.object(assistant, 'is_on_step2', return_value=True), \
             patch.object(assistant, 'select_first_train', return_value=True), \
             patch.object(assistant, 'confirm_train_selection'), \
             patch.object(assistant, 'is_on_step3', return_value=True), \
             patch.object(assistant, 'fill_passenger_info'), \
             patch.object(assistant, 'confirm_booking'), \
             patch.object(assistant, 'close'), \
             patch('src.booking.time.sleep'), \
             patch('builtins.input'):

            assistant.run()

        # Should call wait method with the trigger time
        mock_wait.assert_called_once_with(time_str)
