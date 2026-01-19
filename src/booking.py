
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout
import time
from .config import (
    BASE_URL, HEADLESS, SLOW_MO,
    START_STATION, END_STATION, TRAVEL_DATE, TRAVEL_TIME,
    ADULT_COUNT, CHILD_COUNT, DISABLED_COUNT, ELDER_COUNT, STUDENT_COUNT,
    Selectors, TIME_VALUES, STATIONS,
    PASSENGER_ID, PASSENGER_PHONE, PASSENGER_EMAIL,
    TRIGGER_TIME
)
from .captcha import CaptchaSolver

class BookingAssistant:
    def __init__(self, config: dict = None, on_success=None, on_error=None):
        """
        Initialize BookingAssistant.

        Args:
            config: Optional configuration dict. If None, will read from .env via config.py
            on_success: Optional callback function called on successful booking
            on_error: Optional callback function called on error, receives error message string
        """
        self.solver = CaptchaSolver()
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.on_success = on_success
        self.on_error = on_error

        # Use provided config or load from environment
        if config:
            self.config = config
        else:
            # CLI mode: read from .env via config.py
            self.config = {
                "base_url": BASE_URL,
                "start_station": START_STATION,
                "end_station": END_STATION,
                "travel_date": TRAVEL_DATE,
                "travel_time": TRAVEL_TIME,
                "adult_count": ADULT_COUNT,
                "child_count": CHILD_COUNT,
                "disabled_count": DISABLED_COUNT,
                "elder_count": ELDER_COUNT,
                "student_count": STUDENT_COUNT,
                "passenger_id": PASSENGER_ID,
                "passenger_phone": PASSENGER_PHONE,
                "passenger_email": PASSENGER_EMAIL,
                "headless": HEADLESS,
                "slow_mo": SLOW_MO,
                "trigger_time": TRIGGER_TIME,
            }

    def start(self):
        print("Launching browser...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.config["headless"],
            slow_mo=self.config["slow_mo"],
            args=["--disable-blink-features=AutomationControlled"]
        )
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        self.page = self.context.new_page()
        print("Browser launched successfully.")
    
    def open_booking_page(self):
        try:
            print(f"Navigating to {self.config['base_url']}...")
            self.page.goto(self.config["base_url"], timeout=60000)
            self.page.wait_for_load_state("domcontentloaded")
            print("Page loaded successfully!")
            return True
        except PlaywrightTimeout:
            print("Timeout error: Could not load page within 60 seconds.")
            return False
        except Exception as e:
            print(f"Error opening page: {e}")
            return False

    def dismiss_cookie_dialog(self):
        """Dismiss cookie consent dialog if present."""
        try:
            cookie_btn = self.page.locator("#cookieAccpetBtn")
            if cookie_btn.is_visible(timeout=2000):
                cookie_btn.click()
                print("Cookie dialog dismissed.")
        except:
            pass  # No cookie dialog or already dismissed

    def fill_booking_form(self):
        """Fill the booking form with configured values."""
        print("\n--- Filling Booking Form ---")

        # Select departure station
        start_station = self.config["start_station"]
        print(f"Selecting departure station: {STATIONS.get(start_station, start_station)}")
        self.page.select_option(Selectors.START_STATION, value=start_station)

        # Select destination station
        end_station = self.config["end_station"]
        print(f"Selecting destination station: {STATIONS.get(end_station, end_station)}")
        self.page.select_option(Selectors.END_STATION, value=end_station)

        # Set departure date (if specified)
        travel_date = self.config.get("travel_date", "")
        if travel_date:
            print(f"Setting departure date: {travel_date}")
            # Date picker uses flatpickr which hides the actual input
            # We need to use JavaScript to set the value
            self.page.evaluate(f'''
                document.querySelector("#toTimeInputField").value = "{travel_date}";
                document.querySelector("#toTimeInputField").dispatchEvent(new Event("change"));
            ''')

        # Set departure time (if specified)
        travel_time = self.config.get("travel_time", "")
        if travel_time:
            time_value = TIME_VALUES.get(travel_time, travel_time)
            print(f"Setting departure time: {travel_time} ({time_value})")
            self.page.select_option(Selectors.DEPARTURE_TIME, value=time_value)

        # Set ticket count (adult)
        adult_count = self.config.get("adult_count", 1)
        ticket_value = f"{adult_count}F"
        print(f"Setting adult tickets: {adult_count}")
        self.page.select_option(Selectors.ADULT_TICKETS, value=ticket_value)

        print("Form filled successfully!")

    def get_captcha_image(self) -> bytes:
        """Capture captcha image and return as bytes."""
        captcha_img = self.page.locator(Selectors.CAPTCHA_IMAGE)
        return captcha_img.screenshot()

    def solve_and_fill_captcha(self) -> str:
        """Solve captcha and fill in the answer."""
        print("\n--- Solving Captcha ---")
        
        # Get captcha image
        captcha_bytes = self.get_captcha_image()
        
        # Solve using OCR
        captcha_text = self.solver.solve_bytes(captcha_bytes)
        print(f"Captcha recognized: {captcha_text}")
        
        # Fill captcha input
        captcha_input = self.page.locator(Selectors.CAPTCHA_INPUT)
        captcha_input.fill(captcha_text)
        
        # Wait a moment so user can see the filled value
        time.sleep(0.5)
        
        # Verify the fill worked
        filled_value = captcha_input.input_value()
        print(f"Captcha input filled with: {filled_value}")
        
        return captcha_text

    def refresh_captcha(self):
        """Click refresh button to get new captcha."""
        self.page.click(Selectors.CAPTCHA_REFRESH)
        time.sleep(1)  # Wait for new captcha to load

    def submit_form(self):
        """Submit the booking form."""
        print("\n--- Submitting Form ---")
        self.page.click(Selectors.SUBMIT_BUTTON)
        self.page.wait_for_load_state("domcontentloaded")

    def check_for_errors(self) -> str:
        """Check if there are any error messages on the page."""
        try:
            error_el = self.page.locator(Selectors.ERROR_MESSAGE)
            if error_el.is_visible(timeout=1000):
                return error_el.inner_text().strip()
        except:
            pass
        return ""

    def close(self):
        """Close browser and cleanup."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def is_on_step2(self) -> bool:
        """Check if we're on the train selection page (Step 2)."""
        try:
            return self.page.locator(Selectors.STEP2_FORM).is_visible(timeout=2000)
        except:
            return False

    def select_first_train(self):
        """Select the first available train on Step 2."""
        print("\n--- Selecting Train ---")
        
        # Wait for train list to load
        self.page.wait_for_selector(Selectors.TRAIN_LIST, timeout=10000)
        
        # Get all train options
        trains = self.page.locator(Selectors.TRAIN_RADIO)
        count = trains.count()
        print(f"Found {count} available trains")
        
        if count == 0:
            print("No trains available!")
            return False
        
        # Select the first train (usually already selected by default)
        first_train = trains.first
        if not first_train.is_checked():
            first_train.click()
        
        # Get train info for display
        train_code = first_train.get_attribute("QueryCode")
        departure = first_train.get_attribute("QueryDeparture")
        arrival = first_train.get_attribute("QueryArrival")
        print(f"Selected train: {train_code} ({departure} → {arrival})")
        
        return True

    def confirm_train_selection(self):
        """Click the confirm button on Step 2."""
        print("Confirming train selection...")
        self.page.click(Selectors.CONFIRM_TRAIN)
        self.page.wait_for_load_state("domcontentloaded")
        time.sleep(1)
        print("Train confirmed!")

    def is_on_step3(self) -> bool:
        """Check if we're on the passenger info page (Step 3)."""
        try:
            return self.page.locator(Selectors.STEP3_FORM).is_visible(timeout=2000)
        except:
            return False

    def fill_passenger_info(self):
        """Fill passenger information on Step 3."""
        print("\n--- Filling Passenger Info ---")

        # Fill ID number (required)
        passenger_id = self.config.get("passenger_id", "")
        if passenger_id:
            print(f"Filling ID: {passenger_id[:3]}***")
            self.page.fill(Selectors.PASSENGER_ID, passenger_id)

        # Fill phone (optional)
        passenger_phone = self.config.get("passenger_phone", "")
        if passenger_phone:
            print(f"Filling phone: {passenger_phone[:4]}***")
            self.page.fill(Selectors.PASSENGER_PHONE, passenger_phone)

        # Fill email (required)
        passenger_email = self.config.get("passenger_email", "")
        if passenger_email:
            print(f"Filling email: {passenger_email}")
            self.page.fill(Selectors.PASSENGER_EMAIL, passenger_email)

        # Check agree checkbox
        print("Checking agreement checkbox...")
        agree_box = self.page.locator(Selectors.AGREE_CHECKBOX)
        if not agree_box.is_checked():
            agree_box.click()

        print("Passenger info filled!")

    def confirm_booking(self):
        """Click confirm booking button on Step 3."""
        print("\n--- Confirming Booking ---")
        self.page.click(Selectors.CONFIRM_BOOKING)
        self.page.wait_for_load_state("domcontentloaded")
        time.sleep(2)
        print("Booking confirmed!")

    def _parse_trigger_time(self, time_str: str):
        """
        Parse trigger time string to datetime object.
        Supported formats:
        - 2026-01-29T00:00:00
        - 2026-01-29T00:00 (seconds default to 00)

        :param time_str: Time string
        :return: datetime object
        :raises ValueError: Invalid format or time has passed
        """
        from datetime import datetime

        # Try both formats
        for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"]:
            try:
                trigger_time = datetime.strptime(time_str, fmt)
                break
            except ValueError:
                continue
        else:
            raise ValueError(
                f"Invalid trigger time format: '{time_str}'\n"
                f"Please use format: 2026-01-29T00:00:00 or 2026-01-29T00:00"
            )

        # Check if time has passed
        now = datetime.now()
        if trigger_time <= now:
            raise ValueError(
                f"Trigger time {time_str} has already passed\n"
                f"Current time: {now.strftime('%Y-%m-%dT%H:%M:%S')}"
            )

        return trigger_time

    def _wait_until_trigger_time(self, time_str: str):
        """
        Wait until trigger time.
        - Display remaining time every 60 seconds
        - Support Ctrl+C interruption

        :param time_str: Trigger time string
        """
        from datetime import datetime

        trigger_time = self._parse_trigger_time(time_str)

        # Calculate wait seconds
        now = datetime.now()
        total_seconds = (trigger_time - now).total_seconds()

        # Display wait info
        msg = (
            f"⏰ Scheduled Execution Mode\n"
            f"Trigger time: {trigger_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Time until execution: {int(total_seconds // 3600):02d}:{int((total_seconds % 3600) // 60):02d}:{int(total_seconds % 60):02d}\n"
            f"Press Ctrl+C to cancel..."
        )

        if self.on_error:
            # GUI mode: Display wait status (using on_error because it accepts string parameter)
            self.on_error(f"⏰ Waiting until {trigger_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            # CLI mode: Direct output
            print(msg)

        # Loop wait, reminder every 60 seconds
        remaining_seconds = total_seconds
        last_reminder = time.time()

        try:
            while remaining_seconds > 0:
                sleep_time = min(60, remaining_seconds)
                time.sleep(sleep_time)
                remaining_seconds = (trigger_time - datetime.now()).total_seconds()

                # Reminder every 60 seconds (CLI mode only)
                if not self.on_error and time.time() - last_reminder >= 60:
                    hours = int(remaining_seconds // 3600)
                    minutes = int((remaining_seconds % 3600) // 60)
                    seconds = int(remaining_seconds % 60)
                    print(f"⏳ Time remaining: {hours:02d}:{minutes:02d}:{seconds:02d}")
                    last_reminder = time.time()

        except KeyboardInterrupt:
            msg = "\n❌ Cancelled by user"
            if self.on_error:
                self.on_error(msg)
            else:
                print(msg)
            raise  # Re-raise for outer handler

    def run(self, max_captcha_retries: int = 5):
        """
        Run the booking assistant with automatic captcha retry.

        Args:
            max_captcha_retries: Maximum number of captcha retry attempts.
        """
        try:
            # Check if we need to wait for trigger time
            trigger_time = self.config.get("trigger_time", "")
            if trigger_time:
                self._wait_until_trigger_time(trigger_time)

            self.start()

            if not self.open_booking_page():
                error_msg = "Failed to load page"
                if self.on_error:
                    self.on_error(error_msg)
                else:
                    print(f"{error_msg}. Exiting...")
                return

            # Dismiss cookie dialog
            self.dismiss_cookie_dialog()

            # Fill form
            self.fill_booking_form()

            # Try to submit with captcha retry
            for attempt in range(1, max_captcha_retries + 1):
                print(f"\n=== Attempt {attempt}/{max_captcha_retries} ===")

                # Solve captcha
                self.solve_and_fill_captcha()

                # Submit form
                self.submit_form()
                time.sleep(1)

                # Check if we reached Step 2
                if self.is_on_step2():
                    print("✅ Successfully reached train selection page!")
                    break

                # Check for errors
                error = self.check_for_errors()
                if error:
                    print(f"❌ Error: {error}")
                    # Check for captcha-related errors
                    if "驗證碼" in error or "檢測碼" in error or "security" in error.lower():
                        print("Captcha error - refreshing and retrying...")
                        self.refresh_captcha()
                        continue
                    else:
                        error_msg = f"Non-captcha error: {error}"
                        if self.on_error:
                            self.on_error(error_msg)
                        else:
                            print(f"{error_msg} - stopping")
                        return
                else:
                    error_msg = "Unknown error after form submission"
                    if self.on_error:
                        self.on_error(error_msg)
                    else:
                        print(f"{error_msg} - stopping")
                    return
            else:
                error_msg = f"Failed after {max_captcha_retries} captcha attempts"
                if self.on_error:
                    self.on_error(error_msg)
                else:
                    print(error_msg)
                return

            # === Step 2: Select Train ===
            if not self.select_first_train():
                error_msg = "No available trains to select"
                if self.on_error:
                    self.on_error(error_msg)
                else:
                    print(f"{error_msg} - stopping")
                return

            # Confirm train selection
            self.confirm_train_selection()

            # === Step 3: Fill Passenger Info ===
            if not self.is_on_step3():
                error_msg = "Failed to reach passenger info page (Step 3)"
                if self.on_error:
                    self.on_error(error_msg)
                else:
                    print(f"{error_msg} - stopping")
                return

            print("\n=== Step 3: Passenger Info ===")
            self.fill_passenger_info()

            # Confirm booking
            self.confirm_booking()

            # === Step 4: Booking Complete ===
            if self.on_success:
                self.on_success()
            else:
                # CLI mode: display success message
                print("\n" + "="*50)
                print("🎉 BOOKING COMPLETE!")
                print("="*50)
                print("\nPlease check the page for your booking confirmation.")
                print("Press Enter to close the browser...")
                input()

        except Exception as e:
            error_msg = str(e)
            if self.on_error:
                self.on_error(error_msg)
            else:
                # CLI mode: print error
                print(f"An error occurred: {error_msg}")
                import traceback
                traceback.print_exc()
        finally:
            self.close()
            if not self.on_success and not self.on_error:
                # CLI mode only
                print("Assistant finished.")

