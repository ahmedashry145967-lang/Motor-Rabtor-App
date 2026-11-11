import flet as ft
import urllib.request
import threading

ROBOT_IP = "http://192.168.4.1"


def main(page: ft.Page):
    page.title = "Motor Rabtor"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.padding = 20

    bt_connected = False
    wifi_connected = False

    status_text = ft.Text(
        "الحالة: جاهز للاتصال بالروبوت",
        size=16,
        color=ft.Colors.AMBER_400,
        weight=ft.FontWeight.BOLD,
    )

    def send_http_request(cmd_name, endpoint):
        try:
            urllib.request.urlopen(f"{ROBOT_IP}/{endpoint}", timeout=0.8)
            status_text.value = f"تم التنفيذ: {cmd_name}"
        except Exception:
            status_text.value = "فشل الاتصال: تأكد من اتصالك بشبكة الروبوت"
        page.update()

    def send_command(cmd_name, endpoint):
        status_text.value = f"جاري إرسال: {cmd_name}..."
        page.update()

        if wifi_connected:
            threading.Thread(
                target=send_http_request, args=(cmd_name, endpoint), daemon=True
            ).start()
        else:
            status_text.value = f"وضع التجربة (فعل الواي فاي): {cmd_name}"
            page.update()

    def toggle_bt(e):
        nonlocal bt_connected
        bt_connected = not bt_connected
        bt_btn.icon_color = (
            ft.Colors.BLUE_400 if bt_connected else ft.Colors.GREY_600
        )
        status_text.value = (
            "البلوتوث: مفعل (لربط الشريحة استخدم Wi-Fi)"
            if bt_connected
            else "البلوتوث: متوقف"
        )
        page.update()

    def toggle_wifi(e):
        nonlocal wifi_connected
        wifi_connected = not wifi_connected
        wifi_btn.icon_color = (
            ft.Colors.GREEN_400 if wifi_connected else ft.Colors.GREY_600
        )
        status_text.value = (
            "متصل بشبكة Motor Rabtor (Wi-Fi)"
            if wifi_connected
            else "تم فصل الاتصال"
        )
        page.update()

    bt_btn = ft.IconButton(
        icon=ft.Icons.BLUETOOTH,
        icon_color=ft.Colors.GREY_600,
        icon_size=28,
        on_click=toggle_bt,
    )
    wifi_btn = ft.IconButton(
        icon=ft.Icons.WIFI,
        icon_color=ft.Colors.GREY_600,
        icon_size=28,
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

    def create_dir_btn(icon, label, endpoint):
        return ft.ElevatedButton(
            content=ft.Column(
                [ft.Icon(icon, size=36), ft.Text(label, size=16)],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=105,
            height=105,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=20),
                bgcolor="#252525",
                color=ft.Colors.WHITE,
            ),
            on_click=lambda e: send_command(label, endpoint),
        )

    page1_content = ft.Column(
        [
            ft.Text("التحكم في الحركة", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(height=15),
            create_dir_btn(ft.Icons.ARROW_UPWARD, "للأمام", "forward"),
            ft.Row(
                [
                    create_dir_btn(ft.Icons.ARROW_BACK, "لليسار", "left"),
                    ft.Container(width=30),
                    create_dir_btn(ft.Icons.ARROW_FORWARD, "لليمين", "right"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            create_dir_btn(ft.Icons.ARROW_DOWNWARD, "للخلف", "backward"),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True,
    )

    def create_func_btn(icon, label, color, endpoint):
        return ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(icon, size=28, color=color),
                    ft.Text(label, size=18, weight=ft.FontWeight.W_600),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            width=280,
            height=55,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=15),
                bgcolor="#252525",
                color=ft.Colors.WHITE,
            ),
            on_click=lambda e: send_command(label, endpoint),
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
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12,
        expand=True,
    )

    def create_limb_card(title, prefix, actions):
        buttons = [
            ft.ElevatedButton(
                text=act_name,
                on_click=lambda e, n=f"{title}: {act_name}", ep=f"{prefix}_{act_ep}": send_command(
                    n, ep
                ),
                style=ft.ButtonStyle(bgcolor="#333333", color=ft.Colors.CYAN_200),
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
                "الرأس", "head", [("يسار", "left"), ("وسط", "center"), ("يمين", "right")]
            ),
            create_limb_card(
                "اليد اليمنى", "r_hand", [("رفع", "up"), ("تحية", "wave"), ("خفض", "down")]
            ),
            create_limb_card(
                "اليد اليسرى", "l_hand", [("رفع", "up"), ("تحية", "wave"), ("خفض", "down")]
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12,
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
        ft.Container(content=status_text, alignment=ft.alignment.center, padding=8),
        body_container,
    )


ft.app(target=main)
