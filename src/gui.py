import platform
import threading


def gui():
    """Launch GUI for HSR booking assistant (Windows only)."""
    if platform.system() != "Windows":
        print("GUI 僅支援 Windows")
        return

    import flet as ft
    from .config import STATIONS, TIME_VALUES
    from .booking import BookingAssistant

    def main(page: ft.Page):
        page.title = "高鐵訂票助手"
        page.window.width = 600
        page.window.height = 900
        page.padding = 20
        page.scroll = ft.ScrollMode.AUTO

        # Station options
        station_options = [
            ft.dropdown.Option(key=k, text=v) for k, v in STATIONS.items()
        ]

        # Time options
        time_options = [
            ft.dropdown.Option(key=k, text=k) for k in TIME_VALUES.keys()
        ]

        # Form fields
        start_station = ft.Dropdown(
            label="起站",
            options=station_options,
            value="2",  # Default: 台北
            width=200,
        )

        end_station = ft.Dropdown(
            label="迄站",
            options=station_options,
            value="12",  # Default: 左營
            width=200,
        )

        travel_date = ft.TextField(
            label="日期",
            hint_text="2026/01/25",
            value="",
            width=200,
        )

        travel_time = ft.Dropdown(
            label="時間",
            options=time_options,
            value="08:00",
            width=200,
        )

        adult_count = ft.TextField(
            label="成人",
            value="1",
            width=80,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        child_count = ft.TextField(
            label="孩童",
            value="0",
            width=80,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        disabled_count = ft.TextField(
            label="愛心",
            value="0",
            width=80,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        elder_count = ft.TextField(
            label="敬老",
            value="0",
            width=80,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        student_count = ft.TextField(
            label="學生",
            value="0",
            width=80,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        passenger_id = ft.TextField(
            label="身分證字號",
            hint_text="A123456789",
            value="",
            width=300,
        )

        passenger_email = ft.TextField(
            label="Email",
            hint_text="your@email.com",
            value="",
            width=300,
        )

        trigger_time = ft.TextField(
            label="觸發時間（選填）",
            hint_text="2026-01-29T00:00:00",
            value="",
            width=300,
            helper_text="空白表示立即執行",
        )

        headless = ft.Checkbox(
            label="Headless 模式",
            value=False,
        )

        slow_mo = ft.TextField(
            label="Slow Mo (ms)",
            value="300",
            width=120,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        status_text = ft.Text(
            "狀態: 等待中",
            size=16,
            weight=ft.FontWeight.BOLD,
        )

        start_btn = ft.ElevatedButton(
            "🚄 開始訂票",
            width=200,
            height=50,
        )

        def start_booking(e):
            """Start booking process in background thread."""
            # Disable button
            start_btn.disabled = True
            status_text.value = "狀態: 執行中..."
            page.update()

            # Collect form values
            config = {
                "base_url": "https://irs.thsrc.com.tw/IMINT/",
                "start_station": start_station.value,
                "end_station": end_station.value,
                "travel_date": travel_date.value,
                "travel_time": travel_time.value,
                "adult_count": int(adult_count.value) if adult_count.value else 1,
                "child_count": int(child_count.value) if child_count.value else 0,
                "disabled_count": int(disabled_count.value) if disabled_count.value else 0,
                "elder_count": int(elder_count.value) if elder_count.value else 0,
                "student_count": int(student_count.value) if student_count.value else 0,
                "passenger_id": passenger_id.value,
                "passenger_email": passenger_email.value,
                "passenger_phone": "",  # GUI 不輸入
                "headless": headless.value,
                "slow_mo": int(slow_mo.value) if slow_mo.value else 300,
                "trigger_time": trigger_time.value.strip(),
            }

            # Callbacks
            def on_success():
                status_text.value = "狀態: ✅ 完成"
                start_btn.disabled = False
                page.update()

            def on_error(msg):
                # If waiting status message (starts with ⏰), use different display
                if msg.startswith("⏰"):
                    status_text.value = f"狀態: {msg}"
                else:
                    status_text.value = f"狀態: ❌ {msg}"
                    start_btn.disabled = False  # Re-enable button on error
                page.update()

            # Run booking in background
            def run_booking():
                try:
                    assistant = BookingAssistant(
                        config=config,
                        on_success=on_success,
                        on_error=on_error,
                    )
                    assistant.run()
                except ValueError as e:
                    # Time format error or time has passed
                    on_error(str(e))
                except KeyboardInterrupt:
                    # User cancelled (rare in GUI, but still need to handle)
                    on_error("用戶取消")
                except Exception as e:
                    # Other unexpected errors
                    on_error(f"未預期錯誤：{e}")

            threading.Thread(target=run_booking, daemon=True).start()

        start_btn.on_click = start_booking

        # Layout
        page.add(
            ft.Text("高鐵訂票助手", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row([start_station, end_station]),
            ft.Row([travel_date, travel_time]),
            ft.Divider(),
            ft.Text("票數", size=18, weight=ft.FontWeight.BOLD),
            ft.Row([adult_count, child_count, elder_count]),
            ft.Row([disabled_count, student_count]),
            ft.Divider(),
            ft.Text("乘客資料", size=18, weight=ft.FontWeight.BOLD),
            passenger_id,
            passenger_email,
            ft.Divider(),
            ft.Text("預約執行", size=18, weight=ft.FontWeight.BOLD),
            trigger_time,
            ft.Divider(),
            ft.Text("設定", size=18, weight=ft.FontWeight.BOLD),
            ft.Row([headless, slow_mo]),
            ft.Divider(),
            ft.Row(
                [start_btn],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Container(height=20),
            status_text,
        )

    ft.app(target=main)


if __name__ == "__main__":
    gui()
