import flet as ft


def main(page: ft.Page):
    page.title = "تحكم الروبوت"
    page.theme_mode = ft.ThemeMode.DARK
    page.rtl = True  # دعم اللغة العربية من اليمين لليسار
    page.padding = 15

    # متغيرات الحالة
    state = {
        "bt": False,
        "wifi": False,
        "obstacle": False,
        "light": False,
        "mic": False,
        "speaker": False,
        "power": True,
    }

    def send_command(cmd):
        # اسمح بأوامر الطاقة والاتصال والتوقف حتى عندما تكون الطاقة مطفأة.
        allowed_when_off = {
            "PWR_ON", "PWR_OFF", "BT_ON", "BT_OFF",
            "WIFI_ON", "WIFI_OFF", "S", "H_OFF",
        }
        if not state["power"] and cmd not in allowed_when_off:
            return

        print(f"Command Sent: {cmd}")
        # TODO: أضف هنا كود الإرسال الفعلي للروبوت عبر بلوتوث أو واي فاي.

    # ==================== الشريط العلوي (بلوتوث وواي فاي) ====================
    bt_btn = ft.IconButton(
        icon=ft.Icons.BLUETOOTH,
        icon_color=ft.Colors.GREY,
        tooltip="بلوتوث",
    )
    wifi_btn = ft.IconButton(
        icon=ft.Icons.WIFI,
        icon_color=ft.Colors.GREY,
        tooltip="واي فاي",
    )

    def toggle_bt(e):
        state["bt"] = not state["bt"]
        bt_btn.icon_color = ft.Colors.BLUE_ACCENT if state["bt"] else ft.Colors.GREY
        send_command("BT_ON" if state["bt"] else "BT_OFF")
        page.update()

    def toggle_wifi(e):
        state["wifi"] = not state["wifi"]
        wifi_btn.icon_color = ft.Colors.GREEN_ACCENT if state["wifi"] else ft.Colors.GREY
        send_command("WIFI_ON" if state["wifi"] else "WIFI_OFF")
        page.update()

    bt_btn.on_click = toggle_bt
    wifi_btn.on_click = toggle_wifi

    page.appbar = ft.AppBar(
        title=ft.Text("لوحة تحكم الروبوت", weight=ft.FontWeight.BOLD),
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        actions=[bt_btn, wifi_btn],
    )

    # ==================== الصفحة الأولى: الحركة والرادار ====================
    radar_text = ft.Text(
        "الطريق آمن\n120 سم",
        color=ft.Colors.GREEN_ACCENT,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
    )
    radar_icon = ft.Icon(ft.Icons.RADAR, color=ft.Colors.GREEN_ACCENT, size=45)

    radar_box = ft.Container(
        width=165,
        height=165,
        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.GREEN),
        border=ft.border.all(3, ft.Colors.GREEN_ACCENT),
        border_radius=12,
        alignment=ft.alignment.center,
        content=ft.Column(
            [radar_icon, radar_text],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    def toggle_radar(e):
        # محاكاة للاختبار فقط؛ استبدلها بقراءة حساس المسافة الفعلي.
        state["obstacle"] = not state["obstacle"]
        if state["obstacle"]:
            radar_box.bgcolor = ft.Colors.with_opacity(0.25, ft.Colors.RED)
            radar_box.border = ft.border.all(3, ft.Colors.RED)
            radar_icon.name = ft.Icons.WARNING_AMBER_ROUNDED
            radar_icon.color = ft.Colors.RED
            radar_text.value = "تحذير: عائق قريب!\n15 سم"
            radar_text.color = ft.Colors.RED
        else:
            radar_box.bgcolor = ft.Colors.with_opacity(0.15, ft.Colors.GREEN)
            radar_box.border = ft.border.all(3, ft.Colors.GREEN_ACCENT)
            radar_icon.name = ft.Icons.RADAR
            radar_icon.color = ft.Colors.GREEN_ACCENT
            radar_text.value = "الطريق آمن\n120 سم"
            radar_text.color = ft.Colors.GREEN_ACCENT
        page.update()

    radar_box.on_click = toggle_radar

    def dir_button(icon, label, cmd):
        return ft.GestureDetector(
            on_tap_down=lambda e: send_command(cmd),
            on_tap_up=lambda e: send_command("S"),
            on_tap_cancel=lambda e: send_command("S"),
            content=ft.Container(
                width=75,
                height=75,
                bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.BLUE_ACCENT),
                border=ft.border.all(1.5, ft.Colors.BLUE_ACCENT),
                border_radius=15,
                content=ft.Column(
                    [ft.Icon(icon, size=30), ft.Text(label, size=12)],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
        )

    page1_content = ft.Column(
        [
            ft.Text("شاشة الرادار (اضغط لاختبار العائق)", size=13, color=ft.Colors.GREY),
            radar_box,
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            dir_button(ft.Icons.ARROW_UPWARD, "أمام", "F"),
            ft.Row(
                [
                    dir_button(ft.Icons.ARROW_BACK, "يسار", "L"),
                    ft.Container(width=50),
                    dir_button(ft.Icons.ARROW_FORWARD, "يمين", "R"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            dir_button(ft.Icons.ARROW_DOWNWARD, "خلف", "B"),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        scroll=ft.ScrollMode.AUTO,
    )

    # ==================== الصفحة الثانية: الوظائف ====================
    horn_btn = ft.GestureDetector(
        on_tap_down=lambda e: send_command("H_ON"),
        on_tap_up=lambda e: send_command("H_OFF"),
        on_tap_cancel=lambda e: send_command("H_OFF"),
        content=ft.Container(
            padding=16,
            bgcolor=ft.Colors.AMBER_700,
            border_radius=12,
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CAMPAIGN, size=28),
                    ft.Text("1. كلكس (اضغط باستمرار)", size=16, weight=ft.FontWeight.BOLD),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ),
    )

    def create_switch_card(title, icon, key, on_cmd, off_cmd, default_val=False):
        state[key] = default_val
        sw = ft.Switch(value=default_val, active_color=ft.Colors.BLUE_ACCENT)

        def on_change(e):
            state[key] = e.control.value
            send_command(on_cmd if state[key] else off_cmd)

        sw.on_change = on_change
        return ft.Card(
            content=ft.ListTile(
                leading=ft.Icon(icon),
                title=ft.Text(title),
                trailing=sw,
            )
        )

    page2_content = ft.Column(
        [
            horn_btn,
            create_switch_card("2. الضوء (الكشاف)", ft.Icons.LIGHTBULB, "light", "W_ON", "W_OFF"),
            create_switch_card("3. الميكروفون", ft.Icons.MIC, "mic", "MIC_ON", "MIC_OFF"),
            create_switch_card("4. الإسبيكر", ft.Icons.VOLUME_UP, "speaker", "SPK_ON", "SPK_OFF"),
            create_switch_card(
                "5. تشغيل وإيقاف الروبوت",
                ft.Icons.POWER_SETTINGS_NEW,
                "power",
                "PWR_ON",
                "PWR_OFF",
                True,
            ),
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
    )

    # ==================== الصفحة الثالثة: الأذرع والرأس ====================
    def create_servo_card(title, icon, prefix):
        val_text = ft.Text("90°", color=ft.Colors.BLUE_ACCENT, weight=ft.FontWeight.BOLD)

        def on_slide(e):
            angle = int(e.control.value)
            val_text.value = f"{angle}°"
            send_command(f"{prefix}:{angle}")
            page.update()

        return ft.Card(
            content=ft.Container(
                padding=15,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(icon, color=ft.Colors.BLUE_ACCENT),
                                ft.Text(title, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                val_text,
                            ]
                        ),
                        ft.Slider(min=0, max=180, divisions=180, value=90, on_change=on_slide),
                    ]
                ),
            )
        )

    page3_content = ft.Column(
        [
            create_servo_card("التحكم في الرأس", ft.Icons.FACE, "HEAD"),
            create_servo_card("التحكم في اليد اليمنى", ft.Icons.FRONT_HAND, "R_ARM"),
            create_servo_card("التحكم في اليد اليسرى", ft.Icons.BACK_HAND, "L_ARM"),
        ],
        spacing=15,
        scroll=ft.ScrollMode.AUTO,
    )

    # ==================== التنقل السفلي ====================
    body_container = ft.Container(content=page1_content, expand=True)

    def on_nav_change(e):
        idx = e.control.selected_index
        if idx == 0:
            body_container.content = page1_content
        elif idx == 1:
            body_container.content = page2_content
        elif idx == 2:
            body_container.content = page3_content
        page.update()

    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        on_change=on_nav_change,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.GAMEPAD, label="الحركة والرادار"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS_REMOTE, label="الوظائف"),
            ft.NavigationBarDestination(icon=ft.Icons.PRECISION_MANUFACTURING, label="الأذرع والرأس"),
        ],
    )

    page.add(body_container)


ft.run(main)
