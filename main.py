import threading
import time
import urllib.request
import flet as ft

try:
    import serial

    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

ROBOT_IP = "http://192.168.4.1"
BT_PORT = "COM5"
BT_BAUD = 9600


def main(page: ft.Page):
    page.title = "Motor Rabtor"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.padding = 20
    page.rtl = True

    bt_connected = False
    wifi_connected = False
    bt_serial = None
    obstacle_detected = False

    status_text = ft.Text(
        "الحالة: جاهز للاتصال بالروبوت",
        size=15,
        color=ft.Colors.AMBER_400,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
    )

    radar_icon = ft.Icon(
        ft.Icons.SHIELD_OUTLINED, size=50, color=ft.Colors.GREEN_400
    )
    radar_status_title = ft.Text(
        "المسار آمن",
        size=18,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.GREEN_400,
    )
    radar_distance_text = ft.Text(
        "لا توجد عوائق قريبة", size=14, color=ft.Colors.GREY_300
    )

    radar_screen = ft.Container(
        content=ft.Column(
            [
                radar_icon,
                radar_status_title,
                radar_distance_text,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        ),
        width=220,
        height=180,
        bgcolor="#1B2E1E",
        border=ft.border.all(3, ft.Colors.GREEN_500),
        border_radius=20,
        alignment=ft.alignment.center,
        animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
    )

    def update_radar_ui(is_danger, distance_info=""):
        nonlocal obstacle_detected
        obstacle_detected = is_danger
        if is_danger:
            radar_screen.bgcolor = "#7F1D1D"
            radar_screen.border = ft.border.all(3, ft.Colors.RED_500)
            radar_icon.name = ft.Icons.WARNING_AMBER_ROUNDED
            radar_icon.color = ft.Colors.RED_200
            radar_status_title.value = "تحذير: جسم قريب!"
            radar_status_title.color = ft.Colors.WHITE
            radar_distance_text.value = (
                distance_info if distance_info else "عائق أمام الروبوت"
            )
            radar_distance_text.color = ft.Colors.RED_100
        else:
            radar_screen.bgcolor = "#1B2E1E"
            radar_screen.border = ft.border.all(3, ft.Colors.GREEN_500)
            radar_icon.name = ft.Icons.SHIELD_OUTLINED
            radar_icon.color = ft.Colors.GREEN_400
            radar_status_title.value = "المسار آمن"
            radar_status_title.color = ft.Colors.GREEN_400
            radar_distance_text.value = (
                distance_info if distance_info else "لا توجد عوائق قريبة"
            )
            radar_distance_text.color = ft.Colors.GREY_300
        page.update()

    def send_http_request(cmd_name, endpoint):
        try:
            urllib.request.urlopen(f"{ROBOT_IP}/{endpoint}", timeout=0.8)
            status_text.value = f"تم التنفيذ (Wi-Fi): {cmd_name}"
        except Exception:
            status_text.value = "فشل اتصال Wi-Fi: تأكد من الشبكة"
        page.update()

    def send_bt_command(cmd_name, endpoint):
        nonlocal bt_serial, bt_connected
        try:
            if bt_serial and bt_serial.is_open:
                bt_serial.write(f"{endpoint}\n".encode("utf-8"))
                status_text.value = f"تم التنفيذ (Bluetooth): {cmd_name}"
            else:
                status_text.value = "انقطع اتصال البلوتوث"
                bt_connected = False
                bt_btn.icon_color = ft.Colors.GREY_600
        except Exception:
            status_text.value = "خطأ في الإرسال عبر البلوتوث"
        page.update()

    def send_command(cmd_name, endpoint):
        status_text.value = f"جاري إرسال: {cmd_name}..."
        page.update()

        if bt_connected:
            threading.Thread(
                target=send_bt_command, args=(cmd_name, endpoint), daemon=True
            ).start()
        elif wifi_connected:
            threading.Thread(
                target=send_http_request, args=(cmd_name, endpoint), daemon=True
            ).start()
        else:
            status_text.value = f"وضع التجربة (فعل الاتصال): {cmd_name}"
            page.update()

    def radar_listener():
        nonlocal bt_serial
        while True:
            try:
                if bt_connected and bt_serial and bt_serial.is_open:
                    if bt_serial.in_waiting > 0:
                        line = (
                            bt_serial.readline()
                            .decode("utf-8", errors="ignore")
                            .strip()
                        )
                        if "DANGER" in line or "NEAR" in line:
                            update_radar_ui(True, "المسافة قريبة جداً!")
                        elif "SAFE" in line or "CLEAR" in line:
                            update_radar_ui(False, "الطريق خالٍ")
                        elif line.startswith("DIST:"):
                            dist = int(line.split(":")[1])
                            if dist < 25:
                                update_radar_ui(True, f"المسافة: {dist} سم")
                            else:
                                update_radar_ui(False, f"المسافة: {dist} سم")
                elif wifi_connected:
                    res = (
                        urllib.request.urlopen(
                            f"{ROBOT_IP}/radar_status", timeout=0.5
                        )
                        .read()
                        .decode("utf-8")
                        .strip()
                    )
                    if "DANGER" in res:
                        update_radar_ui(True, "عائق مرصود بالرادار!")
                    elif "SAFE" in res:
                        update_radar_ui(False, "لا توجد عوائق")
            except Exception:
                pass
            time.sleep(0.3)

    threading.Thread(target=radar_listener, daemon=True).start()

    def toggle_bt(e):
        nonlocal bt_connected, bt_serial, wifi_connected
        if not SERIAL_AVAILABLE:
            status_text.value = "مكتبة pyserial غير مثبتة!"
            page.update()
            return

        if not bt_connected:
            try:
                status_text.value = f"جاري الاتصال بالبلوتوث ({BT_PORT})..."
                page.update()
                bt_serial = serial.Serial(BT_PORT, BT_BAUD, timeout=1)
                bt_connected = True
                wifi_connected = False
                bt_btn.icon_color = ft.Colors.BLUE_400
                wifi_btn.icon_color = ft.Colors.GREY_600
                status_text.value = f"متصل بالبلوتوث بنجاح ({BT_PORT})"
            except Exception:
                status_text.value = f"فشل الاتصال بمنفذ {BT_PORT} (تأكد من الاقتران)"
        else:
            if bt_serial and bt_serial.is_open:
                bt_serial.close()
            bt_connected = False
            bt_btn.icon_color = ft.Colors.GREY_600
            status_text.value = "تم فصل البلوتوث"
        page.update()

    def toggle_wifi(e):
        nonlocal wifi_connected, bt_connected, bt_serial
        wifi_connected = not wifi_connected
        if wifi_connected:
            if bt_serial and bt_serial.is_open:
                bt_serial.close()
            bt_connected = False
            bt_btn.icon_color = ft.Colors.GREY_600
            wifi_btn.icon_color = ft.Colors.GREEN_400
            status_text.value = "متصل بشبكة Motor Rabtor (Wi-Fi)"
        else:
            wifi_btn.icon_color = ft.Colors.GREY_600
            status_text.value = "تم فصل اتصال Wi-Fi"
        page.update()

    bt_btn = ft.IconButton(
        icon=ft.Icons.BLUETOOTH,
        icon_color=ft.Colors.GREY_600,
        icon_size=28,
        tooltip="اتصال بلوتوث",
        on_click=toggle_bt,
    )
    wifi_btn = ft.IconButton(
        icon=ft.Icons.WIFI,
        icon_color=ft.Colors.GREY_600,
        icon_size=28,
        tooltip="اتصال واي فاي",
        on_click=toggle_wifi,
    )

    top_bar = ft.Container(
        content=ft.Row(
            [
                ft.Text(
                    "Motor Rabtor",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.CYAN_400,
                ),
                ft.Row([bt_btn, wifi_btn], spacing=5),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.padding.symmetric(vertical=10, horizontal=15),
        bgcolor="#1E1E1E",
        border_radius=15,
    )

    def create_dir_btn(icon, label, endpoint, btn_color="#252525"):
        return ft.ElevatedButton(
            content=ft.Column(
                [ft.Icon(icon, size=32), ft.Text(label, size=15)],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            width=95,
            height=95,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=20),
                bgcolor=btn_color,
                color=ft.Colors.WHITE,
            ),
            on_click=lambda e: send_command(label, endpoint),
        )
    page1_content = ft.Column(
        [
            ft.Text("التحكم في الحركة", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            create_dir_btn(ft.Icons.ARROW_UPWARD, "للأمام", "forward"),
            ft.Row(
                [
                    create_dir_btn(ft.Icons.ARROW_FORWARD, "لليمين", "right"),
                    create_dir_btn(
                        ft.Icons.STOP_CIRCLE, "توقف", "stop", "#8B0000"
                    ),
                    create_dir_btn(ft.Icons.ARROW_BACK, "لليسار", "left"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            create_dir_btn(ft.Icons.ARROW_DOWNWARD, "للخلف", "backward"),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    def create_func_btn(icon, label, color, endpoint):
        return ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(icon, size=24, color=color),
                    ft.Text(label, size=16, weight=ft.FontWeight.W_600),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            width=290,
            height=46,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=15),
                bgcolor="#252525",
                color=ft.Colors.WHITE,
            ),
            on_click=lambda e: send_command(label, endpoint),
        )

    def create_radar_btn(icon, label, endpoint):
        return ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(icon, size=22, color=ft.Colors.CYAN_300),
                    ft.Text(label, size=15, weight=ft.FontWeight.W_600),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            width=140,
            height=48,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=15),
                bgcolor="#1E293B",
                color=ft.Colors.WHITE,
            ),
            on_click=lambda e: send_command(label, endpoint),
        )

    test_radar_btn = ft.TextButton(
        "تجربة إنذار الرادار (محاكاة عائق)",
        icon=ft.Icons.BUG_REPORT,
        on_click=lambda e: update_radar_ui(
            not obstacle_detected,
            "محاكاة: جسم على بعد 12 سم" if not obstacle_detected else "",
        ),
    )

    page2_content = ft.Column(
        [
            ft.Text("الوظائف الإضافية", size=20, weight=ft.FontWeight.BOLD),
            create_func_btn(
                ft.Icons.CAMPAIGN, "١. كلكس", ft.Colors.YELLOW_400, "horn"
            ),
            create_func_btn(
                ft.Icons.LIGHTBULB, "٢. ضوء", ft.Colors.AMBER_300, "light"
            ),
            create_func_btn(
                ft.Icons.MIC, "٣. الميكروفون", ft.Colors.BLUE_300, "mic"
            ),
            create_func_btn(
                ft.Icons.VOLUME_UP, "٤. الاسبيكر", ft.Colors.GREEN_300, "speaker"
            ),
            create_func_btn(
                ft.Icons.POWER_SETTINGS_NEW,
                "٥. تشغيل و إيقاف",
                ft.Colors.RED_400,
                "power",
            ),
            ft.Divider(height=10, color=ft.Colors.GREY_800),
            ft.Text(
                "توجيه وشاشة الرادار",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.CYAN_400,
            ),
            ft.Row(
                [
                    create_radar_btn(
                        ft.Icons.RADAR, "رادار يمين", "radar_right"
                    ),
                    create_radar_btn(
                        ft.Icons.RADAR, "رادار يسار", "radar_left"
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            ft.Container(height=5),
            radar_screen,
            test_radar_btn,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    def create_limb_card(title, prefix, actions):
        buttons = [
            ft.ElevatedButton(
                content=ft.Text(act_name),
                on_click=lambda e, n=f"{title}: {act_name}", ep=f"{prefix}_{act_ep}": send_command(
                    n, ep
                ),
                style=ft.ButtonStyle(
                    bgcolor="#333333", color=ft.Colors.CYAN_200
                ),
            )
            for act_name, act_ep in actions
        ]
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        buttons,
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        wrap=True,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=12,
            bgcolor="#1E1E1E",
            border_radius=15,
            width=340,
        )

    page3_content = ft.Column(
        [
            ft.Text("تحريك الأطراف والرأس", size=20, weight=ft.FontWeight.BOLD),
            create_limb_card(
                "الرأس",
                "head",
                [("يمين", "right"), ("وسط", "center"), ("يسار", "left")],
            ),
            create_limb_card(
                "اليد اليمنى",
                "r_hand",
                [("رفع", "up"), ("تحية", "wave"), ("خفض", "down")],
            ),
            create_limb_card(
                "اليد اليسرى",
                "l_hand",
                [("رفع", "up"), ("تحية", "wave"), ("خفض", "down")],
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    body_container = ft.Container(content=page1_content, expand=True)

    def change_tab(e):
        idx = e.control.selected_index
        if idx == 0:
            body_container.content = page1_content
        elif idx == 1:
            body_container.content = page2_content
        elif idx == 2:
            body_container.content = page3_content
        page.update()

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.GAMEPAD, label="الحركة"),
            ft.NavigationBarDestination(icon=ft.Icons.TUNE, label="الوظائف"),
            ft.NavigationBarDestination(icon=ft.Icons.SMART_TOY, label="الأطراف"),
        ],
        on_change=change_tab,
        bgcolor="#1E1E1E",
    )

    page.add(
        top_bar,
        ft.Container(
            content=status_text, alignment=ft.alignment.center, padding=6
        ),
        body_container,
    )


ft.app(target=main)
