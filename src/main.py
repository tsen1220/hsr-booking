
from src.booking import BookingAssistant

def main():
    print("Starting HSR Booking Assistant...")

    try:
        assistant = BookingAssistant()
        assistant.run()
    except ValueError as e:
        # Time format error or time has passed
        print(f"\n❌ Error: {e}")
        return 1
    except KeyboardInterrupt:
        # User pressed Ctrl+C to cancel
        print("\n\nCancelled by user")
        return 0

    print("Assistant finished.")
    return 0

if __name__ == "__main__":
    exit(main())
