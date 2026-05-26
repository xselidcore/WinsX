"""
WinsX — GUI-версия активатора Windows
Дизайн: тёмная тема в стиле xselid.ru
"""

import sys
import threading
import subprocess
import ctypes
import time

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QFrame, QScrollArea,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve,
    QTimer, QRect, QSize
)
from PyQt6.QtGui import (
    QFont, QFontDatabase, QColor, QPalette, QIcon,
    QPainter, QBrush, QPen, QPixmap, QLinearGradient
)

#  ПАЛИТРА (xselid.ru)

BG         = "#0f0f0f"   # фон окна
BG_CARD    = "#171717"   # карточки/панели
BG_ITEM    = "#353535"   # строки списка
BG_HOVER   = "#474747"   # hover на строках
BORDER     = "#292929"   # тонкие разделители
RED        = "#e5342a"   # основной акцент (красный с сайта)
RED_HOVER  = "#cc2a20"   # hover на красном
TEXT       = "#f0f0f0"   # основной текст
TEXT_MUTED = "#838383"   # приглушённый текст
TEXT_DIM   = "#535353"   # очень тихий текст
SUCCESS    = "#22c55e"   # зелёный для успеха
WARNING    = "#f59e0b"   # жёлтый

EDITIONS = {
    "1":  ("Home",                    "TX9XD-98N7V-6WMQ6-BX7FG-H8Q99"),
    "2":  ("Home N",                  "3KHY7-WNT83-DGQKR-F7HPR-844BM"),
    "3":  ("Home Single Language",    "7HNRX-D7KGG-3K4RQ-4WPJ4-YTDFH"),
    "4":  ("Home Country Specific",   "PVMJN-6DFY6-9CCP6-7BKTT-D3WVR"),
    "5":  ("Pro",                     "W269N-WFGWX-YVC9B-4J6C9-T83GX"),
    "6":  ("Pro N",                   "MH37W-N47XK-V7XM9-C7227-GCQG9"),
    "7":  ("Pro Workstation",         "DXG7C-N36C4-C4HTG-X4T3X-2YV77"),
    "8":  ("Pro N Workstation",       "WYPNQ-8C467-V2W6J-TX4WX-WT2RQ"),
    "9":  ("Pro Education",           "8PTT6-RNW4C-6V7J2-C2D3X-MHBPB"),
    "10": ("Pro Education N",         "GJTYN-HDMQY-FRR76-HVGC7-QPF8P"),
    "11": ("Enterprise",              "NPPR9-FWDCX-D2C8J-H872K-2YT43"),
    "12": ("Enterprise N",            "DPH2V-TTNVB-4X9Q3-TJR4H-KHJW4"),
    "13": ("Enterprise 2015 LTSB",    "WNMTR-4C88C-JK8YV-HQ7T2-76DF9"),
    "14": ("Enterprise 2015 LTSB N",  "2F77B-TNFGY-69QQF-B8YKP-D69TJ"),
    "15": ("Enterprise 2016 LTSB",    "DCPHK-NFMTC-H88MJ-PFHPY-QJ4BJ"),
    "16": ("Enterprise 2016 LTSB N",  "QFFDN-GRT3P-VKWWX-X7T3R-8B639"),
    "17": ("Education",               "NW6C2-QMPVW-D7KKK-3GKT6-VCFB2"),
    "18": ("Education N",             "2WH4N-8QGBV-H22JP-CT43Q-MDWWJ"),
    "19": ("Starter",                 "D6RD9-D4N8T-RT9QX-YW6YT-FCWWJ"),
    "20": ("S",                       "3NF4D-GF9GY-63VKH-QRC3V-7QW8P"),
    "21": ("Enterprise G N",          "FW7NV-4T673-HF4VX-9X4MM-B4H4T"),
}
KMS_SERVER = "kms.digiboy.ir"


#  ФОНОВЫЙ ПОТОК АКТИВАЦИИ
class ActivatorThread(QThread):
    progress = pyqtSignal(int, str)   
    finished = pyqtSignal(bool, str)  

    def __init__(self, edition_name: str, product_key: str):
        super().__init__()
        self.edition_name = edition_name
        self.product_key  = product_key

    def run_cmd(self, cmd: str, timeout: int = 60) -> bool:
        try:
            r = subprocess.run(cmd, shell=True,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               timeout=timeout)
            return r.returncode == 0
        except subprocess.TimeoutExpired:
            return None
        except Exception:
            return False

    def check_status(self) -> bool:
        try:
            r = subprocess.run("slmgr /dli", shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, timeout=10)
            out = (r.stdout + r.stderr).lower()
            return any(x in out for x in [
                "license status: licensed",
                "состояние лицензии: лицензировано",
            ])
        except Exception:
            return False

    def run(self):
        self.progress.emit(1, "Установка ключа продукта...")
        ok = self.run_cmd(f"slmgr /ipk {self.product_key}")
        if not ok:
            self.finished.emit(False, "Не удалось установить ключ продукта.")
            return

        self.progress.emit(2, "Подключение к KMS-серверу...")
        ok = self.run_cmd(f"slmgr /skms {KMS_SERVER}")
        if not ok:
            self.finished.emit(False, "Не удалось подключиться к KMS-серверу.")
            return

        self.progress.emit(3, "Активация Windows...")
        ok = self.run_cmd("slmgr /ato", timeout=120)
        if ok or ok is None:
            time.sleep(1)
            if self.check_status():
                self.finished.emit(True, f"Windows {self.edition_name} активирована!")
            else:
                self.finished.emit(True, f"Команда выполнена. Проверьте статус вручную.")
        else:
            self.finished.emit(False, "Ошибка при активации. Проверьте подключение к интернету.")


# СТРОКА РЕДАКЦИИ
class EditionRow(QWidget):
    clicked = pyqtSignal(str, str)  # key, name

    def __init__(self, key: str, name: str, popular: bool = False):
        super().__init__()
        self.key  = key
        self.name = name
        self.selected = False
        self.setFixedHeight(46)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        # номер
        num = QLabel(key)
        num.setFixedWidth(24)
        num.setFont(QFont("Consolas", 10))
        num.setStyleSheet(f"color: {TEXT_DIM}; background: transparent;")
        num.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # название
        self.name_lbl = QLabel(name)
        self.name_lbl.setFont(QFont("Segoe UI", 11))
        self.name_lbl.setStyleSheet(f"color: {TEXT}; background: transparent;")

        # бейдж popular
        if popular:
            badge = QLabel("popular")
            badge.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            badge.setStyleSheet(f"""
                color: {RED};
                background: transparent;
                border: 1px solid {RED};
                border-radius: 3px;
                padding: 1px 6px;
            """)
            layout.addWidget(num)
            layout.addWidget(self.name_lbl, 1)
            layout.addWidget(badge)
        else:
            layout.addWidget(num)
            layout.addWidget(self.name_lbl, 1)

        self._update_style()

    def _update_style(self):
        if self.selected:
            bg = BG_HOVER
            left = f"border-left: 2px solid {RED};"
        else:
            bg = "transparent"
            left = f"border-left: 2px solid transparent;"
        self.setStyleSheet(f"""
            EditionRow {{
                background: {bg};
                {left}
                border-radius: 0px;
            }}
        """)

    def set_selected(self, val: bool):
        self.selected = val
        self._update_style()
        if val:
            self.name_lbl.setStyleSheet(f"color: {TEXT}; background: transparent; font-weight: 600;")
        else:
            self.name_lbl.setStyleSheet(f"color: {TEXT}; background: transparent; font-weight: 400;")

    def mousePressEvent(self, e):
        self.clicked.emit(self.key, self.name)

    def enterEvent(self, e):
        if not self.selected:
            self.setStyleSheet(f"""
                EditionRow {{
                    background: {BG_HOVER};
                    border-left: 2px solid {BORDER};
                    border-radius: 0px;
                }}
            """)

    def leaveEvent(self, e):
        self._update_style()



#  ВИДЖЕТ: ШАГ ПРОГРЕССА
class StepWidget(QWidget):
    def __init__(self, num: int, text: str):
        super().__init__()
        self.num   = num
        self.state = "idle"  # idle | active | done | error

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(14)

        # кружок с цифрой
        self.circle = QLabel(str(num))
        self.circle.setFixedSize(28, 28)
        self.circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.circle.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))

        # текст шага
        self.label = QLabel(text)
        self.label.setFont(QFont("Segoe UI", 11))

        layout.addWidget(self.circle)
        layout.addWidget(self.label, 1)
        self._apply_state()

    def _apply_state(self):
        s = self.state
        if s == "idle":
            c_bg, c_fg = BORDER, TEXT_DIM
            t_color = TEXT_DIM
            icon = str(self.num)
        elif s == "active":
            c_bg, c_fg = RED, "#fff"
            t_color = TEXT
            icon = str(self.num)
        elif s == "done":
            c_bg, c_fg = SUCCESS, "#fff"
            t_color = TEXT_MUTED
            icon = "✓"
        else:  # error
            c_bg, c_fg = "#ef4444", "#fff"
            t_color = "#ef4444"
            icon = "✕"

        self.circle.setText(icon)
        self.circle.setStyleSheet(f"""
            background: {c_bg};
            color: {c_fg};
            border-radius: 14px;
            font-weight: 700;
        """)
        self.label.setStyleSheet(f"color: {t_color}; background: transparent;")

    def set_state(self, state: str):
        self.state = state
        self._apply_state()

#  ГЛАВНОЕ ОКНО
class WinsXWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_key  = "5"   # Pro по умолчанию
        self.selected_name = "Pro"
        self.edition_rows  = {}
        self.thread        = None

        self.setWindowTitle("WinsX — Активатор Windows")
        self.setMinimumSize(820, 620)
        self.resize(940, 660)
        self.setStyleSheet(f"QMainWindow {{ background: {BG}; }}")

        self._build_ui()
        self._select_edition("5", "Pro")

    # построение интерфейса
    def _build_ui(self):
        root = QWidget()
        root.setStyleSheet(f"background: {BG};")
        self.setCentralWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # топбар
        topbar = self._make_topbar()
        root_layout.addWidget(topbar)

        # сепаратор
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER};")
        root_layout.addWidget(sep)

        # контент
        content = QWidget()
        content.setStyleSheet(f"background: {BG};")
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        left  = self._make_left_panel()
        right = self._make_right_panel()

        content_layout.addWidget(left, 5)

        vsep = QFrame()
        vsep.setFixedWidth(1)
        vsep.setStyleSheet(f"background: {BORDER};")
        content_layout.addWidget(vsep)

        content_layout.addWidget(right, 4)
        root_layout.addWidget(content, 1)

    def _make_topbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(52)
        bar.setStyleSheet(f"background: {BG};")

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(28, 0, 28, 0)

        logo = QLabel("winsx.")
        logo.setFont(QFont("Segoe UI", 15, QFont.Weight.Black))
        logo.setStyleSheet(f"color: {TEXT}; background: transparent; letter-spacing: -0.5px;")

        dot = QLabel("●")
        dot.setFont(QFont("Segoe UI", 9))
        dot.setStyleSheet(f"color: {RED}; background: transparent; margin-left: -6px;")

        logo_row = QHBoxLayout()
        logo_row.setSpacing(2)
        logo_row.addWidget(logo)
        logo_row.addWidget(dot)
        logo_row.addStretch()

        version = QLabel("v2.0")
        version.setFont(QFont("Segoe UI", 9))
        version.setStyleSheet(f"color: {TEXT_DIM}; background: transparent;")

        layout.addLayout(logo_row, 1)
        layout.addWidget(version)
        return bar

    def _make_left_panel(self) -> QWidget:
        panel = QWidget()
        panel.setStyleSheet(f"background: {BG};")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # заголовок над списком
        header = QWidget()
        header.setFixedHeight(44)
        header.setStyleSheet(f"background: {BG}; border-bottom: 1px solid {BORDER};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 0, 20, 0)

        h_lbl = QLabel("Редакция Windows")
        h_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        h_lbl.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent; letter-spacing: 0.8px;")
        h_layout.addWidget(h_lbl)

        count_lbl = QLabel(f"{len(EDITIONS)} вариантов")
        count_lbl.setFont(QFont("Segoe UI", 9))
        count_lbl.setStyleSheet(f"color: {TEXT_DIM}; background: transparent;")
        h_layout.addStretch()
        h_layout.addWidget(count_lbl)

        layout.addWidget(header)

        # скролл-область со списком редакций
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background: {BG}; }}
            QScrollBar:vertical {{
                background: {BG};
                width: 4px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER};
                border-radius: 2px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{ height: 0; }}
        """)

        list_widget = QWidget()
        list_widget.setStyleSheet(f"background: {BG};")
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 4, 0, 4)
        list_layout.setSpacing(0)

        popular_keys = {"5", "11"}
        for key, (name, _) in EDITIONS.items():
            row = EditionRow(key, name, popular=(key in popular_keys))
            row.clicked.connect(self._select_edition)
            self.edition_rows[key] = row
            list_layout.addWidget(row)

        list_layout.addStretch()
        scroll.setWidget(list_widget)
        layout.addWidget(scroll, 1)
        return panel

    def _make_right_panel(self) -> QWidget:
        panel = QWidget()
        panel.setStyleSheet(f"background: {BG};")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(20)

        # карточка выбранной редакции
        self.card = QFrame()
        self.card.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
        """)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(8)

        card_meta = QLabel("ВЫБРАННАЯ РЕДАКЦИЯ")
        card_meta.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        card_meta.setStyleSheet(f"color: {TEXT_DIM}; background: transparent; letter-spacing: 1px;")

        self.edition_title = QLabel("Pro")
        self.edition_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Black))
        self.edition_title.setStyleSheet(f"color: {TEXT}; background: transparent;")

        key_row = QHBoxLayout()
        key_meta = QLabel("КЛЮЧ")
        key_meta.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        key_meta.setStyleSheet(f"color: {TEXT_DIM}; background: transparent; letter-spacing: 1px;")
        self.key_label = QLabel("W269N-WFGWX-YVC9B-4J6C9-T83GX")
        self.key_label.setFont(QFont("Consolas", 10))
        self.key_label.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")

        card_layout.addWidget(card_meta)
        card_layout.addWidget(self.edition_title)

        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background: {BORDER};")
        card_layout.addWidget(sep2)
        card_layout.addWidget(key_meta)
        card_layout.addWidget(self.key_label)

        layout.addWidget(self.card)

        # ── шаги ──
        steps_frame = QFrame()
        steps_frame.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
        """)
        steps_layout = QVBoxLayout(steps_frame)
        steps_layout.setContentsMargins(20, 14, 20, 14)
        steps_layout.setSpacing(4)

        steps_meta = QLabel("ПРОЦЕСС АКТИВАЦИИ")
        steps_meta.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        steps_meta.setStyleSheet(f"color: {TEXT_DIM}; background: transparent; letter-spacing: 1px;")
        steps_layout.addWidget(steps_meta)

        s1 = QFrame(); s1.setFixedHeight(1)
        s1.setStyleSheet(f"background: {BORDER}; margin: 4px 0;")
        steps_layout.addWidget(s1)

        self.step1 = StepWidget(1, "Установка ключа продукта")
        self.step2 = StepWidget(2, "Подключение к KMS-серверу")
        self.step3 = StepWidget(3, "Активация Windows")
        steps_layout.addWidget(self.step1)
        steps_layout.addWidget(self.step2)
        steps_layout.addWidget(self.step3)

        layout.addWidget(steps_frame)

        # ── статус ──
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")
        self.status_label.setFixedHeight(36)
        layout.addWidget(self.status_label)

        layout.addStretch()

        # кнопка активации
        self.activate_btn = QPushButton("Активировать →")
        self.activate_btn.setFixedHeight(48)
        self.activate_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.activate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.activate_btn.setStyleSheet(f"""
            QPushButton {{
                background: {RED};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                letter-spacing: 0.3px;
            }}
            QPushButton:hover {{
                background: {RED_HOVER};
            }}
            QPushButton:pressed {{
                background: #b02218;
            }}
            QPushButton:disabled {{
                background: {BORDER};
                color: {TEXT_DIM};
            }}
        """)
        self.activate_btn.clicked.connect(self._on_activate)
        layout.addWidget(self.activate_btn)

        # ── подпись ──
        footer_lbl = QLabel("xselid. — xselid.ru")
        footer_lbl.setFont(QFont("Segoe UI", 9))
        footer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_lbl.setStyleSheet(f"color: {TEXT_DIM}; background: transparent;")
        layout.addWidget(footer_lbl)

        return panel

    # логика 
    def _select_edition(self, key: str, name: str):
        # снять выделение с предыдущего
        if self.selected_key in self.edition_rows:
            self.edition_rows[self.selected_key].set_selected(False)

        self.selected_key  = key
        self.selected_name = name
        self.edition_rows[key].set_selected(True)

        _, product_key = EDITIONS[key]
        self.edition_title.setText(f"Windows {name}")
        self.key_label.setText(product_key)

    def _on_activate(self):
        if not self._check_admin():
            self._set_status("⚠  Запустите программу от имени администратора", WARNING)
            return

        self.activate_btn.setEnabled(False)
        self.activate_btn.setText("Активация...")
        self._reset_steps()
        self.status_label.setText("")

        _, product_key = EDITIONS[self.selected_key]
        self.thread = ActivatorThread(self.selected_name, product_key)
        self.thread.progress.connect(self._on_progress)
        self.thread.finished.connect(self._on_finished)
        self.thread.start()

    def _on_progress(self, step: int, text: str):
        self._set_status(text, TEXT_MUTED)
        for i, sw in enumerate([self.step1, self.step2, self.step3], 1):
            if i < step:
                sw.set_state("done")
            elif i == step:
                sw.set_state("active")
            else:
                sw.set_state("idle")

    def _on_finished(self, success: bool, message: str):
        if success:
            for sw in [self.step1, self.step2, self.step3]:
                sw.set_state("done")
            self._set_status("✓  " + message, SUCCESS)
            self.activate_btn.setText("Готово ✓")
            self.activate_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {SUCCESS};
                    color: #fff;
                    border: none;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: 700;
                }}
            """)
        else:
            for sw in [self.step1, self.step2, self.step3]:
                if sw.state == "active":
                    sw.set_state("error")
            self._set_status("✕  " + message, "#ef4444")
            self.activate_btn.setEnabled(True)
            self.activate_btn.setText("Попробовать снова →")
            self.activate_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {RED};
                    color: #fff;
                    border: none;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: 700;
                }}
                QPushButton:hover {{ background: {RED_HOVER}; }}
                QPushButton:pressed {{ background: #b02218; }}
            """)

    def _reset_steps(self):
        for sw in [self.step1, self.step2, self.step3]:
            sw.set_state("idle")

    def _set_status(self, text: str, color: str):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; background: transparent;")

    @staticmethod
    def _check_admin() -> bool:
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return True  # не на Windows


#  ЗАПУСК
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Fusion dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,          QColor(BG))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Base,            QColor(BG_CARD))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor(BG_ITEM))
    palette.setColor(QPalette.ColorRole.ToolTipBase,     QColor(BG_CARD))
    palette.setColor(QPalette.ColorRole.ToolTipText,     QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Text,            QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Button,          QColor(BG_CARD))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor(TEXT))
    palette.setColor(QPalette.ColorRole.BrightText,      QColor(RED))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor(RED))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#fff"))
    app.setPalette(palette)

    win = WinsXWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()