"""
Echo Settings & Echo Installer - Centralized Internationalization (i18n) & Localization System.
Provides full translation strings for all pages, sections, rows, buttons, dialogs, and components.
"""

import os
import locale
from PySide6.QtCore import QObject, Signal, QSettings

SUPPORTED_LANGUAGES = {
    "ru": {"name": "Russian", "native": "Русский", "code": "ru"},
    "en": {"name": "English", "native": "English", "code": "en"},
    "es": {"name": "Spanish", "native": "Español", "code": "es"},
    "de": {"name": "German", "native": "Deutsch", "code": "de"},
    "fr": {"name": "French", "native": "Français", "code": "fr"},
    "zh_CN": {"name": "Chinese", "native": "简体中文", "code": "zh_CN"},
    "ja": {"name": "Japanese", "native": "日本語", "code": "ja"},
    "it": {"name": "Italian", "native": "Italiano", "code": "it"},
    "pt_BR": {"name": "Portuguese", "native": "Português", "code": "pt_BR"},
    "tr": {"name": "Turkish", "native": "Türkçe", "code": "tr"},
    "uk": {"name": "Ukrainian", "native": "Українська", "code": "uk"},
    "kk": {"name": "Kazakh", "native": "Қазақша", "code": "kk"},
    "ar": {"name": "Arabic", "native": "العربية", "code": "ar"}
}

# --- Comprehensive Translations Dictionary ---
TRANSLATIONS = {
    # ── Sidebar & Navigation ──
    "nav.connectivity": {
        "en": "CONNECTIVITY", "ru": "СВЯЗЬ", "es": "CONECTIVIDAD", "de": "VERBINDUNG",
        "fr": "CONNECTIVITÉ", "zh_CN": "网络与连接", "ja": "接続", "it": "CONNETTIVITÀ",
        "pt_BR": "CONECTIVIDADE", "tr": "BAĞLANTI", "uk": "ЗВ'ЯЗОК", "kk": "БАЙЛАНЫС", "ar": "الاتصال"
    },
    "nav.wifi": {
        "en": "Wi-Fi", "ru": "Wi-Fi", "es": "Wi-Fi", "de": "WLAN",
        "fr": "Wi-Fi", "zh_CN": "无线局域网", "ja": "Wi-Fi", "it": "Wi-Fi",
        "pt_BR": "Wi-Fi", "tr": "Wi-Fi", "uk": "Wi-Fi", "kk": "Wi-Fi", "ar": "واي فاي"
    },
    "nav.bluetooth": {
        "en": "Bluetooth", "ru": "Bluetooth", "es": "Bluetooth", "de": "Bluetooth",
        "fr": "Bluetooth", "zh_CN": "蓝牙", "ja": "Bluetooth", "it": "Bluetooth",
        "pt_BR": "Bluetooth", "tr": "Bluetooth", "uk": "Bluetooth", "kk": "Bluetooth", "ar": "بلوتوث"
    },
    "nav.network": {
        "en": "Network", "ru": "Сеть", "es": "Red", "de": "Netzwerk",
        "fr": "Réseau", "zh_CN": "网络", "ja": "ネットワーク", "it": "Rete",
        "pt_BR": "Rede", "tr": "Ağ", "uk": "Мережа", "kk": "Желі", "ar": "الشبكة"
    },
    "nav.interaction": {
        "en": "INTERACTION", "ru": "ВЗАИМОДЕЙСТВИЕ", "es": "INTERACCIÓN", "de": "INTERAKTION",
        "fr": "INTERACTION", "zh_CN": "操作与输入", "ja": "操作と入力", "it": "INTERAZIONE",
        "pt_BR": "INTERAÇÃO", "tr": "ETKİLEŞİM", "uk": "ВЗАЄМОДІЯ", "kk": "ӨЗАРА ӘРЕКЕТТЕСТІК", "ar": "التفاعل"
    },
    "nav.sound": {
        "en": "Sound", "ru": "Звук", "es": "Sonido", "de": "Ton",
        "fr": "Son", "zh_CN": "声音", "ja": "サウンド", "it": "Suono",
        "pt_BR": "Som", "tr": "Ses", "uk": "Звук", "kk": "Дыбыс", "ar": "الصوت"
    },
    "nav.notifications": {
        "en": "Notifications", "ru": "Уведомления", "es": "Notificaciones", "de": "Mitteilungen",
        "fr": "Notifications", "zh_CN": "通知", "ja": "通知", "it": "Notifiche",
        "pt_BR": "Notificações", "tr": "Bildirimler", "uk": "Сповіщення", "kk": "Хабарландырулар", "ar": "الإشعارات"
    },
    "nav.keyboard": {
        "en": "Keyboard", "ru": "Клавиатура", "es": "Teclado", "de": "Tastatur",
        "fr": "Clavier", "zh_CN": "键盘", "ja": "キーボード", "it": "Tastiera",
        "pt_BR": "Teclado", "tr": "Klavye", "uk": "Клавіатура", "kk": "Пернетақта", "ar": "لوحة المفاتيح"
    },
    "nav.mouse": {
        "en": "Mouse", "ru": "Мышь", "es": "Ratón", "de": "Maus",
        "fr": "Souris", "zh_CN": "鼠标与触控板", "ja": "マウス", "it": "Mouse",
        "pt_BR": "Mouse", "tr": "Fare", "uk": "Миша", "kk": "Тінтуір", "ar": "الماوس"
    },
    "nav.privacy_section": {
        "en": "PRIVACY & SECURITY", "ru": "КОНФИДЕНЦИАЛЬНОСТЬ", "es": "PRIVACIDAD Y SEGURIDAD", "de": "DATENSCHUTZ & SICHERHEIT",
        "fr": "CONFIDENTIALITÉ ET SÉCURITÉ", "zh_CN": "隐私与安全性", "ja": "プライバシーとセキュリティ", "it": "PRIVACY E SICUREZZA",
        "pt_BR": "PRIVACIDADE E SEGURANÇA", "tr": "GİZLİLİK VE GÜVENLİK", "uk": "КОНФІДЕНЦІЙНІСТЬ ТА БЕЗПЕКА", "kk": "ҚҰПИЯЛЫЛЫҚ ЖӘНЕ ҚАУІПСІЗДІК", "ar": "الخصوصية والأمان"
    },
    "nav.privacy": {
        "en": "Privacy & Security", "ru": "Конфиденциальность", "es": "Privacidad y seguridad", "de": "Datenschutz & Sicherheit",
        "fr": "Confidentialité et sécurité", "zh_CN": "隐私与安全性", "ja": "プライバシーとセキュリティ", "it": "Privacy e sicurezza",
        "pt_BR": "Privacidade e Segurança", "tr": "Gizlilik ve Güvenlik", "uk": "Конфіденційність та безпека", "kk": "Құпиялылық және қауіпсіздік", "ar": "الخصوصية والأمان"
    },
    "nav.customization": {
        "en": "CUSTOMIZATION", "ru": "ПЕРСОНАЛИЗАЦИЯ", "es": "PERSONALIZACIÓN", "de": "ANPASSUNG",
        "fr": "PERSONNALISATION", "zh_CN": "个性化与外观", "ja": "カスタマイズ", "it": "PERSONALIZZAZIONE",
        "pt_BR": "PERSONALIZAÇÃO", "tr": "ÖZELLEŞTİRME", "uk": "ПЕРСОНАЛІЗАЦІЯ", "kk": "ДАРАЛАУ", "ar": "التخصيص"
    },
    "nav.general": {
        "en": "General", "ru": "Основные", "es": "General", "de": "Allgemein",
        "fr": "Général", "zh_CN": "通用", "ja": "一般", "it": "Generali",
        "pt_BR": "Geral", "tr": "Genel", "uk": "Загальні", "kk": "Негізгі", "ar": "عام"
    },
    "nav.appearance": {
        "en": "Appearance", "ru": "Внешний вид", "es": "Aspecto", "de": "Erscheinungsbild",
        "fr": "Apparence", "zh_CN": "外观", "ja": "外観", "it": "Aspetto",
        "pt_BR": "Aparência", "tr": "Görünüm", "uk": "Вигляд", "kk": "Сыртқы түрі", "ar": "المظهر"
    },
    "nav.display": {
        "en": "Display", "ru": "Дисплеи", "es": "Pantallas", "de": "Displays",
        "fr": "Moniteurs", "zh_CN": "显示器", "ja": "ディスプレイ", "it": "Schermi",
        "pt_BR": "Telas", "tr": "Ekranlar", "uk": "Дисплеї", "kk": "Дисплейлер", "ar": "شاشات العرض"
    },
    "nav.storage_power": {
        "en": "STORAGE & POWER", "ru": "ХРАНИЛИЩЕ И ПИТАНИЕ", "es": "ALMACENAMIENTO Y ENERGÍA", "de": "SPEICHER & ENERGIE",
        "fr": "STOCKAGE ET ALIMENTATION", "zh_CN": "储存与电源", "ja": "ストレージと電源", "it": "SPAZIO E BATTERIA",
        "pt_BR": "ARMAZENAMENTO E ENERGIA", "tr": "DEPOLAMA VE GÜÇ", "uk": "СХОВИЩЕ ТА ЖИВЛЕННЯ", "kk": "ЖАД ЖӘНЕ ҚУАТ", "ar": "التخزين والطاقة"
    },
    "nav.storage": {
        "en": "Storage", "ru": "Хранилище", "es": "Almacenamiento", "de": "Speicher",
        "fr": "Stockage", "zh_CN": "储存空间", "ja": "ストレージ", "it": "Spazio",
        "pt_BR": "Armazenamento", "tr": "Depolama", "uk": "Сховище", "kk": "Жад", "ar": "التخزين"
    },
    "nav.power": {
        "en": "Power", "ru": "Питание", "es": "Batería", "de": "Batterie",
        "fr": "Batterie", "zh_CN": "电池与电源", "ja": "バッテリー", "it": "Batteria",
        "pt_BR": "Bateria", "tr": "Güç", "uk": "Живлення", "kk": "Қуат", "ar": "الطاقة"
    },
    "nav.system": {
        "en": "SYSTEM", "ru": "СИСТЕМА", "es": "SISTEMA", "de": "SYSTEM",
        "fr": "SYSTÈME", "zh_CN": "系统", "ja": "システム", "it": "SISTEMA",
        "pt_BR": "SISTEMA", "tr": "SİSTEM", "uk": "СИСТЕМА", "kk": "ЖҮЙЕ", "ar": "النظام"
    },
    "nav.search": {
        "en": "Echo Search", "ru": "Поиск Echo", "es": "Búsqueda Echo", "de": "Echo-Suche",
        "fr": "Recherche Echo", "zh_CN": "Echo 搜索", "ja": "Echo 検索", "it": "Cerca Echo",
        "pt_BR": "Busca Echo", "tr": "Echo Arama", "uk": "Пошук Echo", "kk": "Echo іздеу", "ar": "بحث Echo"
    },
    "nav.search_placeholder": {
        "en": "Search", "ru": "Поиск", "es": "Buscar", "de": "Suchen",
        "fr": "Rechercher", "zh_CN": "搜索", "ja": "検索", "it": "Cerca",
        "pt_BR": "Buscar", "tr": "Ara", "uk": "Пошук", "kk": "Іздеу", "ar": "بحث"
    },

    # ── General Page ──
    "general.title": {
        "en": "General", "ru": "Основные", "es": "General", "de": "Allgemein",
        "fr": "Général", "zh_CN": "通用", "ja": "一般", "it": "Generali",
        "pt_BR": "Geral", "tr": "Genel", "uk": "Загальні", "kk": "Негізгі", "ar": "عام"
    },
    "general.dev_info": {
        "en": "Device Information", "ru": "Информация об устройстве", "es": "Información del dispositivo", "de": "Geräteinformationen",
        "fr": "Informations sur l'appareil", "zh_CN": "设备信息", "ja": "デバイス情報", "it": "Informazioni dispositivo",
        "pt_BR": "Informações do Dispositivo", "tr": "Cihaz Bilgisi", "uk": "Інформація про пристрій", "kk": "Құрылғы туралы ақпарат", "ar": "معلومات الجهاز"
    },
    "general.startup": {
        "en": "Startup", "ru": "Автозагрузка", "es": "Inicio", "de": "Autostart",
        "fr": "Démarrage", "zh_CN": "启动项", "ja": "スタートアップ", "it": "Avvio",
        "pt_BR": "Inicialização", "tr": "Başlangıç", "uk": "Автозапуск", "kk": "Автоқосылу", "ar": "بدء التشغيل"
    },
    "general.start_at_login": {
        "en": "Start Settings at Login", "ru": "Запускать настройки при входе", "es": "Iniciar al iniciar sesión", "de": "Beim Anmelden starten",
        "fr": "Lancer les paramètres à la connexion", "zh_CN": "开机登录时启动设置", "ja": "ログイン時に設定を起動", "it": "Avvia impostazioni al login",
        "pt_BR": "Iniciar Configurações ao Entrar", "tr": "Açılışta Ayarları Başlat", "uk": "Запускати налаштування під час входу", "kk": "Жүйеге кіргенде параметрлерді іске қосу", "ar": "بدء الإعدادات عند تسجيل الدخول"
    },
    "general.updates": {
        "en": "Updates", "ru": "Обновления", "es": "Actualizaciones", "de": "Aktualisierungen",
        "fr": "Mises à jour", "zh_CN": "软件更新", "ja": "アップデート", "it": "Aggiornamenti",
        "pt_BR": "Atualizações", "tr": "Güncellemeler", "uk": "Оновлення", "kk": "Жаңартулар", "ar": "التحديثات"
    },
    "general.system_up_to_date": {
        "en": "System is up to date", "ru": "Установлены последние обновления", "es": "El sistema está actualizado", "de": "System ist auf dem neuesten Stand",
        "fr": "Le système est à jour", "zh_CN": "系统已是最新版本", "ja": "システムは最新です", "it": "Il sistema è aggiornato",
        "pt_BR": "O sistema está atualizado", "tr": "Sistem güncel", "uk": "Встановлено найновіші оновлення", "kk": "Жүйе жаңартылған", "ar": "النظام محدث"
    },
    "general.last_checked": {
        "en": "Last checked: Today", "ru": "Последняя проверка: Сегодня", "es": "Última comprobación: Hoy", "de": "Zuletzt geprüft: Heute",
        "fr": "Dernière vérification : Aujourd'hui", "zh_CN": "上次检查：今天", "ja": "最終確認：今日", "it": "Ultimo controllo: Oggi",
        "pt_BR": "Última verificação: Hoje", "tr": "Son kontrol: Bugün", "uk": "Остання перевірка: Сьогодні", "kk": "Соңғы тексеру: Бүгін", "ar": "آخر فحص: اليوم"
    },
    "general.check_updates": {
        "en": "Check for Updates", "ru": "Проверить обновления", "es": "Buscar actualizaciones", "de": "Nach Updates suchen",
        "fr": "Rechercher des mises à jour", "zh_CN": "检查更新", "ja": "アップデートを確認", "it": "Verifica aggiornamenti",
        "pt_BR": "Verificar Atualizações", "tr": "Güncellemeleri Denetle", "uk": "Перевірити оновлення", "kk": "Жаңартуларды тексеру", "ar": "التحقق من وجود تحديثات"
    },
    "general.default_apps": {
        "en": "Default Applications", "ru": "Приложения по умолчанию", "es": "Aplicaciones predeterminadas", "de": "Standard-Anwendungen",
        "fr": "Applications par défaut", "zh_CN": "默认应用程序", "ja": "デフォルトのアプリ", "it": "Applicazioni predefinite",
        "pt_BR": "Aplicativos Padrão", "tr": "Varsayılan Uygulamalar", "uk": "Програми за замовчуванням", "kk": "Әдепкі қолданбалар", "ar": "التطبيقات الافتراضية"
    },
    "general.browser": {
        "en": "Web Browser", "ru": "Веб-браузер", "es": "Navegador web", "de": "Webbrowser",
        "fr": "Navigateur Web", "zh_CN": "网页浏览器", "ja": "Web ブラウザ", "it": "Browser Web",
        "pt_BR": "Navegador Web", "tr": "Web Tarayıcısı", "uk": "Веб-браузер", "kk": "Веб-шолғыш", "ar": "متصفح الويب"
    },
    "general.lang_region": {
        "en": "Language & Region", "ru": "Язык и регион", "es": "Idioma y región", "de": "Sprache & Region",
        "fr": "Langue et région", "zh_CN": "语言与地区", "ja": "言語と地域", "it": "Lingua e zona",
        "pt_BR": "Idioma e Região", "tr": "Dil ve Bölge", "uk": "Мова та регіон", "kk": "Тіл және аймақ", "ar": "اللغة والمنطقة"
    },
    "general.app_language": {
        "en": "Echo Settings Language", "ru": "Язык приложения Echo Settings", "es": "Idioma de Echo Settings", "de": "Sprache für Echo Settings",
        "fr": "Langue d'Echo Settings", "zh_CN": "Echo Settings 界面语言", "ja": "Echo Settings の言語", "it": "Lingua di Echo Settings",
        "pt_BR": "Idioma do Echo Settings", "tr": "Echo Settings Dili", "uk": "Мова застосунку Echo Settings", "kk": "Echo Settings қолданбасының тілі", "ar": "لغة تطبيق Echo Settings"
    },
    "general.system_language": {
        "en": "System Display Language", "ru": "Язык системы", "es": "Idioma del sistema", "de": "Systemsprache",
        "fr": "Langue du système", "zh_CN": "系统语言", "ja": "システム言語", "it": "Lingua di sistema",
        "pt_BR": "Idioma do Sistema", "tr": "Sistem Dili", "uk": "Мова системи", "kk": "Жүйе тілі", "ar": "لغة النظام"
    },
    "general.region": {
        "en": "Region", "ru": "Регион", "es": "Región", "de": "Region",
        "fr": "Région", "zh_CN": "地区", "ja": "地域", "it": "Regione",
        "pt_BR": "Região", "tr": "Bölge", "uk": "Регіон", "kk": "Аймақ", "ar": "المنطقة"
    },
    "general.first_day": {
        "en": "First Day of Week", "ru": "Первый день недели", "es": "Primer día de la semana", "de": "Erster Wochentag",
        "fr": "Premier jour de la semaine", "zh_CN": "每周第一天", "ja": "週の始まりの曜日", "it": "Primo giorno della settimana",
        "pt_BR": "Primeiro Dia da Semana", "tr": "Haftanın İlk Günü", "uk": "Перший день тижня", "kk": "Аптаның бірінші күні", "ar": "أول يوم في الأسبوع"
    },
    "general.monday": {
        "en": "Monday", "ru": "Понедельник", "es": "Lunes", "de": "Montag",
        "fr": "Lundi", "zh_CN": "星期一", "ja": "月曜日", "it": "Lunedì",
        "pt_BR": "Segunda-feira", "tr": "Pazartesi", "uk": "Понеділок", "kk": "Дүйсенбі", "ar": "الاثنين"
    },
    "general.sunday": {
        "en": "Sunday", "ru": "Воскресенье", "es": "Domingo", "de": "Sonntag",
        "fr": "Dimanche", "zh_CN": "星期日", "ja": "日曜日", "it": "Domenica",
        "pt_BR": "Domingo", "tr": "Pazar", "uk": "Неділя", "kk": "Жексенбі", "ar": "الأحد"
    },
    "general.date_time": {
        "en": "Date & Time", "ru": "Дата и время", "es": "Fecha y hora", "de": "Datum & Uhrzeit",
        "fr": "Date et heure", "zh_CN": "日期与时间", "ja": "日付と時刻", "it": "Data e ora",
        "pt_BR": "Data e Hora", "tr": "Tarih ve Saat", "uk": "Дата та час", "kk": "Күн мен уақыт", "ar": "التاريخ والوقت"
    },
    "general.auto_time": {
        "en": "Set Time Automatically", "ru": "Автоматическая установка времени", "es": "Ajustar hora automáticamente", "de": "Uhrzeit automatisch einstellen",
        "fr": "Régler l'heure automatiquement", "zh_CN": "自动设置时间", "ja": "自動的に日時を設定", "it": "Imposta data e ora automaticamente",
        "pt_BR": "Definir Hora Automaticamente", "tr": "Saati Otomatik Ayarla", "uk": "Встановлювати час автоматично", "kk": "Уақытты автоматты орнату", "ar": "تعيين الوقت تلقائيًا"
    },
    "general.timezone": {
        "en": "Timezone", "ru": "Часовой пояс", "es": "Zona horaria", "de": "Zeitzone",
        "fr": "Fuseau horaire", "zh_CN": "时区", "ja": "タイムゾーン", "it": "Fuso orario",
        "pt_BR": "Fuso Horário", "tr": "Saat Dilimi", "uk": "Часовий пояс", "kk": "Уақыт белдеуі", "ar": "المنطقة الزمنية"
    },
    "general.use_24h": {
        "en": "Use 24-hour clock", "ru": "24-часовой формат", "es": "Usar formato de 24 horas", "de": "24-Stunden-Format",
        "fr": "Utiliser le format 24 heures", "zh_CN": "使用 24 小时制", "ja": "24時間表示を使用", "it": "Usa il formato a 24 ore",
        "pt_BR": "Usar formato de 24 horas", "tr": "24 saat biçimini kullan", "uk": "Використовувати 24-годинний формат", "kk": "24 сағаттық пішім", "ar": "استخدام نظام 24 ساعة"
    },
    "general.quick_shortcuts": {
        "en": "Quick Shortcuts", "ru": "Быстрый переход", "es": "Accesos directos", "de": "Schnellzugriff",
        "fr": "Raccourcis rapides", "zh_CN": "快捷跳转", "ja": "クイックショートカット", "it": "Scorciatoie rapide",
        "pt_BR": "Atalhos Rápidos", "tr": "Hızlı Kısayollar", "uk": "Швидкий перехід", "kk": "Жылдам өту", "ar": "اختصارات سريعة"
    },
    "general.session": {
        "en": "Session", "ru": "Сеанс и питание", "es": "Sesión", "de": "Sitzung",
        "fr": "Session", "zh_CN": "会话与电源", "ja": "セッション", "it": "Sessione",
        "pt_BR": "Sessão", "tr": "Oturum", "uk": "Сеанс", "kk": "Сеанс", "ar": "الجلسة"
    },
    "general.lock_screen": {
        "en": "Lock Screen", "ru": "Заблокировать экран", "es": "Bloquear pantalla", "de": "Bildschirm sperren",
        "fr": "Verrouiller l'écran", "zh_CN": "锁定屏幕", "ja": "画面をロック", "it": "Blocca schermo",
        "pt_BR": "Bloquear Tela", "tr": "Ekranı Kilitle", "uk": "Заблокувати екран", "kk": "Экранды құлыптау", "ar": "قفل الشاشة"
    },
    "general.log_out": {
        "en": "Log Out", "ru": "Выйти из системы", "es": "Cerrar sesión", "de": "Abmelden",
        "fr": "Se déconnecter", "zh_CN": "退出登录", "ja": "ログアウト", "it": "Esci",
        "pt_BR": "Encerrar Sessão", "tr": "Oturumu Kapat", "uk": "Вийти із системи", "kk": "Жүйеден шығу", "ar": "تسجيل الخروج"
    },
    "general.restart": {
        "en": "Restart...", "ru": "Перезагрузить...", "es": "Reiniciar...", "de": "Neu starten...",
        "fr": "Redémarrer...", "zh_CN": "重新启动...", "ja": "再起動...", "it": "Riavvia...",
        "pt_BR": "Reiniciar...", "tr": "Yeniden Başlat...", "uk": "Перезавантажити...", "kk": "Қайта жүктеу...", "ar": "إعادة التشغيل..."
    },
    "general.power_off": {
        "en": "Shut Down...", "ru": "Выключить...", "es": "Apagar...", "de": "Ausschalten...",
        "fr": "Éteindre...", "zh_CN": "关机...", "ja": "システム終了...", "it": "Spegni...",
        "pt_BR": "Desligar...", "tr": "Kapat...", "uk": "Вимкнути...", "kk": "Сөндіру...", "ar": "إيقاف التشغيل..."
    },
    "general.software_update": {
        "en": "Software Update...", "ru": "Обновление ПО...", "es": "Actualización...", "de": "Softwareupdate...",
        "fr": "Mise à jour...", "zh_CN": "软件更新...", "ja": "ソフトウェアアップデート...", "it": "Aggiornamento...",
        "pt_BR": "Atualização de Software...", "tr": "Yazılım Güncelleme...", "uk": "Оновлення ПЗ...", "kk": "БҚ жаңарту...", "ar": "تحديث البرامج..."
    },
    "general.system_report": {
        "en": "System Report...", "ru": "Отчёт о системе...", "es": "Informe del sistema...", "de": "Systembericht...",
        "fr": "Rapport système...", "zh_CN": "系统报告...", "ja": "システムレポート...", "it": "Resoconto di sistema...",
        "pt_BR": "Relatório do Sistema...", "tr": "Sistem Raporu...", "uk": "Звіт про систему...", "kk": "Жүйе есебі...", "ar": "تقرير النظام..."
    },

    # ── Appearance Page ──
    "appearance.title": {
        "en": "Appearance", "ru": "Внешний вид", "es": "Aspecto", "de": "Erscheinungsbild",
        "fr": "Apparence", "zh_CN": "外观", "ja": "外観", "it": "Aspetto",
        "pt_BR": "Aparência", "tr": "Görünüm", "uk": "Вигляд", "kk": "Сыртқы түрі", "ar": "المظهر"
    },
    "appearance.theme": {
        "en": "THEME", "ru": "ТЕМА ОФОРМЛЕНИЯ", "es": "TEMA", "de": "DESIGN",
        "fr": "THÈME", "zh_CN": "主题模式", "ja": "テーマ", "it": "TEMA",
        "pt_BR": "TEMA", "tr": "TEMA", "uk": "ТЕМА", "kk": "ТАҚЫРЫП", "ar": "السمة"
    },
    "appearance.light": {
        "en": "Light", "ru": "Светлая", "es": "Claro", "de": "Hell",
        "fr": "Clair", "zh_CN": "浅色", "ja": "ライト", "it": "Chiaro",
        "pt_BR": "Claro", "tr": "Açık", "uk": "Світла", "kk": "Ашық", "ar": "فاتح"
    },
    "appearance.dark": {
        "en": "Dark", "ru": "Тёмная", "es": "Oscuro", "de": "Dunkel",
        "fr": "Sombre", "zh_CN": "深色", "ja": "ダーク", "it": "Scuro",
        "pt_BR": "Escuro", "tr": "Koyu", "uk": "Темна", "kk": "Күңгірт", "ar": "داكن"
    },
    "appearance.auto": {
        "en": "Auto", "ru": "Авто", "es": "Auto", "de": "Automatisch",
        "fr": "Automatique", "zh_CN": "自动", "ja": "自動", "it": "Automatico",
        "pt_BR": "Automático", "tr": "Otomatik", "uk": "Авто", "kk": "Авто", "ar": "تلقائي"
    },
    "appearance.accent_color": {
        "en": "ACCENT COLOR", "ru": "ЦВЕТ АКЦЕНТА", "es": "COLOR DE ÉNFASIS", "de": "AKZENTFARBE",
        "fr": "COULEUR D'ACCENTUATION", "zh_CN": "强调色", "ja": "アクセントカラー", "it": "COLORE RISALTO",
        "pt_BR": "COR DE DESTAQUE", "tr": "VURGU RENGİ", "uk": "АКЦЕНТНИЙ КОЛІР", "kk": "ЕКПІН ТҮСІ", "ar": "لون التمييز"
    },
    "appearance.system_accent": {
        "en": "System Accent", "ru": "Акцентный цвет системы", "es": "Color de énfasis del sistema", "de": "System-Akzentfarbe",
        "fr": "Couleur d'accent du système", "zh_CN": "系统强调色", "ja": "システムアクセント", "it": "Colore risalto del sistema",
        "pt_BR": "Cor de Destaque do Sistema", "tr": "Sistem Vurgu Rengi", "uk": "Акцентний колір системи", "kk": "Жүйенің екпінді түсі", "ar": "لون تمييز النظام"
    },
    "appearance.preview_button": {
        "en": "Action", "ru": "Действие", "es": "Acción", "de": "Aktion",
        "fr": "Action", "zh_CN": "操作", "ja": "アクション", "it": "Azione",
        "pt_BR": "Ação", "tr": "Eylem", "uk": "Дія", "kk": "Әрекет", "ar": "إجراء"
    },
    "appearance.preview_active": {
        "en": "Active ✓", "ru": "Активно ✓", "es": "Activo ✓", "de": "Aktiv ✓",
        "fr": "Actif ✓", "zh_CN": "已激活 ✓", "ja": "有効 ✓", "it": "Attivo ✓",
        "pt_BR": "Ativo ✓", "tr": "Aktif ✓", "uk": "Активно ✓", "kk": "Белсенді ✓", "ar": "مفعل ✓"
    },
    "appearance.preview_clicked": {
        "en": "Pressed!", "ru": "Нажато!", "es": "¡Pulsado!", "de": "Gedrückt!",
        "fr": "Cliqué !", "zh_CN": "已点击！", "ja": "クリック！", "it": "Premuto!",
        "pt_BR": "Pressionado!", "tr": "Tıklandı!", "uk": "Натиснуто!", "kk": "Басылды!", "ar": "تم الضغط!"
    },
    "appearance.preview_badge": {
        "en": "● Accent Live", "ru": "● Живой акцент", "es": "● Énfasis en vivo", "de": "● Live-Akzent",
        "fr": "● Accent en direct", "zh_CN": "● 实时强调色", "ja": "● ライブアクセント", "it": "● Risalto live",
        "pt_BR": "● Destaque ao vivo", "tr": "● Canlı Vurgu", "uk": "● Живий акцент", "kk": "● Жанды екпін", "ar": "● تمييز مباشر"
    },
    "appearance.preview_status_system": {
        "en": "System-wide Active", "ru": "Применено в системе", "es": "Activo en el sistema", "de": "Systemweit aktiv",
        "fr": "Actif dans le système", "zh_CN": "全系统已生效", "ja": "システム全体で有効", "it": "Attivo a livello di sistema",
        "pt_BR": "Ativo em todo o sistema", "tr": "Sistem genelinde etkin", "uk": "Застосовано в системі", "kk": "Жүйе бойынша белсенді", "ar": "مفعل على مستوى النظام"
    },
    "appearance.color_blue": {
        "en": "Blue", "ru": "Синий", "es": "Azul", "de": "Blau",
        "fr": "Bleu", "zh_CN": "蓝色", "ja": "ブルー", "it": "Blu",
        "pt_BR": "Azul", "tr": "Mavi", "uk": "Синій", "kk": "Көк", "ar": "أزرق"
    },
    "appearance.color_purple": {
        "en": "Purple", "ru": "Фиолетовый", "es": "Púrpura", "de": "Lila",
        "fr": "Violet", "zh_CN": "紫色", "ja": "パープル", "it": "Viola",
        "pt_BR": "Roxo", "tr": "Mor", "uk": "Фіолетовий", "kk": "Күлгін", "ar": "أرجواني"
    },
    "appearance.color_pink": {
        "en": "Pink", "ru": "Розовый", "es": "Rosa", "de": "Rosa",
        "fr": "Rose", "zh_CN": "粉色", "ja": "ピンク", "it": "Rosa",
        "pt_BR": "Rosa", "tr": "Pembe", "uk": "Рожевий", "kk": "Қызғылт", "ar": "وردي"
    },
    "appearance.color_red": {
        "en": "Red", "ru": "Красный", "es": "Rojo", "de": "Rot",
        "fr": "Rouge", "zh_CN": "红色", "ja": "レッド", "it": "Rosso",
        "pt_BR": "Vermelho", "tr": "Kırmızı", "uk": "Червоний", "kk": "Қызыл", "ar": "أحمر"
    },
    "appearance.color_orange": {
        "en": "Orange", "ru": "Оранжевый", "es": "Naranja", "de": "Orange",
        "fr": "Orange", "zh_CN": "橙色", "ja": "オレンジ", "it": "Arancione",
        "pt_BR": "Laranja", "tr": "Turuncu", "uk": "Помаранчевий", "kk": "Қызғылт сары", "ar": "برتقالي"
    },
    "appearance.color_yellow": {
        "en": "Yellow", "ru": "Жёлтый", "es": "Amarillo", "de": "Gelb",
        "fr": "Jaune", "zh_CN": "黄色", "ja": "イエロー", "it": "Giallo",
        "pt_BR": "Amarelo", "tr": "Sarı", "uk": "Жовтий", "kk": "Сары", "ar": "أصفر"
    },
    "appearance.color_green": {
        "en": "Green", "ru": "Зелёный", "es": "Verde", "de": "Grün",
        "fr": "Vert", "zh_CN": "绿色", "ja": "グリーン", "it": "Verde",
        "pt_BR": "Verde", "tr": "Yeşil", "uk": "Зелений", "kk": "Жасыл", "ar": "أخضر"
    },
    "appearance.color_teal": {
        "en": "Teal", "ru": "Бирюзовый", "es": "Turquesa", "de": "Türkis",
        "fr": "Sarcelle", "zh_CN": "青色", "ja": "ティール", "it": "Turchese",
        "pt_BR": "Turquesa", "tr": "Camgöbeği", "uk": "Бірюзовий", "kk": "Көгілдір", "ar": "تركواز"
    },
    "appearance.color_slate": {
        "en": "Graphite", "ru": "Графит", "es": "Grafito", "de": "Graphit",
        "fr": "Graphite", "zh_CN": "石墨灰", "ja": "グラファイト", "it": "Grafite",
        "pt_BR": "Grafite", "tr": "Grafit", "uk": "Графіт", "kk": "Графит", "ar": "غرافيت"
    },
    "appearance.color_multicolor": {
        "en": "Multicolor", "ru": "Автоматический", "es": "Multicolor", "de": "Mehrfarbig",
        "fr": "Multicolore", "zh_CN": "彩色", "ja": "マルチカラー", "it": "Multicolore",
        "pt_BR": "Multicolorido", "tr": "Çok Renkli", "uk": "Багатоколірний", "kk": "Көп түсті", "ar": "متعدد الألوان"
    },
    "appearance.wallpaper": {
        "en": "WALLPAPER", "ru": "ОБОИ", "es": "FONDO DE PANTALLA", "de": "SCHREIBTISCHHINTERGRUND",
        "fr": "FOND D'ÉCRAN", "zh_CN": "壁纸", "ja": "壁紙", "it": "SFONDO",
        "pt_BR": "PLANO DE FUNDO", "tr": "DUVAR KAĞIDI", "uk": "ШПАЛЕРИ", "kk": "ТҰСҚАҒАЗДАР", "ar": "خلفية الشاشة"
    },
    "wallpaper.dynamic_title": {
        "en": "Dynamic Time-of-Day Cycle", "ru": "Динамические обои (24ч)", "es": "Ciclo dinámico de 24 horas", "de": "Dynamischer 24-Stunden-Zyklus",
        "fr": "Cycle dynamique 24h", "zh_CN": "24小时动态壁纸循环", "ja": "24時間ダイナミック壁紙", "it": "Ciclo dinamico 24 ore",
        "pt_BR": "Ciclo Dinâmico de 24h", "tr": "24 Saatlik Dinamik Döngü", "uk": "Динамічний 24-годинний цикл", "kk": "24 сағаттық динамикалық цикл", "ar": "دورة ديناميكية على مدار 24 ساعة"
    },
    "wallpaper.timeline_auto": {
        "en": "Auto 24h", "ru": "Авто-время", "es": "Auto 24h", "de": "Auto 24h",
        "fr": "Auto 24h", "zh_CN": "自动跟随时间", "ja": "自動時間連動", "it": "Auto 24h",
        "pt_BR": "Automático 24h", "tr": "Otomatik 24s", "uk": "Авто 24г", "kk": "Авто 24сағ", "ar": "تلقائي 24 ساعة"
    },
    "wallpaper.btn_customize": {
        "en": "Customize Collection ⚙", "ru": "Настроить коллекцию ⚙", "es": "Personalizar colección ⚙", "de": "Sammlung anpassen ⚙",
        "fr": "Personnaliser la collection ⚙", "zh_CN": "自定义图集 ⚙", "ja": "コレクションを編集 ⚙", "it": "Personalizza raccolta ⚙",
        "pt_BR": "Personalizar Coleção ⚙", "tr": "Koleksiyonu Özelleştir ⚙", "uk": "Налаштувати колекцію ⚙", "kk": "Жинақты баптау ⚙", "ar": "تخصيص المجموعة ⚙"
    },
    "wallpaper.add_dynamic_card": {
        "en": "+ Create Dynamic Cycle...", "ru": "+ Создать цикл 24ч...", "es": "+ Crear ciclo dinámico...", "de": "+ Dynamischen Zyklus erstellen...",
        "fr": "+ Créer un cycle dynamique...", "zh_CN": "+ 创建动态图集...", "ja": "+ ダイナミックサイクルを作成...", "it": "+ Crea ciclo dinamico...",
        "pt_BR": "+ Criar Ciclo Dinâmico...", "tr": "+ Dinamik Döngü Oluştur...", "uk": "+ Створити цикл 24г...", "kk": "+ Динамикалық цикл жасау...", "ar": "+ إنشاء دورة ديناميكية..."
    },
    "wallpaper.phase_morning": {
        "en": "Morning / Sunrise", "ru": "Утро / Рассвет", "es": "Mañana / Amanecer", "de": "Morgen / Sonnenaufgang",
        "fr": "Matin / Lever du soleil", "zh_CN": "早晨 / 日出", "ja": "朝 / 日の出", "it": "Mattina / Alba",
        "pt_BR": "Manhã / Amanhecer", "tr": "Sabah / Gün Doğumu", "uk": "Ранок / Світанок", "kk": "Таң / Күн шығуы", "ar": "الصباح / الشروق"
    },
    "wallpaper.phase_day": {
        "en": "Day / Noon", "ru": "День / Полдень", "es": "Día / Mediodía", "de": "Tag / Mittag",
        "fr": "Jour / Midi", "zh_CN": "白天 / 中午", "ja": "昼 / 正午", "it": "Giorno / Mezzogiorno",
        "pt_BR": "Dia / Meio-dia", "tr": "Gündüz / Öğle", "uk": "День / Полудень", "kk": "Күндіз / Түс", "ar": "النهار / الظهر"
    },
    "wallpaper.phase_sunset": {
        "en": "Sunset / Golden Hour", "ru": "Закат / Золотой час", "es": "Atardecer / Hora dorada", "de": "Abend / Sonnenuntergang",
        "fr": "Coucher du soleil", "zh_CN": "傍晚 / 日落", "ja": "夕方 / 夕焼け", "it": "Tramonto",
        "pt_BR": "Pôr do Sol", "tr": "Akşam / Gün Batımı", "uk": "Захід / Золота година", "kk": "Кеш / Күн батуы", "ar": "الغروب / ساعة الغروب"
    },
    "wallpaper.phase_night": {
        "en": "Night / Stars", "ru": "Ночь / Звёзды", "es": "Noche / Estrellas", "de": "Nacht / Sterne",
        "fr": "Nuit / Étoiles", "zh_CN": "夜晚 / 星空", "ja": "夜 / 星空", "it": "Notte / Stelle",
        "pt_BR": "Noite / Estrelas", "tr": "Gece / Yıldızlar", "uk": "Ніч / Зорі", "kk": "Түн / Жұлдыздар", "ar": "الليل / النجوم"
    },
    "wallpaper.editor_title": {
        "en": "Custom Dynamic Wallpaper", "ru": "Настройка динамических обоев", "es": "Fondo dinámico personalizado", "de": "Benutzerdefiniertes dynamisches Hintergrundbild",
        "fr": "Fond d'écran dynamique personnalisé", "zh_CN": "自定义动态壁纸", "ja": "カスタムダイナミック壁紙", "it": "Sfondo dinamico personalizzato",
        "pt_BR": "Papel de Parede Dinâmico Personalizado", "tr": "Özel Dinamik Duvar Kağıdı", "uk": "Власні динамічні шпалери", "kk": "Жеке динамикалық тұсқағаз", "ar": "خلفية ديناميكية مخصصة"
    },
    "wallpaper.editor_heading": {
        "en": "24-Hour Dynamic Collection", "ru": "24-часовая коллекция обоев", "es": "Colección dinámica de 24 horas", "de": "24-Stunden-Dynamiksammlung",
        "fr": "Collection dynamique 24h", "zh_CN": "24小时动态壁纸集", "ja": "24時間ダイナミックコレクション", "it": "Raccolta dinamica 24 ore",
        "pt_BR": "Coleção Dinâmica de 24 Horas", "tr": "24 Saatlik Dinamik Koleksiyon", "uk": "24-годинна колекція шпалер", "kk": "24 сағаттық динамикалық жинақ", "ar": "مجموعة ديناميكية على مدار 24 ساعة"
    },
    "wallpaper.collection_name": {
        "en": "Collection Name:", "ru": "Название коллекции:", "es": "Nombre de la colección:", "de": "Sammlungsname:",
        "fr": "Nom de la collection :", "zh_CN": "图集名称：", "ja": "コレクション名：", "it": "Nome raccolta:",
        "pt_BR": "Nome da Coleção:", "tr": "Koleksiyon Adı:", "uk": "Назва колекції:", "kk": "Жинақ атауы:", "ar": "اسم المجموعة:"
    },
    "wallpaper.new_collection_default": {
        "en": "My Dynamic Horizon", "ru": "Мой динамический горизонт", "es": "Mi horizonte dinámico", "de": "Mein dynamischer Horizont",
        "fr": "Mon horizon dynamique", "zh_CN": "我的动态地平线", "ja": "マイダイナミックホライズン", "it": "Il mio orizzonte dinamico",
        "pt_BR": "Meu Horizonte Dinâmico", "tr": "Dinamik Ufuk", "uk": "Мій динамічний горизонт", "kk": "Менің динамикалық көкжиегім", "ar": "أفقي الديناميكي"
    },
    "wallpaper.configure_slots": {
        "en": "Daily Solar Phases:", "ru": "Суточные фазы времени:", "es": "Fases solares diarias:", "de": "Tägliche Sonnenphasen:",
        "fr": "Phases solaires du jour :", "zh_CN": "每日时间阶段：", "ja": "一日の時間帯フェーズ：", "it": "Fasi solari giornaliere:",
        "pt_BR": "Fases Solares do Dia:", "tr": "Günlük Güneş Aşamaları:", "uk": "Добові фази часу:", "kk": "Тәуліктік уақыт кезеңдері:", "ar": "مراحل اليوم الشمسية:"
    },
    "wallpaper.start_time": {
        "en": "Starts at:", "ru": "Начало в:", "es": "Comienza a las:", "de": "Beginnt um:",
        "fr": "Début à :", "zh_CN": "开始时间：", "ja": "開始時刻：", "it": "Inizia alle:",
        "pt_BR": "Inicia às:", "tr": "Başlangıç:", "uk": "Початок о:", "kk": "Басталуы:", "ar": "يبدأ في:"
    },
    "wallpaper.btn_browse": {
        "en": "Choose Image...", "ru": "Выбрать обои...", "es": "Elegir imagen...", "de": "Bild auswählen...",
        "fr": "Choisir une image...", "zh_CN": "选择图片...", "ja": "画像を選択...", "it": "Scegli immagine...",
        "pt_BR": "Escolher Imagem...", "tr": "Resim Seç...", "uk": "Обрати шпалери...", "kk": "Суретті таңдау...", "ar": "اختر صورة..."
    },
    "wallpaper.choose_file_title": {
        "en": "Select Wallpaper Image", "ru": "Выберите файл изображения", "es": "Seleccionar imagen de fondo", "de": "Hintergrundbild auswählen",
        "fr": "Sélectionner une image", "zh_CN": "选择壁纸图片", "ja": "壁紙画像を選択", "it": "Seleziona immagine sfondo",
        "pt_BR": "Selecionar Imagem de Fundo", "tr": "Duvar Kağıdı Resmi Seç", "uk": "Оберіть файл шпалер", "kk": "Тұсқағаз суретін таңдаңыз", "ar": "حدد صورة الخلفية"
    },
    "wallpaper.save_collection": {
        "en": "Save Collection ✓", "ru": "Сохранить коллекцию ✓", "es": "Guardar colección ✓", "de": "Sammlung speichern ✓",
        "fr": "Enregistrer la collection ✓", "zh_CN": "保存图集 ✓", "ja": "コレクションを保存 ✓", "it": "Salva raccolta ✓",
        "pt_BR": "Salvar Coleção ✓", "tr": "Koleksiyonu Kaydet ✓", "uk": "Зберегти колекцію ✓", "kk": "Жинақты сақтау ✓", "ar": "حفظ المجموعة ✓"
    },
    "appearance.fonts": {
        "en": "SYSTEM FONTS", "ru": "СИСТЕМНЫЕ ШРИФТЫ", "es": "FUENTES DEL SISTEMA", "de": "SYSTEMSCHRIFTARTEN",
        "fr": "POLICES DU SYSTÈME", "zh_CN": "系统字体", "ja": "システムフォント", "it": "FONT DI SISTEMA",
        "pt_BR": "FONTES DO SISTEMA", "tr": "SİSTEM YAZI TİPLERİ", "uk": "СИСТЕМНІ ШРИФТИ", "kk": "ЖҮЙЕЛІК ҚАРІПТЕР", "ar": "خطوط النظام"
    },
    "appearance.workspace_desktop": {
        "en": "WORKSPACE & DESKTOP", "ru": "РАБОЧИЕ СТОЛЫ И МНОГОЗАДАЧНОСТЬ", "es": "ESPACIOS DE TRABAJO Y ESCRITORIO", "de": "ARBEITSBEREICHE & DESKTOP",
        "fr": "ESPACES DE TRAVAIL ET MULTITÂCHE", "zh_CN": "工作区与桌面行为", "ja": "ワークスペースとデスクトップ", "it": "SPAZI DI LAVORO E DESKTOP",
        "pt_BR": "ÁREAS DE TRABALHO E MULTITAREFA", "tr": "ÇALIŞMA ALANLARI VE MASAÜSTÜ", "uk": "РОБОЧІ СТОЛИ ТА БАГАТОЗАДАЧНІСТЬ", "kk": "ЖҰМЫС ҮСТЕЛДЕРІ ЖӘНЕ КӨПТАПСЫРМАЛЫЛЫҚ", "ar": "مساحات العمل وسطح المكتب"
    },
    "appearance.hot_corners": {
        "en": "Hot Corners", "ru": "Активные углы", "es": "Esquinas activas", "de": "Aktive Ecken",
        "fr": "Coins actifs", "zh_CN": "触发角", "ja": "ホットコーナー", "it": "Angoli attivi",
        "pt_BR": "Cantos de Ação", "tr": "Etkin Köşeler", "uk": "Активні кути", "kk": "Белсенді бұрыштар", "ar": "الزوايا الفعالة"
    },
    "appearance.hot_corners_sub": {
        "en": "Touch the screen corners to trigger desktop shortcuts",
        "ru": "Наведите курсор в угол экрана для выполнения действия",
        "es": "Toque las esquinas de la pantalla para activar acciones",
        "de": "Berühren Sie die Bildschirmecken, um Aktionen auszulösen",
        "fr": "Pointez les coins de l'écran pour déclencher des actions",
        "zh_CN": "将鼠标移至屏幕角落以触发系统操作",
        "ja": "画面の隅にカーソルを移動してアクションを実行します",
        "it": "Tocca gli angoli dello schermo per eseguire azioni",
        "pt_BR": "Mova o cursor para os cantos da tela para executar ações",
        "tr": "İşlemleri tetiklemek için ekran köşelerine gelin",
        "uk": "Наведіть курсор у кут екрана для виконання дії",
        "kk": "Әрекетті орындау үшін курсорды экран бұрышына апарыңыз",
        "ar": "المس زوايا الشاشة لتشغيل اختصارات سطح المكتب"
    },
    "appearance.workspaces": {
        "en": "Workspaces", "ru": "Рабочие столы", "es": "Espacios de trabajo", "de": "Arbeitsbereiche",
        "fr": "Espaces de travail", "zh_CN": "工作区", "ja": "ワークスペース", "it": "Spazi di lavoro",
        "pt_BR": "Áreas de Trabalho", "tr": "Çalışma Alanları", "uk": "Робочі столи", "kk": "Жұмыс үстелдері", "ar": "مساحات العمل"
    },
    "appearance.workspaces_dynamic": {
        "en": "Dynamic workspaces", "ru": "Динамические рабочие столы", "es": "Espacios de trabajo dinámicos", "de": "Dynamische Arbeitsbereiche",
        "fr": "Espaces de travail dynamiques", "zh_CN": "动态工作区", "ja": "動的ワークスペース", "it": "Spazi di lavoro dinamici",
        "pt_BR": "Áreas de trabalho dinâmicas", "tr": "Dinamik çalışma alanları", "uk": "Динамічні робочі столи", "kk": "Динамикалық жұмыс үстелдері", "ar": "مساحات عمل ديناميكية"
    },
    "appearance.workspaces_dynamic_desc": {
        "en": "Automatically adds and removes workspaces as needed",
        "ru": "Автоматически создает и удаляет рабочие столы",
        "es": "Crea y elimina espacios de trabajo automáticamente",
        "de": "Arbeitsbereiche automatisch nach Bedarf erstellen und entfernen",
        "fr": "Crée et supprime automatiquement des espaces de travail",
        "zh_CN": "根据打开的窗口自动增减工作区数量",
        "ja": "必要に応じてワークスペースを自動的に追加および削除します",
        "it": "Aggiunge e rimuove automaticamente gli spazi di lavoro",
        "pt_BR": "Adiciona e remove áreas de trabalho automaticamente conforme necessário",
        "tr": "İhtiyaç duyuldukça çalışma alanlarını otomatik olarak ekler ve kaldırır",
        "uk": "Автоматично додає та видаляє робочі столи за потреби",
        "kk": "Жұмыс үстелдерін қажетінше автоматты түрде қосады және жояды",
        "ar": "إضافة وإزالة مساحات العمل تلقائيًا حسب الحاجة"
    },
    "appearance.workspaces_fixed": {
        "en": "Fixed number of workspaces", "ru": "Фиксированное количество рабочих столов", "es": "Número fijo de espacios de trabajo", "de": "Feste Anzahl an Arbeitsbereichen",
        "fr": "Nombre fixe d'espaces de travail", "zh_CN": "固定工作区数量", "ja": "固定数のワークスペース", "it": "Numero fisso di spazi di lavoro",
        "pt_BR": "Número fixo de áreas de trabalho", "tr": "Sabit sayıda çalışma alanı", "uk": "Фіксована кількість робочих столів", "kk": "Тұрақты жұмыс үстелдерінің саны", "ar": "عدد ثابت من مساحات العمل"
    },
    "appearance.workspaces_fixed_desc": {
        "en": "Specify a fixed workspace count", "ru": "Задать постоянное количество столов", "es": "Especificar un número fijo", "de": "Feste Anzahl festlegen",
        "fr": "Définir un nombre fixe d'espaces", "zh_CN": "指定固定的工作区总数", "ja": "ワークスペースの数を手動で指定", "it": "Specifica un conteggio fisso",
        "pt_BR": "Especificar uma contagem fixa de áreas", "tr": "Sabit bir çalışma alanı sayısı belirtin", "uk": "Вказати постійну кількість столів", "kk": "Үстелдердің тұрақты санын көрсету", "ar": "تحديد عدد ثابت لمساحات العمل"
    },
    "appearance.num_workspaces": {
        "en": "Number of Workspaces", "ru": "Количество столов", "es": "Número de espacios", "de": "Anzahl der Arbeitsbereiche",
        "fr": "Nombre d'espaces", "zh_CN": "工作区数量", "ja": "ワークスペースの数", "it": "Numero di spazi",
        "pt_BR": "Número de Áreas", "tr": "Çalışma Alanı Sayısı", "uk": "Кількість столів", "kk": "Үстелдер саны", "ar": "عدد مساحات العمل"
    },
    "appearance.multiple_displays": {
        "en": "Multiple Displays", "ru": "Несколько дисплеев", "es": "Múltiples pantallas", "de": "Mehrere Bildschirme",
        "fr": "Écrans multiples", "zh_CN": "多显示器", "ja": "マルチディスプレイ", "it": "Schermi multipli",
        "pt_BR": "Múltiplos Monitores", "tr": "Çoklu Ekranlar", "uk": "Кілька дисплеїв", "kk": "Бірнеше дисплей", "ar": "شاشات متعددة"
    },
    "appearance.multiple_displays_sub": {
        "en": "Configure how workspaces behave across connected displays", "ru": "Настройка отображения рабочих мест на подключённых дисплеях", "es": "Configurar espacios en monitores conectados", "de": "Verhalten der Arbeitsbereiche auf Monitoren festlegen",
        "fr": "Comportement des espaces sur les écrans connectés", "zh_CN": "配置多显示器下的工作区分配模式", "ja": "接続されたディスプレイ間での動作を設定", "it": "Comportamento degli spazi sui monitor collegati",
        "pt_BR": "Comportamento das áreas nos monitores conectados", "tr": "Bağlı ekranlardaki çalışma alanı davranışını ayarlayın", "uk": "Поведінка робочих столів на підключених дисплеях", "kk": "Қосылған дисплейлердегі жұмыс үстелдерінің әрекеті", "ar": "تكوين سلوك مساحات العمل عبر شاشات العرض"
    },
    "appearance.ws_primary_only": {
        "en": "Primary Display Only", "ru": "Только на основном дисплее", "es": "Solo en pantalla principal", "de": "Nur auf dem Hauptbildschirm",
        "fr": "Écran principal uniquement", "zh_CN": "仅在主显示器上使用工作区", "ja": "プライマリディスプレイのみ", "it": "Solo sullo schermo principale",
        "pt_BR": "Apenas no monitor principal", "tr": "Yalnızca birincil ekranda", "uk": "Лише на головному дисплеї", "kk": "Тек негізгі дисплейде", "ar": "الشاشة الرئيسية فقط"
    },
    "appearance.ws_primary_only_desc": {
        "en": "Workspaces are only shown and switched on the primary monitor", "ru": "Рабочие места переключаются только на основном мониторе", "es": "Los espacios solo cambian en el monitor principal", "de": "Arbeitsbereiche werden nur auf dem Hauptbildschirm umgeschaltet",
        "fr": "Les espaces ne changent que sur l'écran principal", "zh_CN": "副显示器保持固定，工作区仅在主显示器上切换", "ja": "プライマリモニター上でのみワークスペースが切り替わります", "it": "Gli spazi cambiano solo sul monitor principale",
        "pt_BR": "As áreas alternam apenas no monitor principal", "tr": "Çalışma alanları yalnızca birincil monitörde değişir", "uk": "Робочі столи перемикаються лише на головному моніторі", "kk": "Жұмыс үстелдері тек негізгі мониторда ауыстырылады", "ar": "يتم تبديل مساحات العمل على الشاشة الرئيسية فقط"
    },
    "appearance.ws_all_displays": {
        "en": "All Displays", "ru": "На всех дисплеях", "es": "En todas las pantallas", "de": "Auf allen Bildschirmen",
        "fr": "Sur tous les écrans", "zh_CN": "在所有显示器上均启用", "ja": "すべてのディスプレイ", "it": "Su tutti gli schermi",
        "pt_BR": "Em todos os monitores", "tr": "Tüm ekranlarda", "uk": "На всіх дисплеях", "kk": "Барлық дисплейлерде", "ar": "جميع شاشات العرض"
    },
    "appearance.ws_all_displays_desc": {
        "en": "Each display has its own independent set of workspaces", "ru": "Каждый подключённый дисплей имеет собственные рабочие места", "es": "Cada monitor tiene su propio conjunto de espacios", "de": "Jeder Bildschirm verfügt über eigene Arbeitsbereiche",
        "fr": "Chaque écran dispose de ses propres espaces", "zh_CN": "每个显示器都拥有独立的工作区切换", "ja": "各ディスプレイが独立したワークスペースを持ちます", "it": "Ogni monitor ha i propri spazi di lavoro",
        "pt_BR": "Cada monitor possui seu próprio conjunto de áreas", "tr": "Her ekranın kendi bağımsız çalışma alanı grubu vardır", "uk": "Кожен підключений дисплей має власні робочі столи", "kk": "Әрбір қосылған дисплейдің жеке жұмыс үстелдері болады", "ar": "تحتوي كل شاشة على مجموعة مساحات عمل مستقلة"
    },
    "appearance.app_switching": {
        "en": "Application Switching", "ru": "Переключение приложений", "es": "Cambio de aplicaciones", "de": "Anwendungswechsel",
        "fr": "Changement d'application", "zh_CN": "应用程序切换", "ja": "アプリケーションの切り替え", "it": "Cambio applicazione",
        "pt_BR": "Alternância de Aplicativos", "tr": "Uygulama Değiştirme", "uk": "Перемикання програм", "kk": "Қолданбаларды ауыстыру", "ar": "تبديل التطبيقات"
    },
    "appearance.app_switching_sub": {
        "en": "Choose which windows appear when pressing Alt+Tab", "ru": "Выбор окон, отображаемых при переключении клавишами Alt+Tab", "es": "Ventanas visibles al pulsar Alt+Tab", "de": "Sichtbare Fenster beim Drücken von Alt+Tab",
        "fr": "Fenêtres affichées lors de l'appui sur Alt+Tab", "zh_CN": "自定义按下 Alt+Tab 时参与切换的窗口范围", "ja": "Alt+Tab 押下時に切り替えるウィンドウを選択", "it": "Finestre visibili premendo Alt+Tab",
        "pt_BR": "Janelas visíveis ao pressionar Alt+Tab", "tr": "Alt+Tab tuşlarına basıldığında görünecek pencereleri seçin", "uk": "Вікна, які відображаються при натисканні Alt+Tab", "kk": "Alt+Tab пернелерін басқанда көрсетілетін терезелер", "ar": "اختيار النوافذ التي تظهر عند الضغط على Alt+Tab"
    },
    "appearance.app_all_ws": {
        "en": "All Workspaces", "ru": "Со всех рабочих мест", "es": "De todos los espacios", "de": "Aus allen Arbeitsbereichen",
        "fr": "De tous les espaces", "zh_CN": "包含所有工作区中的窗口", "ja": "すべてのワークスペース", "it": "Da tutti gli spazi",
        "pt_BR": "De todas as áreas", "tr": "Tüm çalışma alanlarından", "uk": "З усіх робочих столів", "kk": "Барлық жұмыс үстелдерінен", "ar": "من جميع مساحات العمل"
    },
    "appearance.app_all_ws_desc": {
        "en": "Switching includes applications across all active workspaces", "ru": "Переключение включает открытые окна со всех рабочих мест", "es": "Incluye ventanas de todos los espacios activos", "de": "Wechsel schließt Fenster aller aktiven Arbeitsbereiche ein",
        "fr": "Inclut les fenêtres de tous les espaces actifs", "zh_CN": "在全局所有工作区中检索并切换应用程序", "ja": "すべてのアクティブなワークスペース上のアプリを含めます", "it": "Include le finestre da tutti gli spazi attivi",
        "pt_BR": "Inclui janelas de todas as áreas ativas", "tr": "Tüm etkin çalışma alanlarındaki pencereleri içerir", "uk": "Включає вікна з усіх активних робочих столів", "kk": "Барлық белсенді жұмыс үстелдеріндегі терезелерді қамтиды", "ar": "يتضمن التبديل النوافذ عبر جميع مساحات العمل النشطة"
    },
    "appearance.app_current_ws": {
        "en": "Current Workspace Only", "ru": "Только с текущего рабочего места", "es": "Solo del espacio actual", "de": "Nur aus aktuellem Arbeitsbereich",
        "fr": "De l'espace actuel uniquement", "zh_CN": "仅限当前活动工作区", "ja": "現在のワークスペースのみ", "it": "Solo dallo spazio corrente",
        "pt_BR": "Apenas da área atual", "tr": "Yalnızca geçerli çalışma alanından", "uk": "Лише з поточного робочого столу", "kk": "Тек ағымдағы жұмыс үстелінен", "ar": "من مساحة العمل الحالية فقط"
    },
    "appearance.app_current_ws_desc": {
        "en": "Switching only includes applications on the currently active workspace", "ru": "Переключение ограничено окнами на активном в данный момент рабочем месте", "es": "Solo incluye ventanas del espacio activo", "de": "Wechsel ist auf den aktuell aktiven Arbeitsbereich beschränkt",
        "fr": "Ne prend en compte que l'espace actuellement actif", "zh_CN": "仅在当前正在使用的工作区内切换应用程序", "ja": "現在アクティブなワークスペース内のアプリのみ対象とします", "it": "Limita il cambio allo spazio attualmente attivo",
        "pt_BR": "Limita a alternância à área ativa no momento", "tr": "Yalnızca etkin çalışma alanındaki pencereleri içerir", "uk": "Обмежується вікнами на поточному робочому столі", "kk": "Тек ағымдағы белсенді жұмыс үстеліндегі терезелермен шектеледі", "ar": "يقتصر التبديل فقط على مساحة العمل النشطة حاليًا"
    },

    # ── Sound Page ──
    "sound.title": {
        "en": "Sound", "ru": "Звук", "es": "Sonido", "de": "Ton",
        "fr": "Son", "zh_CN": "声音", "ja": "サウンド", "it": "Suono",
        "pt_BR": "Som", "tr": "Ses", "uk": "Звук", "kk": "Дыбыс", "ar": "الصوت"
    },
    "sound.output": {
        "en": "OUTPUT", "ru": "ВЫВОД ЗВУКА", "es": "SALIDA", "de": "AUSGABE",
        "fr": "SORTIE", "zh_CN": "输出设备", "ja": "出力", "it": "USCITA",
        "pt_BR": "SAÍDA", "tr": "ÇIKIŞ", "uk": "ВИВЕДЕННЯ ЗВУКУ", "kk": "ШЫҒЫС ДЫБЫСЫ", "ar": "الإخراج"
    },
    "sound.input": {
        "en": "INPUT", "ru": "ВВОД ЗВУКА (МИКРОФОН)", "es": "ENTRADA", "de": "EINGABE",
        "fr": "ENTRÉE", "zh_CN": "输入设备 (麦克风)", "ja": "入力 (マイク)", "it": "INGRESSO",
        "pt_BR": "ENTRADA", "tr": "GİRİŞ", "uk": "ВВЕДЕННЯ ЗВУКУ", "kk": "КІРІС ДЫБЫСЫ", "ar": "الإدخال"
    },
    "sound.volume": {
        "en": "Volume", "ru": "Громкость", "es": "Volumen", "de": "Lautstärke",
        "fr": "Volume", "zh_CN": "主音量", "ja": "音量", "it": "Volume",
        "pt_BR": "Volume", "tr": "Ses Düzeyi", "uk": "Гучність", "kk": "Дыбыс деңгейі", "ar": "مستوى الصوت"
    },
    "sound.balance": {
        "en": "Balance", "ru": "Баланс", "es": "Balance", "de": "Balance",
        "fr": "Balance", "zh_CN": "声道平衡", "ja": "バランス", "it": "Bilanciamento",
        "pt_BR": "Balanço", "tr": "Denge", "uk": "Баланс", "kk": "Теңгерім", "ar": "التوازن"
    },
    "sound.mute": {
        "en": "Mute", "ru": "Заглушить", "es": "Silenciar", "de": "Stummschalten",
        "fr": "Couper le son", "zh_CN": "静音", "ja": "消音", "it": "Muto",
        "pt_BR": "Mudo", "tr": "Sessiz", "uk": "Вимкнути звук", "kk": "Дыбысты өшіру", "ar": "كتم الصوت"
    },
    "sound.effects": {
        "en": "SOUND EFFECTS", "ru": "ЗВУКОВЫЕ ЭФФЕКТЫ", "es": "EFECTOS DE SONIDO", "de": "TONEFFEKTE",
        "fr": "EFFETS SONORES", "zh_CN": "声音效果", "ja": "効果音", "it": "EFFETTI SONORI",
        "pt_BR": "EFEITOS SONOROS", "tr": "SES EFEKTLERİ", "uk": "ЗВУКОВІ ЕФЕКТИ", "kk": "ДЫБЫС ӘСЕРЛЕРІ", "ar": "المؤثرات الصوتية"
    },

    # ── Power Page ──
    "power.title": {
        "en": "Power", "ru": "Питание", "es": "Batería", "de": "Batterie",
        "fr": "Batterie", "zh_CN": "电池与电源", "ja": "バッテリー", "it": "Batteria",
        "pt_BR": "Bateria", "tr": "Güç", "uk": "Живлення", "kk": "Қуат", "ar": "الطاقة"
    },
    "power.mode": {
        "en": "POWER MODE", "ru": "РЕЖИМ ПИТАНИЯ", "es": "MODO DE ENERGÍA", "de": "ENERGIE-MODUS",
        "fr": "MODE D'ALIMENTATION", "zh_CN": "电源模式", "ja": "電源モード", "it": "MODALITÀ ENERGIA",
        "pt_BR": "MODO DE ENERGIA", "tr": "GÜÇ MODU", "uk": "РЕЖИМ ЖИВЛЕННЯ", "kk": "ҚУАТ РЕЖИМІ", "ar": "وضع الطاقة"
    },
    "power.balanced": {
        "en": "Balanced", "ru": "Сбалансированный", "es": "Equilibrado", "de": "Ausbalanciert",
        "fr": "Équilibré", "zh_CN": "平衡模式", "ja": "バランス", "it": "Bilanciato",
        "pt_BR": "Equilibrado", "tr": "Dengeli", "uk": "Збалансований", "kk": "Теңгерімді", "ar": "متوازن"
    },
    "power.performance": {
        "en": "Performance", "ru": "Производительность", "es": "Rendimiento", "de": "Leistung",
        "fr": "Performances", "zh_CN": "高性能模式", "ja": "パフォーマンス", "it": "Prestazioni",
        "pt_BR": "Desempenho", "tr": "Yüksek Performans", "uk": "Продуктивність", "kk": "Өнімділік", "ar": "الأداء العالي"
    },
    "power.saver": {
        "en": "Power Saver", "ru": "Энергосбережение", "es": "Ahorro de energía", "de": "Energiesparmodus",
        "fr": "Économie d'énergie", "zh_CN": "节能模式", "ja": "省電力", "it": "Risparmio energetico",
        "pt_BR": "Economia de Energia", "tr": "Güç Tasarrufu", "uk": "Енергозбереження", "kk": "Қуат үнемдеу", "ar": "توفير الطاقة"
    },
    "power.screen_blank": {
        "en": "Turn off screen when inactive", "ru": "Отключать экран при бездействии", "es": "Apagar pantalla al estar inactivo", "de": "Bildschirm bei Inaktivität ausschalten",
        "fr": "Éteindre l'écran en cas d'inactivité", "zh_CN": "闲置时关闭屏幕", "ja": "非操作時に画面をオフ", "it": "Spegni schermo quando inattivo",
        "pt_BR": "Desligar tela quando inativo", "tr": "Boşta kaldığında ekranı kapat", "uk": "Вимикати екран при бездіяльності", "kk": "Әрекетсіз болғанда экранды өшіру", "ar": "إيقاف تشغيل الشاشة عند عدم النشاط"
    },
    "power.auto_suspend": {
        "en": "Automatic Suspend", "ru": "Автоматический спящий режим", "es": "Suspensión automática", "de": "Automatischer Bereitschaftsmodus",
        "fr": "Mise en veille automatique", "zh_CN": "自动睡眠", "ja": "自動サスペンド", "it": "Sospensione automatica",
        "pt_BR": "Suspensão Automática", "tr": "Otomatik Askıya Alma", "uk": "Автоматичний режим сну", "kk": "Автоматты ұйқы режимі", "ar": "تعليق تلقائي"
    },

    "power.never": {
        "en": "Never", "ru": "Никогда", "es": "Nunca", "de": "Nie",
        "fr": "Jamais", "zh_CN": "从不", "ja": "しない", "it": "Mai",
        "pt_BR": "Nunca", "tr": "Hiçbir zaman", "uk": "Ніколи", "kk": "Ешқашан", "ar": "أبداً"
    },
    "power.1m": {"en": "1 minute", "ru": "1 минута", "es": "1 minuto", "de": "1 Minute", "fr": "1 minute", "zh_CN": "1 分钟", "ja": "1分", "it": "1 minuto", "pt_BR": "1 minuto", "tr": "1 dakika", "uk": "1 хвилина", "kk": "1 минут", "ar": "دقيقة واحدة"},
    "power.2m": {"en": "2 minutes", "ru": "2 минуты", "es": "2 minutos", "de": "2 Minuten", "fr": "2 minutes", "zh_CN": "2 分钟", "ja": "2分", "it": "2 minuti", "pt_BR": "2 minutos", "tr": "2 dakika", "uk": "2 хвилини", "kk": "2 минут", "ar": "دقيقتان"},
    "power.5m": {"en": "5 minutes", "ru": "5 минут", "es": "5 minutos", "de": "5 Minuten", "fr": "5 minutes", "zh_CN": "5 分钟", "ja": "5分", "it": "5 minuti", "pt_BR": "5 minutos", "tr": "5 dakika", "uk": "5 хвилин", "kk": "5 минут", "ar": "5 دقائق"},
    "power.10m": {"en": "10 minutes", "ru": "10 минут", "es": "10 minutos", "de": "10 Minuten", "fr": "10 minutes", "zh_CN": "10 分钟", "ja": "10分", "it": "10 minuti", "pt_BR": "10 minutos", "tr": "10 dakika", "uk": "10 хвилин", "kk": "10 минут", "ar": "10 دقائق"},
    "power.15m": {"en": "15 minutes", "ru": "15 минут", "es": "15 minutos", "de": "15 Minuten", "fr": "15 minutes", "zh_CN": "15 分钟", "ja": "15分", "it": "15 minuti", "pt_BR": "15 minutos", "tr": "15 dakika", "uk": "15 хвилин", "kk": "15 минут", "ar": "15 دقيقة"},
    "power.30m": {"en": "30 minutes", "ru": "30 минут", "es": "30 minutos", "de": "30 Minuten", "fr": "30 minutes", "zh_CN": "30 分钟", "ja": "30分", "it": "30 minuti", "pt_BR": "30 minutos", "tr": "30 dakika", "uk": "30 хвилин", "kk": "30 минут", "ar": "30 دقيقة"},
    "power.1h": {"en": "1 hour", "ru": "1 час", "es": "1 hora", "de": "1 Stunde", "fr": "1 heure", "zh_CN": "1 小时", "ja": "1時間", "it": "1 ora", "pt_BR": "1 hora", "tr": "1 saat", "uk": "1 година", "kk": "1 сағат", "ar": "ساعة واحدة"},
    "power.btn_sleep": {"en": "Sleep", "ru": "Спящий режим", "es": "Suspender", "de": "Ruhezustand", "fr": "Suspendre", "zh_CN": "睡眠", "ja": "スリープ", "it": "Sospendi", "pt_BR": "Suspender", "tr": "Uyut", "uk": "Режим сну", "kk": "Ұйқы режимі", "ar": "سكون"},
    "power.btn_poweroff": {"en": "Power Off", "ru": "Выключение", "es": "Apagar", "de": "Ausschalten", "fr": "Éteindre", "zh_CN": "关机", "ja": "電源オフ", "it": "Spegni", "pt_BR": "Desligar", "tr": "Kapat", "uk": "Вимкнення", "kk": "Сөндіру", "ar": "إيقاف التشغيل"},
    "power.btn_ask": {"en": "Ask", "ru": "Запрашивать действие", "es": "Preguntar", "de": "Nachfragen", "fr": "Demander", "zh_CN": "询问", "ja": "確認する", "it": "Chiedi", "pt_BR": "Perguntar", "tr": "Sor", "uk": "Запитувати", "kk": "Сұрау", "ar": "سؤال"},
    "power.btn_nothing": {"en": "Do Nothing", "ru": "Ничего не делать", "es": "No hacer nada", "de": "Keine Aktion", "fr": "Ne rien faire", "zh_CN": "无操作", "ja": "何もしない", "it": "Nessuna azione", "pt_BR": "Não fazer nada", "tr": "Hiçbir şey yapma", "uk": "Нічого не робити", "kk": "Ештеңе істемеу", "ar": "عدم القيام بشيء"},
    "power.button_action": {
        "en": "Power Button Action", "ru": "Действие кнопки питания", "es": "Acción del botón de encendido", "de": "Aktion des Ein-/Ausschalters",
        "fr": "Action du bouton d'alimentation", "zh_CN": "电源按键行为", "ja": "電源ボタンの動作", "it": "Azione pulsante di accensione",
        "pt_BR": "Ação do Botão Liga/Desliga", "tr": "Güç Düğmesi Eylemi", "uk": "Дія кнопки живлення", "kk": "Қуат батырмасының әрекеті", "ar": "إجراء زر الطاقة"
    },
    "power.charge": {
        "en": "Current Charge", "ru": "Текущий заряд", "es": "Carga actual", "de": "Aktueller Ladestand",
        "fr": "Charge actuelle", "zh_CN": "当前电量", "ja": "現在のバッテリー残量", "it": "Carica attuale",
        "pt_BR": "Carga Atual", "tr": "Geçerli Şarj", "uk": "Поточний заряд", "kk": "Ағымдағы заряд", "ar": "الشحن الحالي"
    },
    "general.device_name": {
        "en": "Device Name", "ru": "Имя устройства", "es": "Nombre del dispositivo", "de": "Gerätename",
        "fr": "Nom de l'appareil", "zh_CN": "设备名称", "ja": "デバイス名", "it": "Nome dispositivo",
        "pt_BR": "Nome do Dispositivo", "tr": "Cihaz Adı", "uk": "Назва пристрою", "kk": "Құрылғы атауы", "ar": "اسم الجهاز"
    },
    "general.processor": {
        "en": "Processor", "ru": "Процессор (CPU)", "es": "Procesador", "de": "Prozessor",
        "fr": "Processeur", "zh_CN": "处理器", "ja": "プロセッサ", "it": "Processore",
        "pt_BR": "Processador", "tr": "İşlemci", "uk": "Процесор", "kk": "Процессор", "ar": "المعالج"
    },
    "general.graphics": {
        "en": "Graphics", "ru": "Видеокарта (GPU)", "es": "Gráficos", "de": "Grafikkarte",
        "fr": "Carte graphique", "zh_CN": "显卡", "ja": "グラフィックス", "it": "Grafica",
        "pt_BR": "Placa de Vídeo", "tr": "Grafik Kartı", "uk": "Відеокарта", "kk": "Бейнекарта", "ar": "بطاقة الرسوميات"
    },
    "general.memory": {
        "en": "Memory", "ru": "Память (RAM)", "es": "Memoria", "de": "Speicher",
        "fr": "Mémoire", "zh_CN": "内存", "ja": "メモリ", "it": "Memoria",
        "pt_BR": "Memória", "tr": "Bellek", "uk": "Пам'ять", "kk": "Жад", "ar": "الذاكرة"
    },
    "general.disk_capacity": {
        "en": "Storage Disk", "ru": "Основной диск", "es": "Disco de almacenamiento", "de": "Festplatte",
        "fr": "Disque de stockage", "zh_CN": "存储磁盘", "ja": "ストレージディスク", "it": "Disco di archiviazione",
        "pt_BR": "Disco de Armazenamento", "tr": "Depolama Diski", "uk": "Основний диск", "kk": "Негізгі диск", "ar": "قرص التخزين"
    },
    "general.os_name": {
        "en": "OS Kernel", "ru": "Ядро ОС", "es": "Núcleo del SO", "de": "Betriebssystem-Kernel",
        "fr": "Noyau de l'OS", "zh_CN": "系统内核", "ja": "OS カーネル", "it": "Kernel del sistema",
        "pt_BR": "Kernel do SO", "tr": "İşletim Sistemi Çekirdeği", "uk": "Ядро ОС", "kk": "ОЖ ядросы", "ar": "نواة النظام"
    },
    # ── Storage Page ──
    "storage.title": {
        "en": "Storage", "ru": "Хранилище", "es": "Almacenamiento", "de": "Speicher",
        "fr": "Stockage", "zh_CN": "储存空间", "ja": "ストレージ", "it": "Spazio",
        "pt_BR": "Armazenamento", "tr": "Depolama", "uk": "Сховище", "kk": "Жад", "ar": "التخزين"
    },
    "storage.system": {
        "en": "System", "ru": "Система", "es": "Sistema", "de": "System",
        "fr": "Système", "zh_CN": "系统", "ja": "システム", "it": "Sistema",
        "pt_BR": "Sistema", "tr": "Sistem", "uk": "Система", "kk": "Жүйе", "ar": "النظام"
    },
    "storage.games": {
        "en": "Games", "ru": "Игры", "es": "Juegos", "de": "Spiele",
        "fr": "Jeux", "zh_CN": "游戏", "ja": "ゲーム", "it": "Giochi",
        "pt_BR": "Jogos", "tr": "Oyunlar", "uk": "Ігри", "kk": "Ойындар", "ar": "الألعاب"
    },
    "storage.applications": {
        "en": "Applications", "ru": "Приложения", "es": "Aplicaciones", "de": "Programme",
        "fr": "Applications", "zh_CN": "应用程序", "ja": "アプリケーション", "it": "Applicazioni",
        "pt_BR": "Aplicativos", "tr": "Uygulamalar", "uk": "Програми", "kk": "Қолданбалар", "ar": "التطبيقات"
    },
    "storage.apps": {
        "en": "Applications", "ru": "Приложения", "es": "Aplicaciones", "de": "Programme",
        "fr": "Applications", "zh_CN": "应用程序", "ja": "アプリケーション", "it": "Applicazioni",
        "pt_BR": "Aplicativos", "tr": "Uygulamalar", "uk": "Програми", "kk": "Қолданбалар", "ar": "التطبيقات"
    },
    "storage.downloads": {
        "en": "Downloads", "ru": "Загрузки", "es": "Descargas", "de": "Downloads",
        "fr": "Téléchargements", "zh_CN": "下载", "ja": "ダウンロード", "it": "Download",
        "pt_BR": "Downloads", "tr": "İndirilenler", "uk": "Завантаження", "kk": "Жүктеулер", "ar": "التنزيلات"
    },
    "storage.pictures": {
        "en": "Pictures", "ru": "Фото", "es": "Fotos", "de": "Fotos",
        "fr": "Photos", "zh_CN": "照片", "ja": "写真", "it": "Foto",
        "pt_BR": "Fotos", "tr": "Fotoğraflar", "uk": "Фото", "kk": "Суреттер", "ar": "الصور"
    },
    "storage.videos": {
        "en": "Videos", "ru": "Видео", "es": "Vídeos", "de": "Videos",
        "fr": "Vidéos", "zh_CN": "视频", "ja": "ビデオ", "it": "Video",
        "pt_BR": "Vídeos", "tr": "Videolar", "uk": "Відео", "kk": "Бейнелер", "ar": "الفيديوهات"
    },
    "storage.music": {
        "en": "Music", "ru": "Музыка", "es": "Música", "de": "Musik",
        "fr": "Musique", "zh_CN": "音乐", "ja": "ミュージック", "it": "Musica",
        "pt_BR": "Música", "tr": "Müzik", "uk": "Музика", "kk": "Музыка", "ar": "الموسيقى"
    },
    "storage.documents": {
        "en": "Documents", "ru": "Документы", "es": "Documentos", "de": "Dokumente",
        "fr": "Documents", "zh_CN": "文稿", "ja": "書類", "it": "Documenti",
        "pt_BR": "Documentos", "tr": "Belgeler", "uk": "Документи", "kk": "Құжаттар", "ar": "المستندات"
    },
    "storage.docs": {
        "en": "Documents", "ru": "Документы", "es": "Documentos", "de": "Dokumente",
        "fr": "Documents", "zh_CN": "文稿", "ja": "書類", "it": "Documenti",
        "pt_BR": "Documentos", "tr": "Belgeler", "uk": "Документи", "kk": "Құжаттар", "ar": "المستندات"
    },
    "storage.dev": {
        "en": "Developer", "ru": "Разработка", "es": "Desarrollo", "de": "Entwickler",
        "fr": "Développeur", "zh_CN": "开发者", "ja": "デベロッパ", "it": "Sviluppatore",
        "pt_BR": "Desenvolvedor", "tr": "Geliştirici", "uk": "Розробка", "kk": "Әзірлеу", "ar": "المطور"
    },
    "storage.trash": {
        "en": "Trash", "ru": "Корзина", "es": "Papelera", "de": "Papierkorb",
        "fr": "Corbeille", "zh_CN": "废纸篓", "ja": "ゴミ箱", "it": "Cestino",
        "pt_BR": "Lixeira", "tr": "Çöp Kutusu", "uk": "Смітник", "kk": "Себет", "ar": "سلة المهملات"
    },
    "storage.other": {
        "en": "Other", "ru": "Другое", "es": "Otros", "de": "Sonstiges",
        "fr": "Autre", "zh_CN": "其他", "ja": "その他", "it": "Altro",
        "pt_BR": "Outros", "tr": "Diğer", "uk": "Інше", "kk": "Басқа", "ar": "أخرى"
    },
    "storage.used": {
        "en": "Used", "ru": "Занято", "es": "Usado", "de": "Belegt",
        "fr": "Utilisé", "zh_CN": "已用", "ja": "使用済み", "it": "Utilizzato",
        "pt_BR": "Usado", "tr": "Kullanılan", "uk": "Використано", "kk": "Пайдаланылған", "ar": "المستخدم"
    },
    "storage.free": {
        "en": "Free Space", "ru": "Свободно", "es": "Espacio libre", "de": "Freier Speicher",
        "fr": "Espace libre", "zh_CN": "可用空间", "ja": "空き領域", "it": "Spazio disponibile",
        "pt_BR": "Espaço Livre", "tr": "Boş Alan", "uk": "Вільно", "kk": "Бос орын", "ar": "المساحة الخالية"
    },
    "storage.recommendations": {
        "en": "Recommendations", "ru": "Рекомендации", "es": "Recomendaciones", "de": "Empfehlungen",
        "fr": "Recommandations", "zh_CN": "优化建议", "ja": "おすすめ", "it": "Consigli",
        "pt_BR": "Recomendações", "tr": "Öneriler", "uk": "Рекомендації", "kk": "Ұсыныстар", "ar": "التوصيات"
    },
    "storage.disk_info": {
        "en": "Disk Information", "ru": "Информация о диске", "es": "Información del disco", "de": "Festplatten-Info",
        "fr": "Informations sur le disque", "zh_CN": "磁盘详情", "ja": "ディスク情報", "it": "Informazioni disco",
        "pt_BR": "Informações do Disco", "tr": "Disk Bilgileri", "uk": "Інформація про диск", "kk": "Диск ақпараты", "ar": "معلومات القرص"
    },
    "storage.volumes": {
        "en": "Volumes", "ru": "Тома и разделы", "es": "Volúmenes", "de": "Volumes",
        "fr": "Volumes", "zh_CN": "储存卷与分区", "ja": "ボリューム", "it": "Volumi",
        "pt_BR": "Volumes", "tr": "Birimler", "uk": "Томи та розділи", "kk": "Томдар мен бөлімдер", "ar": "وحدات التخزين"
    },
    "storage.largest_files": {
        "en": "Largest Files", "ru": "Крупные файлы", "es": "Archivos más grandes", "de": "Größte Dateien",
        "fr": "Fichiers les plus volumineux", "zh_CN": "大文件", "ja": "大容量ファイル", "it": "File più grandi",
        "pt_BR": "Maiores Arquivos", "tr": "En Büyük Dosyalar", "uk": "Великі файли", "kk": "Ең үлкен файлдар", "ar": "أكبر الملفات"
    },
    "storage.storage_health": {
        "en": "Storage Health", "ru": "Состояние накопителя", "es": "Salud del almacenamiento", "de": "Speicherzustand",
        "fr": "Santé du stockage", "zh_CN": "硬盘健康状态", "ja": "ストレージの状態", "it": "Stato del disco",
        "pt_BR": "Saúde do Armazenamento", "tr": "Depolama Sağlığı", "uk": "Стан накопичувача", "kk": "Жад күйі", "ar": "صحة التخزين"
    },
    "storage.healthy": {
        "en": "Healthy", "ru": "В норме", "es": "Saludable", "de": "Gut",
        "fr": "Sain", "zh_CN": "良好", "ja": "正常", "it": "Ottimale",
        "pt_BR": "Saudável", "tr": "Sağlıklı", "uk": "У нормі", "kk": "Қалыпты", "ar": "سليم"
    },
    "storage.model": {"en": "Model", "ru": "Модель", "es": "Modelo", "de": "Modell", "fr": "Modèle", "zh_CN": "型号", "ja": "モデル", "it": "Modello", "pt_BR": "Modelo", "tr": "Model", "uk": "Модель", "kk": "Үлгі", "ar": "النموذج"},
    "storage.interface": {"en": "Interface", "ru": "Интерфейс", "es": "Interfaz", "de": "Schnittstelle", "fr": "Interface", "zh_CN": "接口", "ja": "インターフェース", "it": "Interfaccia", "pt_BR": "Interface", "tr": "Arayüz", "uk": "Інтерфейс", "kk": "Интерфейс", "ar": "الواجهة"},
    "storage.capacity": {"en": "Capacity", "ru": "Ёмкость", "es": "Capacidad", "de": "Kapazität", "fr": "Capacité", "zh_CN": "容量", "ja": "容量", "it": "Capacità", "pt_BR": "Capacidade", "tr": "Kapasite", "uk": "Місткість", "kk": "Сыйымдылық", "ar": "السعة"},
    "storage.filesystem": {"en": "Filesystem", "ru": "Файловая система", "es": "Sistema de archivos", "de": "Dateisystem", "fr": "Système de fichiers", "zh_CN": "文件系统", "ja": "ファイルシステム", "it": "File system", "pt_BR": "Sistema de Arquivos", "tr": "Dosya Sistemi", "uk": "Файлова система", "kk": "Файлдық жүйе", "ar": "نظام الملفات"},
    "storage.mountpoint": {"en": "Mount Point", "ru": "Точка монтирования", "es": "Punto de montaje", "de": "Einhängepunkt", "fr": "Point de montage", "zh_CN": "挂载点", "ja": "マウントポイント", "it": "Punto di montaggio", "pt_BR": "Ponto de Montagem", "tr": "Bağlama Noktası", "uk": "Точка монтування", "kk": "Тіркеу нүктесі", "ar": "نقطة التوصيل"},
    "storage.temperature": {"en": "Temperature", "ru": "Температура", "es": "Temperatura", "de": "Temperatur", "fr": "Température", "zh_CN": "温度", "ja": "温度", "it": "Temperatura", "pt_BR": "Temperatura", "tr": "Sıcaklık", "uk": "Температура", "kk": "Температура", "ar": "درجة الحرارة"},
    "storage.serial": {"en": "Serial", "ru": "Серийный номер", "es": "Número de serie", "de": "Seriennummer", "fr": "Numéro de série", "zh_CN": "序列号", "ja": "シリアル番号", "it": "Numero di serie", "pt_BR": "Número de Série", "tr": "Seri Numarası", "uk": "Серійний номер", "kk": "Сериялық нөмірі", "ar": "الرقم التسلسلي"},

    # ── Display Page ──
    "display.no_displays": {"en": "No displays found.", "ru": "Дисплеи не обнаружены.", "es": "No se encontraron pantallas.", "de": "Keine Displays gefunden.", "fr": "Aucun écran trouvé.", "zh_CN": "未找到显示器。", "ja": "ディスプレイが見つかりません。", "it": "Nessuno schermo trovato.", "pt_BR": "Nenhum monitor encontrado.", "tr": "Ekran bulunamadı.", "uk": "Дисплеї не знайдено.", "kk": "Дисплейлер табылмады.", "ar": "لم يتم العثور على شاشات."},
    "display.arrange_btn": {"en": "Arrange Displays...", "ru": "Расстановка дисплеев...", "es": "Organizar pantallas...", "de": "Monitore anordnen...", "fr": "Organiser les écrans...", "zh_CN": "排列显示器...", "ja": "ディスプレイの配置...", "it": "Disponi schermi...", "pt_BR": "Organizar Monitores...", "tr": "Ekranları Düzenle...", "uk": "Розташування дисплеїв...", "kk": "Дисплейлерді реттеу...", "ar": "ترتيب شاشات العرض..."},
    "display.layout_position": {"en": "LAYOUT & POSITION", "ru": "РАЗРЕШЕНИЕ И ОРИЕНТАЦИЯ", "es": "DISPOSICIÓN Y POSICIÓN", "de": "LAYOUT & POSITION", "fr": "DISPOSITION ET POSITION", "zh_CN": "显示布局与位置", "ja": "配置と解像度", "it": "DISPOSIZIONE E POSIZIONE", "pt_BR": "LAYOUT E POSIÇÃO", "tr": "DÜZEN VE KONUM", "uk": "РОЗДІЛЬНА ЗДАТНІСТЬ ТА ОРІЄНТАЦІЯ", "kk": "АЖЫРАТЫМДЫЛЫҚ ПЕН БАҒЫТ", "ar": "التخطيط والموضع"},
    "display.resolution": {"en": "Resolution", "ru": "Разрешение", "es": "Resolución", "de": "Auflösung", "fr": "Résolution", "zh_CN": "分辨率", "ja": "解像度", "it": "Risoluzione", "pt_BR": "Resolução", "tr": "Çözünürlük", "uk": "Роздільна здатність", "kk": "Ажыратымдылық", "ar": "الدقة"},
    "display.refresh_rate": {"en": "Refresh Rate", "ru": "Частота обновления", "es": "Frecuencia de actualización", "de": "Bildwiederholrate", "fr": "Fréquence de rafraîchissement", "zh_CN": "刷新率", "ja": "リフレッシュレート", "it": "Frequenza di aggiornamento", "pt_BR": "Taxa de Atualização", "tr": "Yenileme Hızı", "uk": "Частота оновлення", "kk": "Жаңарту жиілігі", "ar": "معدل التحديث"},
    "display.orientation": {"en": "Orientation", "ru": "Ориентация", "es": "Orientación", "de": "Ausrichtung", "fr": "Orientation", "zh_CN": "旋转方向", "ja": "向き", "it": "Orientamento", "pt_BR": "Orientação", "tr": "Yönlendirme", "uk": "Орієнтація", "kk": "Бағыты", "ar": "الاتجاه"},
    "display.orient_std": {"en": "Standard (0°)", "ru": "Стандартная (0°)", "es": "Estándar (0°)", "de": "Standard (0°)", "fr": "Standard (0°)", "zh_CN": "标准 (0°)", "ja": "標準 (0°)", "it": "Standard (0°)", "pt_BR": "Padrão (0°)", "tr": "Standart (0°)", "uk": "Стандартна (0°)", "kk": "Стандартты (0°)", "ar": "قياسي (0°)"},
    "display.orient_90r": {"en": "90° Right", "ru": "90° вправо", "es": "90° a la derecha", "de": "90° rechts", "fr": "90° à droite", "zh_CN": "向右旋转 90°", "ja": "90° 右回転", "it": "90° destra", "pt_BR": "90° para a Direita", "tr": "90° Sağa", "uk": "90° праворуч", "kk": "90° оңға", "ar": "90° يمين"},
    "display.orient_90l": {"en": "90° Left", "ru": "90° влево", "es": "90° a la izquierda", "de": "90° links", "fr": "90° à gauche", "zh_CN": "向左旋转 90°", "ja": "90° 左回転", "it": "90° sinistra", "pt_BR": "90° para a Esquerda", "tr": "90° Sola", "uk": "90° ліворуч", "kk": "90° солға", "ar": "90° يسار"},
    "display.orient_180": {"en": "180°", "ru": "180°", "es": "180°", "de": "180°", "fr": "180°", "zh_CN": "180°", "ja": "180°", "it": "180°", "pt_BR": "180°", "tr": "180°", "uk": "180°", "kk": "180°", "ar": "180°"},
    "display.use_as_main": {"en": "Use as Main Display", "ru": "Использовать как основной дисплей", "es": "Usar como pantalla principal", "de": "Als Hauptbildschirm verwenden", "fr": "Utiliser comme écran principal", "zh_CN": "设为主显示器", "ja": "主ディスプレイとして使用", "it": "Usa come schermo principale", "pt_BR": "Usar como Monitor Principal", "tr": "Ana Ekran Olarak Kullan", "uk": "Використовувати як головний дисплей", "kk": "Негізгі дисплей ретінде пайдалану", "ar": "استخدام كشاشة رئيسية"},
    "display.scale": {"en": "Scale", "ru": "Масштабирование", "es": "Escala", "de": "Skalierung", "fr": "Échelle", "zh_CN": "缩放比例", "ja": "拡大縮小", "it": "Scala", "pt_BR": "Escala", "tr": "Ölçek", "uk": "Масштабування", "kk": "Масштабтау", "ar": "المقياس"},
    "display.scale_desc": {"en": "Larger text may reduce available space on screen.", "ru": "Увеличенный масштаб может уменьшить доступное пространство на экране.", "es": "Un texto más grande puede reducir el espacio en pantalla.", "de": "Größerer Text kann den verfügbaren Platz auf dem Bildschirm verringern.", "fr": "Un texte plus grand peut réduire l'espace disponible à l'écran.", "zh_CN": "更大的缩放可能会减少屏幕可用显示空间。", "ja": "テキストを拡大すると、画面上の利用可能なスペースが減少する場合があります。", "it": "Un testo più grande potrebbe ridurre lo spazio disponibile sullo schermo.", "pt_BR": "Textos maiores podem reduzir o espaço disponível na tela.", "tr": "Büyük metin ekrandaki kullanılabilir alanı azaltabilir.", "uk": "Більший текст може зменшити доступний простір на екрані.", "kk": "Үлкейтілген мәтін экрандағы бос орынды азайтуы мүмкін.", "ar": "قد يقلل النص الأكبر من المساحة المتوفرة على الشاشة."},
    "display.color_brightness": {"en": "COLOR & BRIGHTNESS", "ru": "ЦВЕТОПЕРЕДАЧА И ЯРКОСТЬ", "es": "COLOR Y BRILLO", "de": "FARBE & HELLIGKEIT", "fr": "COULEUR ET LUMINOSITÉ", "zh_CN": "色彩与亮度", "ja": "カラーと輝度", "it": "COLORE E LUMINOSITÀ", "pt_BR": "COR E BRILHO", "tr": "RENK VE PARLAKLIK", "uk": "КОЛЬОРИ ТА ЯСКРАВІСТЬ", "kk": "ТҮС ПЕН ЖАРЫҚТЫҚ", "ar": "اللون والسطوع"},
    "display.brightness": {"en": "Brightness", "ru": "Яркость дисплея", "es": "Brillo", "de": "Helligkeit", "fr": "Luminosité", "zh_CN": "显示器亮度", "ja": "輝度", "it": "Luminosità", "pt_BR": "Brilho", "tr": "Parlaklık", "uk": "Яскравість", "kk": "Жарықтық", "ar": "السطوع"},
    "display.color_profile": {"en": "Color Profile", "ru": "Цветовой профиль", "es": "Perfil de color", "de": "Farbprofil", "fr": "Profil de couleur", "zh_CN": "色彩描述文件", "ja": "カラープロファイル", "it": "Profilo colore", "pt_BR": "Perfil de Cor", "tr": "Renk Profili", "uk": "Колірний профіль", "kk": "Түс профилі", "ar": "ملف تعريف الألوان"},
    "display.enable_hdr": {"en": "Enable HDR", "ru": "Включить HDR", "es": "Activar HDR", "de": "HDR aktivieren", "fr": "Activer HDR", "zh_CN": "启用 HDR", "ja": "HDR を有効にする", "it": "Abilita HDR", "pt_BR": "Ativar HDR", "tr": "HDR'yi Etkinleştir", "uk": "Увімкнути HDR", "kk": "HDR қосу", "ar": "تمكين HDR"},
    "display.sdr_brightness": {"en": "SDR Brightness", "ru": "Яркость SDR", "es": "Brillo SDR", "de": "SDR-Helligkeit", "fr": "Luminosité SDR", "zh_CN": "SDR 亮度", "ja": "SDR 輝度", "it": "Luminosità SDR", "pt_BR": "Brilho SDR", "tr": "SDR Parlaklığı", "uk": "Яскравість SDR", "kk": "SDR жарықтығы", "ar": "سطوع SDR"},
    "display.gaming_perf": {"en": "GAMING & PERFORMANCE", "ru": "ПРОИЗВОДИТЕЛЬНОСТЬ И ИГРЫ", "es": "JUEGOS Y RENDIMIENTO", "de": "GAMING & LEISTUNG", "fr": "JEUX ET PERFORMANCES", "zh_CN": "游戏与高性能", "ja": "ゲームとパフォーマンス", "it": "GIOCHI E PRESTAZIONI", "pt_BR": "JOGOS E DESEMPENHO", "tr": "OYUN VE PERFORMANS", "uk": "ПРОДУКТИВНІСТЬ ТА ІГРИ", "kk": "ӨНІМДІЛІК ЖӘНЕ ОЙЫНДАР", "ar": "الألعاب والأداء"},
    "display.vrr": {"en": "Variable Refresh Rate", "ru": "Адаптивная частота (VRR)", "es": "Frecuencia de actualización variable", "de": "Variable Bildwiederholrate (VRR)", "fr": "Fréquence variable (VRR)", "zh_CN": "可变刷新率 (VRR)", "ja": "可変リフレッシュレート (VRR)", "it": "Frequenza di aggiornamento variabile", "pt_BR": "Taxa de Atualização Variável", "tr": "Değişken Yenileme Hızı", "uk": "Адаптивна частота (VRR)", "kk": "Бейімделгіш жаңарту жиілігі (VRR)", "ar": "معدل تحديث متغير"},
    "display.vrr_off": {"en": "Off", "ru": "Выкл", "es": "Desactivado", "de": "Aus", "fr": "Désactivé", "zh_CN": "关闭", "ja": "オフ", "it": "Disattivato", "pt_BR": "Desativado", "tr": "Kapalı", "uk": "Вимк", "kk": "Өшіру", "ar": "إيقاف"},
    "display.vrr_always": {"en": "Always", "ru": "Всегда", "es": "Siempre", "de": "Immer", "fr": "Toujours", "zh_CN": "始终启用", "ja": "常に", "it": "Sempre", "pt_BR": "Sempre", "tr": "Her Zaman", "uk": "Завжди", "kk": "Әрқашан", "ar": "دائمًا"},
    "display.vrr_fullscreen": {"en": "Fullscreen Only", "ru": "Только в полноэкранном режиме", "es": "Solo en pantalla completa", "de": "Nur im Vollbildmodus", "fr": "Plein écran uniquement", "zh_CN": "仅全屏模式", "ja": "全画面のみ", "it": "Solo a schermo intero", "pt_BR": "Apenas em Tela Cheia", "tr": "Yalnızca Tam Ekran", "uk": "Лише в повноекранному режимі", "kk": "Тек толық экранда", "ar": "ملء الشاشة فقط"},
    "display.vsync": {"en": "V-Sync / TearFree", "ru": "Вертикальная синхронизация (V-Sync)", "es": "V-Sync / Sin parpadeo", "de": "V-Sync / Ruckelfrei", "fr": "V-Sync / Anti-déchirement", "zh_CN": "垂直同步 / 防撕裂", "ja": "垂直同期 / V-Sync", "it": "V-Sync / TearFree", "pt_BR": "V-Sync / Sem Rasgos", "tr": "Dikey Senkronizasyon (V-Sync)", "uk": "Вертикальна синхронізація (V-Sync)", "kk": "Тік синхрондау (V-Sync)", "ar": "المزامنة الرأسية V-Sync"},
    "display.response_time": {"en": "Response Time", "ru": "Время отклика", "es": "Tiempo de respuesta", "de": "Reaktionszeit", "fr": "Temps de réponse", "zh_CN": "响应时间", "ja": "応答時間", "it": "Tempo di risposta", "pt_BR": "Tempo de Resposta", "tr": "Tepki Süresi", "uk": "Час відгуку", "kk": "Жауап беру уақыты", "ar": "زمن الاستجابة"},
    "display.resp_normal": {"en": "Normal", "ru": "Обычное", "es": "Normal", "de": "Normal", "fr": "Normal", "zh_CN": "标准", "ja": "標準", "it": "Normale", "pt_BR": "Normal", "tr": "Normal", "uk": "Звичайний", "kk": "Қалыпты", "ar": "عادي"},
    "display.resp_fast": {"en": "Fast", "ru": "Быстрое", "es": "Rápido", "de": "Schnell", "fr": "Rapide", "zh_CN": "快速", "ja": "高速", "it": "Veloce", "pt_BR": "Rápido", "tr": "Hızlı", "uk": "Швидкий", "kk": "Жылдам", "ar": "سريع"},
    "display.resp_faster": {"en": "Faster", "ru": "Максимальное", "es": "Muy rápido", "de": "Sehr schnell", "fr": "Très rapide", "zh_CN": "极速", "ja": "最高速", "it": "Molto veloce", "pt_BR": "Muito Rápido", "tr": "Çok Hızlı", "uk": "Максимальний", "kk": "Ең жылдам", "ar": "أسرع"},
    "display.protection": {"en": "DISPLAY PROTECTION", "ru": "ЗАЩИТА ЗРЕНИЯ И ЭКРАНА", "es": "PROTECCIÓN DE PANTALLA", "de": "BILDSCHIRMSCHUTZ", "fr": "PROTECTION DE L'ÉCRAN", "zh_CN": "护眼与屏幕保护", "ja": "ディスプレイ保護", "it": "PROTEZIONE SCHERMO", "pt_BR": "PROTEÇÃO DE TELA", "tr": "EKRAN KORUMASI", "uk": "ЗАХИСТ ЗОРУ ТА ЕКРАНА", "kk": "КӨЗДІ ЖӘНЕ ЭКРАНДЫ ҚОРҒАУ", "ar": "حماية الشاشة"},
    "display.night_shift": {"en": "Night Shift", "ru": "Ночной режим (Night Shift)", "es": "Modo Noche", "de": "Nachtmodus (Night Shift)", "fr": "Night Shift", "zh_CN": "夜览 (Night Shift)", "ja": "Night Shift", "it": "Night Shift", "pt_BR": "Night Shift", "tr": "Gece Işığı", "uk": "Нічний режим (Night Shift)", "kk": "Түнгі режим (Night Shift)", "ar": "الإضاءة الليلية"},
    "display.schedule": {"en": "Schedule", "ru": "Расписание", "es": "Horario", "de": "Zeitplan", "fr": "Programme", "zh_CN": "定时计划", "ja": "スケジュール", "it": "Programmazione", "pt_BR": "Agendamento", "tr": "Zamanlama", "uk": "Розклад", "kk": "Кесте", "ar": "الجدول الزمني"},
    "display.dim_sleep": {"en": "Screen Dim / Sleep", "ru": "Затемнение и выключение экрана", "es": "Atenuación / Suspensión", "de": "Abdunkeln / Ruhezustand", "fr": "Atténuation et veille", "zh_CN": "屏幕变暗与关闭", "ja": "画面の減光 / スリープ", "it": "Attenuazione / Sospensione", "pt_BR": "Esmaecer / Suspender Tela", "tr": "Ekran Karartma / Uyku", "uk": "Затемнення та вимкнення екрана", "kk": "Экранды күңгірттеу және өшіру", "ar": "تعتيم / سكون الشاشة"},
    "display.subtitle": {"en": "Manage your connected displays, resolution, refresh rate and color settings.", "ru": "Управление подключенными дисплеями, разрешением, частотой обновления и параметрами отображения.", "es": "Administra las pantallas conectadas, resolución, frecuencia de actualización y color.", "de": "Verwalten Sie Ihre angeschlossenen Displays, Auflösung, Bildwiederholrate und Farbe.", "fr": "Gérez vos écrans connectés, la résolution, la fréquence et les couleurs.", "zh_CN": "管理已连接的显示器、分辨率、刷新率与色彩设置。", "ja": "接続されたディスプレイ、解像度、リフレッシュレート、カラー設定を管理します。", "it": "Gestisci schermi collegati, risoluzione, frequenza di aggiornamento e colori.", "pt_BR": "Gerencie seus monitores conectados, resolução, taxa de atualização e cores.", "tr": "Bağlı ekranlarınızı, çözünürlüğü, yenileme hızını ve renk ayarlarını yönetin.", "uk": "Керування підключеними дисплеями, роздільною здатністю, частотою оновлення та кольором.", "kk": "Қосылған дисплейлерді, ажыратымдылықты, жаңарту жиілігін және түс параметрлерін басқару.", "ar": "إدارة شاشات العرض المتصلة والدقة ومعدل التحديث وإعدادات الألوان."},
    "display.primary_badge": {"en": "Primary", "ru": "Основной", "es": "Principal", "de": "Primär", "fr": "Principal", "zh_CN": "主显示器", "ja": "メイン", "it": "Principale", "pt_BR": "Principal", "tr": "Birincil", "uk": "Головний", "kk": "Негізгі", "ar": "الرئيسي"},
    "display.hdr_status": {"en": "HDR", "ru": "HDR", "es": "HDR", "de": "HDR", "fr": "HDR", "zh_CN": "HDR", "ja": "HDR", "it": "HDR", "pt_BR": "HDR", "tr": "HDR", "uk": "HDR", "kk": "HDR", "ar": "HDR"},
    "display.sdr_status": {"en": "SDR", "ru": "SDR", "es": "SDR", "de": "SDR", "fr": "SDR", "zh_CN": "SDR", "ja": "SDR", "it": "SDR", "pt_BR": "SDR", "tr": "SDR", "uk": "SDR", "kk": "SDR", "ar": "SDR"},

    # ── Mouse Page ──
    "mouse.primary_mouse_btn": {"en": "Primary Mouse Button", "ru": "Основная кнопка мыши", "es": "Botón principal del ratón", "de": "Primäre Maustaste", "fr": "Bouton principal de la souris", "zh_CN": "主要鼠标按键", "ja": "主マウスボタン", "it": "Pulsante principale del mouse", "pt_BR": "Botão Primário do Mouse", "tr": "Birincil Fare Düğmesi", "uk": "Основна кнопка миші", "kk": "Тінтуірдің негізгі батырмасы", "ar": "زر الماوس الأساسي"},
    "mouse.slow": {"en": "Slow", "ru": "Медленно", "es": "Lento", "de": "Langsam", "fr": "Lent", "zh_CN": "慢", "ja": "遅い", "it": "Lento", "pt_BR": "Lento", "tr": "Yavaş", "uk": "Повільно", "kk": "Баяу", "ar": "بطيء"},
    "mouse.fast": {"en": "Fast", "ru": "Быстро", "es": "Rápido", "de": "Schnell", "fr": "Rapide", "zh_CN": "快", "ja": "速い", "it": "Veloce", "pt_BR": "Rápido", "tr": "Hızlı", "uk": "Швидко", "kk": "Жылдам", "ar": "سريع"},
    "mouse.tracking_speed": {"en": "Tracking Speed", "ru": "Скорость перемещения", "es": "Velocidad del cursor", "de": "Zeigergeschwindigkeit", "fr": "Vitesse du curseur", "zh_CN": "跟踪速度", "ja": "軌跡の速さ", "it": "Velocità tracciamento", "pt_BR": "Velocidade do Cursor", "tr": "İzleme Hızı", "uk": "Швидкість переміщення", "kk": "Жылжу жылдамдығы", "ar": "سرعة التتبع"},
    "mouse.scrolling": {"en": "SCROLLING", "ru": "ПРОКРУТКА", "es": "DESPLAZAMIENTO", "de": "SCROLLEN", "fr": "DÉFILEMENT", "zh_CN": "滚动行为", "ja": "スクロール", "it": "SCORRIMENTO", "pt_BR": "ROLAGEM", "tr": "KAYDIRMA", "uk": "ПРОКРУТКА", "kk": "АЙНАЛДЫРУ", "ar": "التمرير"},
    "mouse.double_click_speed": {"en": "DOUBLE-CLICK SPEED", "ru": "СКОРОСТЬ ДВОЙНОГО ЩЕЛЧКА", "es": "VELOCIDAD DE DOBLE CLIC", "de": "DOPPELKLICK-GESCHWINDIGKEIT", "fr": "VITESSE DU DOUBLE-CLIC", "zh_CN": "连击与双击速度", "ja": "ダブルクリックの間隔", "it": "VELOCITÀ DOPPIO CLIC", "pt_BR": "VELOCIDADE DO CLIQUE DUPLO", "tr": "ÇİFT TIKLAMA HIZI", "uk": "ШВИДКІСТЬ ПОДВІЙНОГО КЛАЦАННЯ", "kk": "ҚОС ШЕРТУ ЖЫЛДАМДЫҒЫ", "ar": "سرعة النقر المزدوج"},
    "mouse.test_double_click": {"en": "Test Double-Click", "ru": "Проверка двойного клика", "es": "Probar doble clic", "de": "Doppelklick testen", "fr": "Tester le double-clic", "zh_CN": "测试双击", "ja": "ダブルクリックをテスト", "it": "Verifica doppio clic", "pt_BR": "Testar Clique Duplo", "tr": "Çift Tıklamayı Sına", "uk": "Перевірка подвійного кліку", "kk": "Қос шертуді тексеру", "ar": "اختبار النقر المزدوج"},
    "mouse.test_click": {"en": "Double-Click Here", "ru": "Нажмите дважды здесь", "es": "Doble clic aquí", "de": "Hier doppelklicken", "fr": "Double-cliquez ici", "zh_CN": "在此处双击测试", "ja": "ここをダブルクリック", "it": "Fai doppio clic qui", "pt_BR": "Clique duas vezes aqui", "tr": "Buraya Çift Tıklayın", "uk": "Натисніть двічі тут", "kk": "Осында екі рет басыңыз", "ar": "انقر نقرًا مزدوجًا هنا"},
    "mouse.test_recognized": {"en": "✓ Recognized!", "ru": "✓ Распознано!", "es": "¡✓ Reconocido!", "de": "✓ Erkannt!", "fr": "✓ Reconnu !", "zh_CN": "✓ 识别成功！", "ja": "✓ 認識完了！", "it": "✓ Riconosciuto!", "pt_BR": "✓ Reconhecido!", "tr": "✓ Algılandı!", "uk": "✓ Розпізнано!", "kk": "✓ Танылды!", "ar": "✓ تم التعرف!"},
    "mouse.acceleration": {"en": "Pointer Acceleration", "ru": "Ускорение указателя мыши", "es": "Aceleración del puntero", "de": "Zeigerbeschleunigung", "fr": "Accélération du curseur", "zh_CN": "指针加速", "ja": "ポインタの加速", "it": "Accelerazione puntatore", "pt_BR": "Aceleração do Ponteiro", "tr": "İşaretçi Hızlandırması", "uk": "Прискорення вказівника", "kk": "Көрсеткішті жылдамдату", "ar": "تسريع المؤشر"},

    # ── Keyboard Page ──
    "keyboard.caps_lock": {"en": "Caps Lock", "ru": "Caps Lock", "es": "Bloq Mayús", "de": "Feststelltaste", "fr": "Verr Maj", "zh_CN": "大写锁定 (Caps Lock)", "ja": "Caps Lock", "it": "Bloc Maiusc", "pt_BR": "Caps Lock", "tr": "Caps Lock", "uk": "Caps Lock", "kk": "Caps Lock", "ar": "قفل الأحرف الكبيرة"},
    "keyboard.num_lock": {"en": "Num Lock", "ru": "Num Lock", "es": "Bloq Num", "de": "Num-Taste", "fr": "Verr Num", "zh_CN": "数字锁定 (Num Lock)", "ja": "Num Lock", "it": "Bloc Num", "pt_BR": "Num Lock", "tr": "Num Lock", "uk": "Num Lock", "kk": "Num Lock", "ar": "قفل الأرقام"},
    "keyboard.scroll_lock": {"en": "Scroll Lock", "ru": "Scroll Lock", "es": "Bloq Despl", "de": "Rollen-Taste", "fr": "Arrêt défil", "zh_CN": "滚动锁定 (Scroll Lock)", "ja": "Scroll Lock", "it": "Bloc Scorr", "pt_BR": "Scroll Lock", "tr": "Scroll Lock", "uk": "Scroll Lock", "kk": "Scroll Lock", "ar": "قفل التمرير"},
    "keyboard.enabled": {"en": "Enabled", "ru": "Включено", "es": "Activado", "de": "Aktiviert", "fr": "Activé", "zh_CN": "已开启", "ja": "有効", "it": "Abilitato", "pt_BR": "Ativado", "tr": "Etkin", "uk": "Увімкнено", "kk": "Қосулы", "ar": "مفعل"},
    "keyboard.disabled": {"en": "Disabled", "ru": "Выключено", "es": "Desactivado", "de": "Deaktiviert", "fr": "Désactivé", "zh_CN": "已关闭", "ja": "無効", "it": "Disabilitato", "pt_BR": "Desativado", "tr": "Devre Dışı", "uk": "Вимкнено", "kk": "Өшірулі", "ar": "معطل"},
    "keyboard.status_sec": {"en": "KEYBOARD STATUS", "ru": "СОСТОЯНИЕ КЛАВИАТУРЫ", "es": "ESTADO DEL TECLADO", "de": "TASTATURSTATUS", "fr": "ÉTAT DU CLAVIER", "zh_CN": "键盘状态", "ja": "キーボードの状態", "it": "STATO TASTIERA", "pt_BR": "STATUS DO TECLADO", "tr": "KLAVYE DURUMU", "uk": "СТАН КЛАВІАТУРИ", "kk": "ПЕРНЕТАҚТА КҮЙІ", "ar": "حالة لوحة المفاتيح"},
    "keyboard.typing_options": {"en": "TYPING OPTIONS", "ru": "ПАРАМЕТРЫ ВВОДА ТЕКСТА", "es": "OPCIONES DE ESCRITURA", "de": "EINGABEOPTIONEN", "fr": "OPTIONS DE SAISIE", "zh_CN": "输入选项", "ja": "入力オプション", "it": "OPZIONI DI DIGITAZIONE", "pt_BR": "OPÇÕES DE DIGITAÇÃO", "tr": "YAZMA SEÇENEKLERİ", "uk": "ПАРАМЕТРИ ВВЕДЕННЯ ТЕКСТУ", "kk": "МӘТІН ЕНГІЗУ ПАРАМЕТРЛЕРІ", "ar": "خيارات الكتابة"},
    "keyboard.cursor_blink": {"en": "Cursor Blinking", "ru": "Мигание курсора", "es": "Parpadeo del cursor", "de": "Blinkender Cursor", "fr": "Clignotement du curseur", "zh_CN": "光标闪烁", "ja": "カーソルの点滅", "it": "Lampeggio del cursore", "pt_BR": "Piscar de Cursor", "tr": "İmleç Yanıp Sönmesi", "uk": "Блимання курсора", "kk": "Меңзердің жыпылықтауы", "ar": "وميض المؤشر"},
    "keyboard.dwt": {"en": "Disable Touchpad While Typing", "ru": "Блокировать тачпад при вводе текста", "es": "Desactivar panel táctil al escribir", "de": "Touchpad beim Tippen sperren", "fr": "Désactiver le pavé tactile lors de la frappe", "zh_CN": "打字时禁用触控板", "ja": "タイピング時にタッチパッドを無効化", "it": "Disabilita touchpad durante la digitazione", "pt_BR": "Desativar Touchpad ao Digitar", "tr": "Yazarken Dokunmatik Yüzeyi Devre Dışı Bırak", "uk": "Блокувати тачпад під час введення", "kk": "Мәтін енгізу кезінде тачпадты өшіру", "ar": "تعطيل لوحة اللمس أثناء الكتابة"},
    "keyboard.sticky_keys": {"en": "Sticky Keys", "ru": "Залипание клавиш", "es": "Teclas especiales", "de": "Eintrastende Tasten", "fr": "Touches rémanentes", "zh_CN": "粘滞键", "ja": "固定キー", "it": "Tasti permanenti", "pt_BR": "Teclas de Aderência", "tr": "Yapışkan Tuşlar", "uk": "Залипання клавіш", "kk": "Пернелердің жабысуы", "ar": "ثبات المفاتيح"},
    "keyboard.typing_sec": {"en": "TYPING & SPEED", "ru": "СКОРОСТЬ И АВТОПОВТОР", "es": "VELOCIDAD DE ESCRITURA", "de": "TIPPEN & WIEDERHOLUNG", "fr": "VITESSE ET RÉPÉTITION", "zh_CN": "按键响应速度", "ja": "キーリピート設定", "it": "DIGITAZIONE E VELOCITÀ", "pt_BR": "DIGITAÇÃO E REPETIÇÃO", "tr": "YAZMA VE YİNELEME", "uk": "ШВИДКІСТЬ ТА АВТОПОВТОР", "kk": "ЖЫЛДАМДЫҚ ПЕН ҚАЙТАЛАУ", "ar": "الكتابة والتكرار"},
    "keyboard.long": {"en": "Long", "ru": "Длинная", "es": "Largo", "de": "Lang", "fr": "Long", "zh_CN": "长", "ja": "長め", "it": "Lungo", "pt_BR": "Longo", "tr": "Uzun", "uk": "Довга", "kk": "Ұзақ", "ar": "طويل"},
    "keyboard.short": {"en": "Short", "ru": "Короткая", "es": "Corto", "de": "Kurz", "fr": "Court", "zh_CN": "短", "ja": "短め", "it": "Corto", "pt_BR": "Curto", "tr": "Kısa", "uk": "Коротка", "kk": "Қысқа", "ar": "قصير"},
    "keyboard.slow": {"en": "Slow", "ru": "Медленно", "es": "Lento", "de": "Langsam", "fr": "Lent", "zh_CN": "慢", "ja": "遅い", "it": "Lento", "pt_BR": "Lento", "tr": "Yavaş", "uk": "Повільно", "kk": "Баяу", "ar": "بطيء"},
    "keyboard.fast": {"en": "Fast", "ru": "Быстро", "es": "Rápido", "de": "Schnell", "fr": "Rapide", "zh_CN": "快", "ja": "速い", "it": "Veloce", "pt_BR": "Rápido", "tr": "Hızlı", "uk": "Швидко", "kk": "Жылдам", "ar": "سريع"},
    "keyboard.input_sources": {"en": "INPUT SOURCES", "ru": "РАСКЛАДКИ И ИСТОЧНИКИ ВВОДА", "es": "FUENTES DE ENTRADA", "de": "EINGABEQUELEN", "fr": "SOURCES D'ENTRÉE", "zh_CN": "输入源与输入法", "ja": "入力ソース", "it": "SORGENTI DI INPUT", "pt_BR": "FONTES DE ENTRADA", "tr": "GİRİŞ KAYNAKLARI", "uk": "ДЖЕРЕЛА ВВЕДЕННЯ", "kk": "ЕНГІЗУ КӨЗДЕРІ", "ar": "مصادر الإدخال"},

    # ── Echo Search Page ──
    "search.hero_desc": {"en": "Instant search for applications, files, and actions", "ru": "Мгновенный поиск приложений, файлов и действий", "es": "Búsqueda instantánea de aplicaciones, archivos y acciones", "de": "Sofortige Suche nach Programmen, Dateien und Aktionen", "fr": "Recherche instantanée d'applications, fichiers et actions", "zh_CN": "快速搜索应用程序、文件及系统操作", "ja": "アプリ、ファイル、アクションを瞬時に検索", "it": "Ricerca istantanea di app, file e azioni", "pt_BR": "Busca instantânea de aplicativos, arquivos e ações", "tr": "Uygulamalar, dosyalar ve eylemler için anında arama", "uk": "Миттєвий пошук програм, файлів та дій", "kk": "Қолданбаларды, файлдарды және әрекеттерді лезде іздеу", "ar": "بحث فوري عن التطبيقات والملفات والإجراءات"},
    "search.status_ready": {"en": "Ready", "ru": "Готово к работе", "es": "Listo", "de": "Bereit", "fr": "Prêt", "zh_CN": "就绪", "ja": "準備完了", "it": "Pronto", "pt_BR": "Pronto", "tr": "Hazır", "uk": "Готово", "kk": "Дайын", "ar": "جاهز"},
    "search.sources_count": {"en": "Sources", "ru": "источников", "es": "Fuentes", "de": "Quellen", "fr": "Sources", "zh_CN": "项来源", "ja": "ソース", "it": "Sorgenti", "pt_BR": "Fontes", "tr": "Kaynak", "uk": "джерел", "kk": "көздер", "ar": "مصادر"},
    "search.open_btn": {"en": "Open Search", "ru": "Открыть Поиск", "es": "Abrir Búsqueda", "de": "Suche öffnen", "fr": "Ouvrir Recherche", "zh_CN": "启动搜索", "ja": "検索を開く", "it": "Apri Ricerca", "pt_BR": "Abrir Busca", "tr": "Aramayı Aç", "uk": "Відкрити Пошук", "kk": "Іздеуді ашу", "ar": "فتح البحث"},
    "search.sec_general": {"en": "GENERAL", "ru": "ОСНОВНЫЕ ПАРАМЕТРЫ", "es": "GENERAL", "de": "ALLGEMEIN", "fr": "GÉNÉRAL", "zh_CN": "常规偏好设置", "ja": "一般", "it": "GENERALE", "pt_BR": "GERAL", "tr": "GENEL", "uk": "ОСНОВНІ ПАРАМЕТРИ", "kk": "НЕГІЗГІ ПАРАМЕТРЛЕР", "ar": "عام"},
    "search.launch_login": {"en": "Launch at Login", "ru": "Запуск при входе в систему", "es": "Iniciar al iniciar sesión", "de": "Beim Anmelden starten", "fr": "Lancer à l'ouverture de session", "zh_CN": "开机登录时自动启动", "ja": "ログイン時に起動", "it": "Avvia all'accesso", "pt_BR": "Iniciar na Sessão", "tr": "Girişte Başlat", "uk": "Запуск під час входу в систему", "kk": "Жүйеге кіргенде іске қосу", "ar": "التشغيل عند تسجيل الدخول"},
    "search.launch_shortcut": {"en": "Launch Shortcut", "ru": "Сочетание клавиш запуска", "es": "Atajo de activación", "de": "Tastenkürzel zum Starten", "fr": "Raccourci de lancement", "zh_CN": "快速呼出快捷键", "ja": "起動ショートカット", "it": "Scorciatoia di avvio", "pt_BR": "Atalho de Inicialização", "tr": "Başlatma Kısayolu", "uk": "Сполучення клавіш запуску", "kk": "Іске қосу пернелер тіркесімі", "ar": "اختصار التشغيل"},
    "search.history": {"en": "Search History", "ru": "История поиска", "es": "Historial de búsqueda", "de": "Suchverlauf", "fr": "Historique de recherche", "zh_CN": "记录搜索历史", "ja": "検索履歴", "it": "Cronologia ricerche", "pt_BR": "Histórico de Busca", "tr": "Arama Geçmişi", "uk": "Історія пошуку", "kk": "Іздеу тарихы", "ar": "سجل البحث"},
    "search.recent_empty": {"en": "Show Recent when Empty", "ru": "Показывать недавние элементы", "es": "Mostrar recientes si está vacío", "de": "Zuletzt verwendete anzeigen", "fr": "Afficher les récents si vide", "zh_CN": "空输入时展示最近打开项", "ja": "未入力時に最近の項目を表示", "it": "Mostra recenti quando vuoto", "pt_BR": "Mostrar Recentes Quando Vazio", "tr": "Boşken Son Öğeleri Göster", "uk": "Показувати нещодавні елементи", "kk": "Бос кезде соңғы элементтерді көрсету", "ar": "إظهار العناصر الأخيرة عندما تكون فارغة"},
    "search.sec_search": {"en": "SEARCH LIMITS", "ru": "ПАРАМЕТРЫ ВЫДАЧИ", "es": "LÍMITES DE BÚSQUEDA", "de": "SUCHGRENZEN", "fr": "LIMITES DE RECHERCHE", "zh_CN": "搜索结果呈现", "ja": "検索結果の制限", "it": "LIMITI RICERCA", "pt_BR": "LIMITES DE BUSCA", "tr": "ARAMA SINIRLARI", "uk": "ПАРАМЕТРИ ВИДАЧІ", "kk": "НӘТИЖЕЛЕР ШЕКТЕУІ", "ar": "حدود البحث"},
    "search.results_limit": {"en": "Results Limit", "ru": "Количество результатов", "es": "Límite de resultados", "de": "Ergebnislimit", "fr": "Nombre de résultats", "zh_CN": "最大结果显示数量", "ja": "最大検索結果数", "it": "Limite risultati", "pt_BR": "Limite de Resultados", "tr": "Sonuç Sınırı", "uk": "Кількість результатів", "kk": "Нәтижелер саны", "ar": "حد النتائج"},
    "search.sec_appearance": {"en": "APPEARANCE", "ru": "ОФОРМЛЕНИЕ", "es": "APARIENCIA", "de": "ERSCHEINUNGSBILD", "fr": "APPARENCE", "zh_CN": "界面外观", "ja": "外観", "it": "ASPETTO", "pt_BR": "APARÊNCIA", "tr": "GÖRÜNÜM", "uk": "ОФОРМЛЕННЯ", "kk": "СЫРТҚЫ ТҮРІ", "ar": "المظهر"},
    "search.theme": {"en": "Theme", "ru": "Тема оформления", "es": "Tema", "de": "Design", "fr": "Thème", "zh_CN": "主题风格", "ja": "テーマ", "it": "Tema", "pt_BR": "Tema", "tr": "Tema", "uk": "Тема оформлення", "kk": "Дизайн тақырыбы", "ar": "السمة"},
    "search.transparency": {"en": "Transparency", "ru": "Прозрачность окна", "es": "Transparencia", "de": "Transparenz", "fr": "Transparence", "zh_CN": "窗口背景透明度", "ja": "透明度", "it": "Trasparenza", "pt_BR": "Transparência", "tr": "Saydamlık", "uk": "Прозорість вікна", "kk": "Терезе мөлдірлігі", "ar": "الشفافية"},
    "search.animations": {"en": "Animations", "ru": "Анимации интерфейса", "es": "Animaciones", "de": "Animationen", "fr": "Animations", "zh_CN": "流畅过渡动画", "ja": "アニメーション", "it": "Animazioni", "pt_BR": "Animações", "tr": "Animasyonlar", "uk": "Анімації інтерфейсу", "kk": "Интерфейс анимациялары", "ar": "الرسوم المتحركة"},
    "search.sec_preview": {"en": "PREVIEW PANEL", "ru": "ПАНЕЛЬ ПРЕДПРОСМОТРА", "es": "PANEL DE VISTA PREVIA", "de": "VORSCHAU-PANEL", "fr": "PANNEAU D'APERÇU", "zh_CN": "预览面板", "ja": "プレビューパネル", "it": "PANNELLO DI ANTEPRIMA", "pt_BR": "PAINEL DE PRÉ-VISUALIZAÇÃO", "tr": "ÖNİZLEME PANELİ", "uk": "ПАНЕЛЬ ПЕРЕДПРОГЛЯДУ", "kk": "АЛДЫН АЛА ҚАРАУ ТАҚТАСЫ", "ar": "لوحة المعاينة"},
    "search.preview_panel": {"en": "Preview Panel", "ru": "Панель быстрого просмотра", "es": "Panel de vista previa", "de": "Vorschaufenster", "fr": "Panneau d'aperçu", "zh_CN": "启用右侧快速预览", "ja": "プレビューパネル", "it": "Pannello di anteprima", "pt_BR": "Painel de Pré-visualização", "tr": "Önizleme Paneli", "uk": "Панель швидкого перегляду", "kk": "Жылдам қарау тақтасы", "ar": "لوحة المعاينة"},
    "search.preview_width": {"en": "Preview Width", "ru": "Ширина предпросмотра", "es": "Ancho de vista previa", "de": "Vorschaubreite", "fr": "Largeur de l'aperçu", "zh_CN": "预览区域宽度", "ja": "プレビュー幅", "it": "Larghezza anteprima", "pt_BR": "Largura da Pré-visualização", "tr": "Önizleme Genişliği", "uk": "Ширина передперегляду", "kk": "Алдын ала қарау ені", "ar": "عرض المعاينة"},
    "search.sec_modes": {"en": "SEARCH CATEGORIES", "ru": "КАТЕГОРИИ ПОИСКА", "es": "CATEGORÍAS DE BÚSQUEDA", "de": "SUCHKATEGORIEN", "fr": "CATÉGORIES DE RECHERCHE", "zh_CN": "启用搜索源", "ja": "検索カテゴリ", "it": "CATEGORIE DI RICERCA", "pt_BR": "CATEGORIAS DE BUSCA", "tr": "ARAMA KATEGORİLERİ", "uk": "КАТЕГОРІЇ ПОШУКУ", "kk": "ІЗДЕУ САНАТТАРЫ", "ar": "فئات البحث"},
    "search.mode_apps": {"en": "Applications", "ru": "Приложения", "es": "Aplicaciones", "de": "Programme", "fr": "Applications", "zh_CN": "应用程序", "ja": "アプリケーション", "it": "Applicazioni", "pt_BR": "Aplicativos", "tr": "Uygulamalar", "uk": "Програми", "kk": "Қолданбалар", "ar": "التطبيقات"},
    "search.mode_files": {"en": "Files & Documents", "ru": "Файлы и документы", "es": "Archivos y documentos", "de": "Dateien & Dokumente", "fr": "Fichiers et documents", "zh_CN": "文件与文稿", "ja": "ファイルと書類", "it": "File e documenti", "pt_BR": "Arquivos e Documentos", "tr": "Dosyalar ve Belgeler", "uk": "Файли та документи", "kk": "Файлдар мен құжаттар", "ar": "الملفات والمستندات"},
    "search.mode_clipboard": {"en": "Clipboard History", "ru": "Буфер обмена", "es": "Portapapeles", "de": "Zwischenablage", "fr": "Presse-papiers", "zh_CN": "剪贴板历史", "ja": "クリップボード履歴", "it": "Appunti", "pt_BR": "Área de Transferência", "tr": "Pano Geçmişi", "uk": "Буфер обміну", "kk": "Алмасу буфері", "ar": "سجل الحافظة"},
    "search.mode_emoji": {"en": "Symbols & Emoji", "ru": "Символы и эмодзи", "es": "Símbolos y emojis", "de": "Symbole & Emojis", "fr": "Symboles et emojis", "zh_CN": "符号与表情包", "ja": "記号と絵文字", "it": "Simboli ed emoji", "pt_BR": "Símbolos e Emojis", "tr": "Simgeler ve Emojiler", "uk": "Символи та емодзі", "kk": "Таңбалар мен эмодзи", "ar": "الرموز والرموز التعبيرية"},

    # ── Notifications Page ──
    "notifications.dnd": {"en": "Do Not Disturb", "ru": "Не беспокоить", "es": "No molestar", "de": "Nicht stören", "fr": "Ne pas déranger", "zh_CN": "勿扰模式", "ja": "おやすみモード", "it": "Non disturbare", "pt_BR": "Não Perturbe", "tr": "Rahatsız Etmeyin", "uk": "Не турбувати", "kk": "Мазаламаңыз", "ar": "عدم الإزعاج"},
    "notifications.sec_center": {"en": "NOTIFICATION CENTER", "ru": "ЦЕНТР УВЕДОМЛЕНИЙ", "es": "CENTRO DE NOTIFICACIONES", "de": "MITTEILUNGSZENTRALE", "fr": "CENTRE DE NOTIFICATIONS", "zh_CN": "通知中心", "ja": "通知センター", "it": "CENTRO NOTIFICHE", "pt_BR": "CENTRO DE NOTIFICAÇÕES", "tr": "BİLDİRİM MERKEZİ", "uk": "ЦЕНТР СПОВІЩЕНЬ", "kk": "ХАБАРЛАНДЫРУ ОРТАЛЫҒЫ", "ar": "مركز الإشعارات"},
    "notifications.lock_previews": {"en": "Show Previews on Lock Screen", "ru": "Показ на экране блокировки", "es": "Mostrar en pantalla bloqueada", "de": "Auf Sperrbildschirm anzeigen", "fr": "Afficher sur l'écran verrouillé", "zh_CN": "在锁定屏幕上显示预览", "ja": "ロック画面でプレビューを表示", "it": "Mostra su schermo bloccato", "pt_BR": "Mostrar na Tela de Bloqueio", "tr": "Kilit Ekranında Önizlemeleri Göster", "uk": "Показ на екрані блокування", "kk": "Құлыптау экранында көрсету", "ar": "إظهار المعاينات على شاشة القفل"},
    "notifications.sec_apps": {"en": "APPLICATION NOTIFICATIONS", "ru": "УВЕДОМЛЕНИЯ ПРИЛОЖЕНИЙ", "es": "NOTIFICACIONES DE APLICACIONES", "de": "APP-MITTEILUNGEN", "fr": "NOTIFICATIONS DES APPLICATIONS", "zh_CN": "应用程序通知管理", "ja": "アプリケーションの通知", "it": "NOTIFICHE DELLE APP", "pt_BR": "NOTIFICAÇÕES DE APLICATIVOS", "tr": "UYGULAMA BİLDİRİMLERİ", "uk": "СПОВІЩЕННЯ ПРОГРАМ", "kk": "ҚОЛДАНБА ХАБАРЛАНДЫРУЛАРЫ", "ar": "إشعارات التطبيقات"},
    "notifications.off": {"en": "Off", "ru": "Выключено", "es": "Desactivado", "de": "Aus", "fr": "Désactivé", "zh_CN": "已关闭", "ja": "オフ", "it": "Disattivato", "pt_BR": "Desativado", "tr": "Kapalı", "uk": "Вимкнено", "kk": "Өшірулі", "ar": "متوقف"},
    "notifications.sub_banners": {"en": "Banners", "ru": "Баннеры", "es": "Tiras", "de": "Banner", "fr": "Bannières", "zh_CN": "横幅", "ja": "バナー", "it": "Banner", "pt_BR": "Banners", "tr": "Başlıklar", "uk": "Банери", "kk": "Баннерлер", "ar": "الشعارات"},
    "notifications.sub_sounds": {"en": "Sounds", "ru": "Звуки", "es": "Sonidos", "de": "Töne", "fr": "Sons", "zh_CN": "声音", "ja": "サウンド", "it": "Suoni", "pt_BR": "Sons", "tr": "Sesler", "uk": "Звуки", "kk": "Дыбыстар", "ar": "الأصوات"},
    "notifications.sub_lock": {"en": "Lock Screen", "ru": "Экран блокировки", "es": "Pantalla bloqueada", "de": "Sperrbildschirm", "fr": "Écran verrouillé", "zh_CN": "锁定屏幕", "ja": "ロック画面", "it": "Schermo bloccato", "pt_BR": "Tela de Bloqueio", "tr": "Kilit Ekranı", "uk": "Екран блокування", "kk": "Құлыптау экраны", "ar": "شاشة القفل"},
    "notifications.sub_badges": {"en": "Badges", "ru": "Значки", "es": "Globos", "de": "Kennzeichen", "fr": "Pastilles", "zh_CN": "标记", "ja": "バッジ", "it": "Badge", "pt_BR": "Avisos", "tr": "İşaretler", "uk": "Значки", "kk": "Белгішелер", "ar": "الشارات"},
    "notifications.back": {"en": "‹ Notifications", "ru": "‹ Уведомления", "es": "‹ Notificaciones", "de": "‹ Mitteilungen", "fr": "‹ Notifications", "zh_CN": "‹ 通知", "ja": "‹ 通知", "it": "‹ Notifiche", "pt_BR": "‹ Notificações", "tr": "‹ Bildirimler", "uk": "‹ Сповіщення", "kk": "‹ Хабарландырулар", "ar": "‹ الإشعارات"},
    "notifications.allow": {"en": "Allow Notifications", "ru": "Разрешить уведомления", "es": "Permitir notificaciones", "de": "Mitteilungen erlauben", "fr": "Autoriser les notifications", "zh_CN": "允许发送通知", "ja": "通知を許可", "it": "Consenti notifiche", "pt_BR": "Permitir Notificações", "tr": "Bildirimlere İzin Ver", "uk": "Дозволити сповіщення", "kk": "Хабарландыруларға рұқсат беру", "ar": "السماح بالإشعارات"},
    "notifications.banners": {"en": "Show Banners", "ru": "Показывать всплывающие баннеры", "es": "Mostrar tiras", "de": "Banner anzeigen", "fr": "Afficher les bannières", "zh_CN": "显示屏幕横幅", "ja": "バナーを表示", "it": "Mostra banner", "pt_BR": "Mostrar Banners", "tr": "Başlıkları Göster", "uk": "Показувати спливаючі банери", "kk": "Қалқымалы баннерлерді көрсету", "ar": "إظهار الشعارات"},
    "notifications.sounds": {"en": "Play Sound Alerts", "ru": "Звуковые оповещения", "es": "Emitir alertas de sonido", "de": "Hinweistöne abspielen", "fr": "Émettre un signal sonore", "zh_CN": "播放提示声音", "ja": "通知音を鳴らす", "it": "Riproduci avvisi sonori", "pt_BR": "Tocar Alertas Sonoros", "tr": "Sesli Uyarıları Çal", "uk": "Звукові сповіщення", "kk": "Дыбыстық ескертулер", "ar": "تشغيل التنبيهات الصوتية"},
    "notifications.lock_screen": {"en": "Show on Lock Screen", "ru": "Отображать на экране блокировки", "es": "Mostrar en la pantalla bloqueada", "de": "Auf Sperrbildschirm anzeigen", "fr": "Afficher sur l'écran verrouillé", "zh_CN": "在锁定屏幕上显示", "ja": "ロック画面に表示", "it": "Mostra sullo schermo bloccato", "pt_BR": "Mostrar na Tela de Bloqueio", "tr": "Kilit Ekranında Göster", "uk": "Відображати на екрані блокування", "kk": "Құлыптау экранында көрсету", "ar": "العرض على شاشة القفل"},
    "notifications.priority": {"en": "Priority", "ru": "Приоритет", "es": "Prioridad", "de": "Priorität", "fr": "Priorité", "zh_CN": "优先级", "ja": "優先度", "it": "Priorità", "pt_BR": "Prioridade", "tr": "Öncelik", "uk": "Пріоритет", "kk": "Басымдық", "ar": "الأولوية"},
    "notifications.not_supported": {"en": "Standard (System)", "ru": "Стандартный (система)", "es": "Estándar (sistema)", "de": "Standard (System)", "fr": "Standard (système)", "zh_CN": "系统默认", "ja": "標準 (システム)", "it": "Standard (sistema)", "pt_BR": "Padrão (Sistema)", "tr": "Standart (Sistem)", "uk": "Стандартний (система)", "kk": "Стандартты (жүйе)", "ar": "قياسي (النظام)"},

    # ── Sound Page (Volume) ──
    "sound.output_volume": {"en": "Output Volume", "ru": "Громкость вывода", "es": "Volumen de salida", "de": "Ausgabelautstärke", "fr": "Volume de sortie", "zh_CN": "输出音量", "ja": "出力音量", "it": "Volume di uscita", "pt_BR": "Volume de Saída", "tr": "Çıkış Sesi", "uk": "Гучність виведення", "kk": "Шығыс дыбыс деңгейі", "ar": "مستوى صوت الإخراج"},
    "sound.test": {"en": "Test", "ru": "Проверить", "es": "Probar", "de": "Testen", "fr": "Tester", "zh_CN": "测试", "ja": "テスト", "it": "Prova", "pt_BR": "Testar", "tr": "Test Et", "uk": "Перевірити", "kk": "Тексеру", "ar": "اختبار"},
    "sound.test_speakers": {"en": "Test Speakers", "ru": "Проверка динамиков", "es": "Probar altavoces", "de": "Lautsprecher testen", "fr": "Tester les haut-parleurs", "zh_CN": "测试扬声器", "ja": "スピーカーをテスト", "it": "Prova altoparlanti", "pt_BR": "Testar Alto-falantes", "tr": "Hoparlörleri Test Et", "uk": "Перевірка динаміків", "kk": "Үндеткіштерді тексеру", "ar": "اختبار مكبرات الصوت"},
    "sound.device_info": {"en": "Output Device Info", "ru": "Сведения об аудиоустройстве", "es": "Información del dispositivo", "de": "Geräteinformationen", "fr": "Informations sur le périphérique", "zh_CN": "音频设备详情", "ja": "出力デバイスの詳細", "it": "Info dispositivo di uscita", "pt_BR": "Informações do Dispositivo", "tr": "Çıkış Cihazı Bilgisi", "uk": "Відомості про аудіопристрій", "kk": "Аудиоқұрылғы туралы мәлімет", "ar": "معلومات جهاز الإخراج"},
    "sound.input_volume": {"en": "Input Volume", "ru": "Громкость микрофона", "es": "Volumen de entrada", "de": "Eingabelautstärke", "fr": "Volume d'entrée", "zh_CN": "输入音量", "ja": "入力音量", "it": "Volume di ingresso", "pt_BR": "Volume de Entrada", "tr": "Giriş Sesi", "uk": "Гучність мікрофона", "kk": "Микрофон дыбыс деңгейі", "ar": "مستوى صوت الإدخال"},
    "sound.input_level": {"en": "Input Level", "ru": "Уровень сигнала микрофона", "es": "Nivel de entrada", "de": "Eingangspegel", "fr": "Niveau d'entrée", "zh_CN": "输入信号电平", "ja": "入力レベル", "it": "Livello di ingresso", "pt_BR": "Nível de Entrada", "tr": "Giriş Seviyesi", "uk": "Рівень сигналу мікрофона", "kk": "Микрофон сигналының деңгейі", "ar": "مستوى الإدخال"},
    "sound.stop": {"en": "Stop", "ru": "Остановить", "es": "Detener", "de": "Stoppen", "fr": "Arrêter", "zh_CN": "停止", "ja": "停止", "it": "Ferma", "pt_BR": "Parar", "tr": "Durdur", "uk": "Зупинити", "kk": "Тоқтату", "ar": "إيقاف"},
    "sound.system_sounds": {"en": "SYSTEM SOUNDS", "ru": "СИСТЕМНЫЕ ЗВУКИ", "es": "SONIDOS DEL SISTEMA", "de": "SYSTEMTÖNE", "fr": "SONS DU SYSTÈME", "zh_CN": "系统提示音", "ja": "システムサウンド", "it": "SUONI DI SISTEMA", "pt_BR": "SONS DO SISTEMA", "tr": "SİSTEM SESLERİ", "uk": "СИСТЕМНІ ЗВУКИ", "kk": "ЖҮЙЕЛІК ДЫБЫСТАР", "ar": "أصوات النظام"},
    "sound.ui_sounds": {"en": "Play User Interface Sounds", "ru": "Звуки пользовательского интерфейса", "es": "Reproducir sonidos de interfaz", "de": "Systemklänge wiedergeben", "fr": "Émettre des effets sonores d'interface", "zh_CN": "播放用户界面操作音效", "ja": "ユーザーインターフェース効果音を鳴らす", "it": "Riproduci effetti sonori di interfaccia", "pt_BR": "Tocar sons da interface do usuário", "tr": "Kullanıcı arayüzü seslerini çal", "uk": "Звуки інтерфейсу користувача", "kk": "Пайдаланушы интерфейсінің дыбыстары", "ar": "تشغيل أصوات واجهة المستخدم"},

    # ── Network Page ──
    "network.summary": {"en": "Network Summary", "ru": "Сводка о состоянии сети", "es": "Resumen de red", "de": "Netzwerkübersicht", "fr": "État du réseau", "zh_CN": "网络连接状态", "ja": "ネットワーク概要", "it": "Riepilogo rete", "pt_BR": "Resumo da Rede", "tr": "Ağ Özeti", "uk": "Зведення про стан мережі", "kk": "Желі күйінің қысқаша мәліметі", "ar": "ملخص الشبكة"},
    "network.active_conn": {"en": "Active Connection", "ru": "Активное подключение", "es": "Conexión activa", "de": "Aktive Verbindung", "fr": "Connexion active", "zh_CN": "活跃连接", "ja": "アクティブな接続", "it": "Connessione attiva", "pt_BR": "Conexão Ativa", "tr": "Etkin Bağlantı", "uk": "Активне підключення", "kk": "Белсенді қосылым", "ar": "الاتصال النشط"},
    "network.local_ip": {"en": "Local IPv4", "ru": "Локальный IPv4", "es": "IPv4 local", "de": "Lokale IPv4", "fr": "IPv4 locale", "zh_CN": "本地 IPv4 地址", "ja": "ローカル IPv4", "it": "IPv4 locale", "pt_BR": "IPv4 Local", "tr": "Yerel IPv4", "uk": "Локальний IPv4", "kk": "Жергілікті IPv4", "ar": "IPv4 المحلي"},
    "network.internet_status": {"en": "Internet Status", "ru": "Доступ в Интернет", "es": "Estado de Internet", "de": "Internetstatus", "fr": "Accès Internet", "zh_CN": "互联网连接", "ja": "インターネット接続", "it": "Stato Internet", "pt_BR": "Status da Internet", "tr": "İnternet Durumu", "uk": "Доступ до Інтернету", "kk": "Интернетке қолжетімділік", "ar": "حالة الإنترنت"},
    "network.vpn_status": {"en": "VPN Status", "ru": "Статус VPN", "es": "Estado de VPN", "de": "VPN-Status", "fr": "État du VPN", "zh_CN": "VPN 状态", "ja": "VPN ステータス", "it": "Stato VPN", "pt_BR": "Status da VPN", "tr": "VPN Durumu", "uk": "Статус VPN", "kk": "VPN күйі", "ar": "حالة VPN"},
    "network.connected": {"en": "Connected", "ru": "Подключено", "es": "Conectado", "de": "Verbunden", "fr": "Connecté", "zh_CN": "已连接", "ja": "接続済み", "it": "Connesso", "pt_BR": "Conectado", "tr": "Bağlandı", "uk": "Підключено", "kk": "Қосылған", "ar": "متصل"},
    "network.not_connected": {"en": "Not Connected", "ru": "Не подключено", "es": "No conectado", "de": "Nicht verbunden", "fr": "Non connecté", "zh_CN": "未连接", "ja": "未接続", "it": "Non connesso", "pt_BR": "Desconectado", "tr": "Bağlı Değil", "uk": "Не підключено", "kk": "Қосылмаған", "ar": "غير متصل"},
    "network.interfaces": {"en": "INTERFACES", "ru": "СЕТЕВЫЕ ИНТЕРФЕЙСЫ", "es": "INTERFACES DE RED", "de": "SCHNITTSTELLEN", "fr": "INTERFACES RÉSEAU", "zh_CN": "网络适配器与接口", "ja": "ネットワークインターフェース", "it": "INTERFACCE DI RETE", "pt_BR": "INTERFACES", "tr": "AĞ ARAYÜZLERİ", "uk": "МЕРЕЖЕВІ ІНТЕРФЕЙСИ", "kk": "ЖЕЛІЛІК ИНТЕРФЕЙСТЕР", "ar": "واجهات الشبكة"},
    "network.no_connection": {"en": "No Network Connection", "ru": "Нет подключения к сети", "es": "Sin conexión de red", "de": "Keine Netzwerkverbindung", "fr": "Aucune connexion réseau", "zh_CN": "无网络连接", "ja": "ネットワーク接続なし", "it": "Nessuna connessione di rete", "pt_BR": "Sem Conexão de Rede", "tr": "Ağ Bağlantısı Yok", "uk": "Немає підключення до мережі", "kk": "Желілік қосылым жоқ", "ar": "لا يوجد اتصال بالشبكة"},
    "network.no_conn_desc": {"en": "Connect to Wi-Fi or Ethernet to access the Internet.", "ru": "Подключитесь к Wi-Fi или Ethernet-кабелю для доступа в Интернет.", "es": "Conéctese a Wi-Fi o Ethernet para acceder a Internet.", "de": "Verbinden Sie sich mit WLAN oder Ethernet, um auf das Internet zuzugreifen.", "fr": "Connectez-vous au Wi-Fi ou à Ethernet pour accéder à Internet.", "zh_CN": "连接无线局域网或插入以太网网线以访问互联网。", "ja": "インターネットにアクセスするには、Wi-Fi または有線 LAN に接続してください。", "it": "Connettiti al Wi-Fi o via cavo Ethernet per accedere a Internet.", "pt_BR": "Conecte-se ao Wi-Fi ou Ethernet para acessar a Internet.", "tr": "İnternete erişmek için Wi-Fi veya Ethernet'e bağlanın.", "uk": "Підключіться до Wi-Fi або Ethernet-кабелю для доступу в Інтернет.", "kk": "Интернетке кіру үшін Wi-Fi немесе Ethernet кабеліне қосылыңыз.", "ar": "اتصل بشبكة Wi-Fi أو كابل Ethernet للوصول إلى الإنترنت."},
    "privacy.title": {
        "en": "Privacy & Security", "ru": "Конфиденциальность", "es": "Privacidad y seguridad", "de": "Datenschutz & Sicherheit",
        "fr": "Confidentialité et sécurité", "zh_CN": "隐私与安全性", "ja": "プライバシーとセキュリティ", "it": "Privacy e sicurezza",
        "pt_BR": "Privacidade e Segurança", "tr": "Gizlilik ve Güvenlik", "uk": "Конфіденційність і безпека", "kk": "Құпиялылық және қауіпсіздік", "ar": "الخصوصية والأمان"
    },
    "privacy.hero_active": {
        "en": "Services Active", "ru": "служб активно", "es": "Servicios activos", "de": "Dienste aktiv",
        "fr": "Services actifs", "zh_CN": "项服务已启用", "ja": "個のサービスが有効", "it": "Servizi attivi",
        "pt_BR": "Serviços Ativos", "tr": "Hizmet Etkin", "uk": "служб активно", "kk": "қызмет белсенді", "ar": "خدمات نشطة"
    },
    "privacy.status_protected": {
        "en": "Protected", "ru": "Защищено", "es": "Protegido", "de": "Geschützt",
        "fr": "Protégé", "zh_CN": "受保护", "ja": "保護されています", "it": "Protetto",
        "pt_BR": "Protegido", "tr": "Korumalı", "uk": "Захищено", "kk": "Қорғалған", "ar": "محمي"
    },
    "privacy.status_standard": {
        "en": "Standard Protection", "ru": "Стандартная защита", "es": "Protección estándar", "de": "Standardschutz",
        "fr": "Protection standard", "zh_CN": "标准保护", "ja": "標準保護", "it": "Protezione standard",
        "pt_BR": "Proteção Padrão", "tr": "Standart Koruma", "uk": "Стандартний захист", "kk": "Стандартты қорғау", "ar": "حماية قياسية"
    },
    "privacy.sec_system": {
        "en": "SYSTEM", "ru": "СИСТЕМА", "es": "SISTEMA", "de": "SYSTEM",
        "fr": "SYSTÈME", "zh_CN": "系统隐私", "ja": "システム", "it": "SISTEMA",
        "pt_BR": "SISTEMA", "tr": "SİSTEM", "uk": "СИСТЕМА", "kk": "ЖҮЙЕ", "ar": "النظام"
    },
    "privacy.sec_devices": {
        "en": "DEVICES", "ru": "УСТРОЙСТВА", "es": "DISPOSITIVOS", "de": "GERÄTE",
        "fr": "APPAREILS", "zh_CN": "硬件设备", "ja": "デバイス", "it": "DISPOSITIVI",
        "pt_BR": "DISPOSITIVOS", "tr": "CİHAZLAR", "uk": "ПРИСТРОЇ", "kk": "ҚҰРЫЛҒЫЛАР", "ar": "الأجهزة"
    },
    "privacy.sec_remote": {
        "en": "REMOTE ACCESS", "ru": "УДАЛЕННЫЙ ДОСТУП", "es": "ACCESO REMOTO", "de": "FERNZUGRIFF",
        "fr": "ACCÈS À DISTANCE", "zh_CN": "远程访问", "ja": "リモートアクセス", "it": "ACCESSO REMOTO",
        "pt_BR": "ACESSO REMOTO", "tr": "UZAKTAN ERİŞİM", "uk": "ВІДДАЛЕНИЙ ДОСТУП", "kk": "ҚАШЫҚТАН ҚОЛЖЕТІМДІЛІК", "ar": "الوصول عن بعد"
    },
    "privacy.back_btn": {
        "en": "‹ Privacy & Security", "ru": "‹ Конфиденциальность", "es": "‹ Privacidad y seguridad", "de": "‹ Datenschutz",
        "fr": "‹ Confidentialité", "zh_CN": "‹ 隐私与安全性", "ja": "‹ プライバシー", "it": "‹ Privacy",
        "pt_BR": "‹ Privacidade", "tr": "‹ Gizlilik", "uk": "‹ Конфіденційність", "kk": "‹ Құпиялылық", "ar": "‹ الخصوصية والأمان"
    },
    "privacy.screen_lock": {
        "en": "Screen Lock", "ru": "Блокировка экрана", "es": "Bloqueo de pantalla", "de": "Bildschirmsperre",
        "fr": "Verrouillage de l'écran", "zh_CN": "锁定屏幕", "ja": "画面ロック", "it": "Blocco schermo",
        "pt_BR": "Bloqueio de Tela", "tr": "Ekran Kilidi", "uk": "Блокування екрана", "kk": "Экранды құлыптау", "ar": "قفل الشاشة"
    },
    "privacy.screen_lock_sub": {
        "en": "Manage screen timeout and automatic locking", "ru": "Автоблокировка и тайм-аут экрана",
        "es": "Administrar tiempo de espera y bloqueo", "de": "Bildschirm-Timeout und Sperre verwalten",
        "fr": "Gérer le verrouillage et délai d'extinction", "zh_CN": "管理屏幕熄灭与自动锁定超时",
        "ja": "画面のタイムアウトと自動ロックを管理", "it": "Gestisci timeout e blocco automatico",
        "pt_BR": "Gerenciar tempo limite e bloqueio automático", "tr": "Ekran zaman aşımını ve kilitlemeyi yönet",
        "uk": "Керування блокуванням та вимкненням екрана", "kk": "Экранды автоматты құлыптауды басқару", "ar": "إدارة مهلة الشاشة والقفل التلقائي"
    },
    "privacy.never": {
        "en": "Never", "ru": "Никогда", "es": "Nunca", "de": "Nie",
        "fr": "Jamais", "zh_CN": "从不", "ja": "しない", "it": "Mai",
        "pt_BR": "Nunca", "tr": "Asla", "uk": "Ніколи", "kk": "Ешқашан", "ar": "أبداً"
    },
    "privacy.5m": {
        "en": "5 min", "ru": "5 мин", "es": "5 min", "de": "5 Min",
        "fr": "5 min", "zh_CN": "5分钟", "ja": "5分", "it": "5 min",
        "pt_BR": "5 min", "tr": "5 dk", "uk": "5 хв", "kk": "5 мин", "ar": "5 دقائق"
    },
    "privacy.15m": {
        "en": "15 min", "ru": "15 мин", "es": "15 min", "de": "15 Min",
        "fr": "15 min", "zh_CN": "15分钟", "ja": "15分", "it": "15 min",
        "pt_BR": "15 min", "tr": "15 dk", "uk": "15 хв", "kk": "15 мин", "ar": "15 دقيقة"
    },
    "privacy.30m": {
        "en": "30 min", "ru": "30 мин", "es": "30 min", "de": "30 Min",
        "fr": "30 min", "zh_CN": "30分钟", "ja": "30分", "it": "30 min",
        "pt_BR": "30 min", "tr": "30 dk", "uk": "30 хв", "kk": "30 мин", "ar": "30 دقيقة"
    },
    "privacy.immediately": {
        "en": "Immediately", "ru": "Сразу", "es": "Inmediatamente", "de": "Sofort",
        "fr": "Immédiatement", "zh_CN": "立即", "ja": "すぐに", "it": "Immediatamente",
        "pt_BR": "Imediatamente", "tr": "Hemen", "uk": "Одразу", "kk": "Дереу", "ar": "فوراً"
    },
    "privacy.5s": {
        "en": "5 sec", "ru": "5 сек", "es": "5 s", "de": "5 Sek",
        "fr": "5 s", "zh_CN": "5秒", "ja": "5秒", "it": "5 s",
        "pt_BR": "5 s", "tr": "5 sn", "uk": "5 с", "kk": "5 сек", "ar": "5 ثوانٍ"
    },
    "privacy.1m": {
        "en": "1 min", "ru": "1 мин", "es": "1 min", "de": "1 Min",
        "fr": "1 min", "zh_CN": "1分钟", "ja": "1分", "it": "1 min",
        "pt_BR": "1 min", "tr": "1 dk", "uk": "1 хв", "kk": "1 мин", "ar": "دقيقة واحدة"
    },
    "privacy.location": {
        "en": "Location Services", "ru": "Службы геолокации", "es": "Servicios de ubicación", "de": "Ortungsdienste",
        "fr": "Services de localisation", "zh_CN": "定位服务", "ja": "位置情報サービス", "it": "Servizi di localizzazione",
        "pt_BR": "Serviços de Localização", "tr": "Konum Servisleri", "uk": "Служби локації", "kk": "Орналасу қызметтері", "ar": "خدمات الموقع"
    },
    "privacy.location_sub": {
        "en": "Control location access for apps and services", "ru": "Доступ приложений и служб к геопозиции",
        "es": "Controlar acceso a la ubicación", "de": "Standortzugriff für Apps steuern",
        "fr": "Contrôler l'accès à la localisation", "zh_CN": "控制应用程序与服务的地理位置访问",
        "ja": "アプリとサービスの位置情報アクセスを制御", "it": "Controlla l'accesso alla posizione",
        "pt_BR": "Controlar acesso à localização", "tr": "Uygulamaların konum erişimini denetle",
        "uk": "Доступ додатків до розташування", "kk": "Қолданбалардың геолокацияға қолжетімділігі", "ar": "التحكم في وصول التطبيقات إلى الموقع"
    },
    "privacy.history": {
        "en": "File & Recent History", "ru": "История файлов и действий", "es": "Historial de archivos", "de": "Datei- und Verlaufsdaten",
        "fr": "Historique des fichiers", "zh_CN": "文件与最近记录", "ja": "ファイルと最近の履歴", "it": "Cronologia file",
        "pt_BR": "Histórico de Arquivos", "tr": "Dosya ve Geçmiş Kayıtları", "uk": "Історія файлів та дій", "kk": "Файлдар мен соңғы әрекеттер тарихы", "ar": "سجل الملفات والنشاط الأخير"
    },
    "privacy.history_sub": {
        "en": "Manage recent files and clear history", "ru": "Управление недавними файлами и очистка",
        "es": "Administrar archivos recientes y limpiar", "de": "Zuletzt verwendete Dateien verwalten",
        "fr": "Gérer les fichiers récents et effacer", "zh_CN": "管理最近打开的文件记录与清除历史",
        "ja": "最近使ったファイルの管理と消去", "it": "Gestisci file recenti e cancella cronologia",
        "pt_BR": "Gerenciar arquivos recentes e limpar", "tr": "Son dosyaları yönet ve geçmişi temizle",
        "uk": "Керування недавніми файлами та очищення", "kk": "Соңғы файлдарды басқару және тазалау", "ar": "إدارة الملفات الأخيرة ومسح السجل"
    },
    "privacy.camera": {
        "en": "Camera", "ru": "Камера", "es": "Cámara", "de": "Kamera",
        "fr": "Appareil photo", "zh_CN": "摄像头访问", "ja": "カメラ", "it": "Fotocamera",
        "pt_BR": "Câmera", "tr": "Kamera", "uk": "Камера", "kk": "Камера", "ar": "الكاميرا"
    },
    "privacy.camera_sub": {
        "en": "Manage camera access for apps and services", "ru": "Управление доступом к веб-камере",
        "es": "Gestionar acceso a la cámara", "de": "Kamerazugriff verwalten",
        "fr": "Gérer l'accès à la caméra", "zh_CN": "控制应用程序对摄像头的硬件访问权限",
        "ja": "カメラへのアクセス許可を管理", "it": "Gestisci l'accesso alla fotocamera",
        "pt_BR": "Gerenciar acesso à câmera", "tr": "Kamera erişim izinlerini yönet",
        "uk": "Керування доступом до веб-камери", "kk": "Камераға қолжетімділікті басқару", "ar": "إدارة وصول التطبيقات إلى الكاميرا"
    },
    "privacy.microphone": {
        "en": "Microphone", "ru": "Микрофон", "es": "Micrófono", "de": "Mikrofon",
        "fr": "Microphone", "zh_CN": "麦克风访问", "ja": "マイク", "it": "Microfono",
        "pt_BR": "Microfone", "tr": "Mikrofon", "uk": "Мікрофон", "kk": "Микрофон", "ar": "الميكروفون"
    },
    "privacy.microphone_sub": {
        "en": "Manage microphone access for apps and services", "ru": "Управление доступом к микрофону",
        "es": "Gestionar acceso al micrófono", "de": "Mikrofonzugriff verwalten",
        "fr": "Gérer l'accès au microphone", "zh_CN": "控制应用程序对麦克风的音频录制权限",
        "ja": "マイクへのアクセス許可を管理", "it": "Gestisci l'accesso al microfono",
        "pt_BR": "Gerenciar acesso ao microfone", "tr": "Mikrofon erişim izinlerini yönet",
        "uk": "Керування доступом до мікрофона", "kk": "Микрофонға қолжетімділікті басқару", "ar": "إدارة وصول التطبيقات إلى الميكروفون"
    },
    "privacy.device_security": {
        "en": "Device Security", "ru": "Безопасность устройства", "es": "Seguridad del dispositivo", "de": "Gerätesicherheit",
        "fr": "Sécurité de l'appareil", "zh_CN": "设备安全性", "ja": "デバイスセキュリティ", "it": "Sicurezza dispositivo",
        "pt_BR": "Segurança do Dispositivo", "tr": "Cihaz Güvenliği", "uk": "Безпека пристрою", "kk": "Құрылғы қауіпсіздігі", "ar": "أمان الجهاز"
    },
    "privacy.device_security_sub": {
        "en": "View device security status and trusted devices", "ru": "Защита USB-портов и статус безопасности",
        "es": "Estado de seguridad y dispositivos USB", "de": "Gerätesicherheit und USB-Schutz",
        "fr": "Sécurité et protection USB", "zh_CN": "查看设备安全状态并限制未经授权的 USB 连接",
        "ja": "セキュリティ状態とUSB保護を管理", "it": "Stato di sicurezza e protezione USB",
        "pt_BR": "Status de segurança e proteção USB", "tr": "Cihaz güvenlik durumu ve USB koruması",
        "uk": "Захист USB та стан безпеки", "kk": "Қауіпсіздік күйі және USB қорғауы", "ar": "عرض حالة أمان الجهاز وحماية USB"
    },
    "privacy.remote_desktop": {
        "en": "Remote Desktop", "ru": "Удалённый рабочий стол", "es": "Escritorio remoto", "de": "Entfernter Desktop",
        "fr": "Bureau à distance", "zh_CN": "远程桌面", "ja": "リモートデスクトップ", "it": "Desktop remoto",
        "pt_BR": "Área de Trabalho Remota", "tr": "Uzak Masaüstü", "uk": "Віддалений робочий стіл", "kk": "Қашықтағы жұмыс үстелі", "ar": "سطح المكتب البعيد"
    },
    "privacy.remote_desktop_sub": {
        "en": "Manage remote desktop access to this device", "ru": "Удалённый доступ к рабочему столу (RDP)",
        "es": "Gestionar acceso a escritorio remoto", "de": "Remotedesktop-Zugriff verwalten",
        "fr": "Gérer l'accès bureau à distance", "zh_CN": "配置基于 RDP 协议的远程桌面访问",
        "ja": "RDP によるリモートデスクトップ接続を管理", "it": "Gestisci l'accesso al desktop remoto via RDP",
        "pt_BR": "Gerenciar conexões de área de trabalho remota", "tr": "Uzak masaüstü erişimini yönet",
        "uk": "Керування віддаленим робочим столом (RDP)", "kk": "Қашықтағы жұмыс үстелін басқару (RDP)", "ar": "إدارة الوصول إلى سطح المكتب البعيد"
    },
    "privacy.remote_control": {
        "en": "Remote Control Mode", "ru": "Режим удалённого управления", "es": "Modo de control remoto", "de": "Fernsteuerungsmodus",
        "fr": "Mode de contrôle à distance", "zh_CN": "远程控制模式", "ja": "リモートコントロールモード", "it": "Modalità controllo remoto",
        "pt_BR": "Modo de Controle Remoto", "tr": "Uzaktan Denetim Modu", "uk": "Режим віддаленого керування", "kk": "Қашықтан басқару режимі", "ar": "وضع التحكم عن بعد"
    },
    "privacy.remote_control_sub": {
        "en": "Allow this device to be controlled remotely", "ru": "Дистанционный ввод с клавиатуры и мыши",
        "es": "Permitir control remoto", "de": "Fernsteuerung zulassen",
        "fr": "Autoriser le contrôle à distance", "zh_CN": "允许通过远程会话接收键盘和鼠标输入",
        "ja": "リモートセッションからの入力を許可", "it": "Consenti il controllo remoto del dispositivo",
        "pt_BR": "Permitir controle remoto deste dispositivo", "tr": "Bu cihazın uzaktan kontrol edilmesine izin ver",
        "uk": "Дозволити дистанційне керування пристроєм", "kk": "Осы құрылғыны қашықтан басқаруға рұқсат ету", "ar": "السماح بالتحكم في هذا الجهاز عن بعد"
    },
    "privacy.view_only": {
        "en": "View Only", "ru": "Только просмотр", "es": "Solo vista", "de": "Nur Anzeige",
        "fr": "Affichage seul", "zh_CN": "仅查看", "ja": "表示のみ", "it": "Sola visualizzazione",
        "pt_BR": "Apenas Visualização", "tr": "Yalnızca Görüntüle", "uk": "Лише перегляд", "kk": "Тек көру", "ar": "عرض فقط"
    },
    "privacy.full_control": {
        "en": "Full Control", "ru": "Полный контроль", "es": "Control total", "de": "Vollzugriff",
        "fr": "Contrôle total", "zh_CN": "完全控制", "ja": "完全制御", "it": "Controllo completo",
        "pt_BR": "Controle Total", "tr": "Tam Denetim", "uk": "Повний контроль", "kk": "Толық басқару", "ar": "تحكم كامل"
    },
    "privacy.screen_lock_desc": {
        "en": "Automatic screen locking helps protect your device and privacy when you step away.",
        "ru": "Автоматическая блокировка экрана защищает устройство и конфиденциальность, когда вы отходите.",
        "es": "El bloqueo automático protege su equipo y privacidad cuando se ausenta.",
        "de": "Die automatische Bildschirmsperre schützt Ihr Gerät, wenn Sie abwesend sind.",
        "fr": "Le verrouillage automatique protège vos données en cas d'absence.",
        "zh_CN": "离开电脑时自动锁定屏幕有助于保护您的设备与个人隐私数据安全。",
        "ja": "席を離れる際に自動的に画面をロックし、デバイスとプライバシーを保護します。",
        "it": "Il blocco automatico dello schermo protegge il dispositivo quando ti allontani.",
        "pt_BR": "O bloqueio automático ajuda a proteger seu dispositivo quando você se ausenta.",
        "tr": "Otomatik ekran kilitleme, ayrıldığınızda cihazınızı korumaya yardımcı olur.",
        "uk": "Автоматичне блокування екрана захищає ваш пристрій, коли ви відходите.",
        "kk": "Экранды автоматты құлыптау құрылғыңыз бен құпиялылығыңызды қорғайды.",
        "ar": "يساعد القفل التلقائي للشاشة في حماية جهازك وخصوصيتك عند الابتعاد."
    },
    "privacy.location_desc": {
        "en": "Location Services allows apps and system services to determine your approximate geographic location using GeoClue2.",
        "ru": "Службы геолокации позволяют приложениям и службам определять ваше примерное местоположение с помощью GeoClue2.",
        "es": "Permite que las apps determinen su ubicación aproximada mediante GeoClue2.",
        "de": "Ermöglicht Apps die Bestimmung Ihres ungefähren Standorts über GeoClue2.",
        "fr": "Permet aux applications de déterminer votre position géographique via GeoClue2.",
        "zh_CN": "定位服务允许应用程序与系统组件通过 GeoClue2 获取您的地理位置坐标。",
        "ja": "GeoClue2 を使用してアプリがおおよその位置情報を取得できるようにします。",
        "it": "Consente alle app di rilevare la posizione approssimativa tramite GeoClue2.",
        "pt_BR": "Permite que apps determinem sua localização geográfica via GeoClue2.",
        "tr": "Uygulamaların GeoClue2 kullanarak yaklaşık konumunuzu belirlemesini sağlar.",
        "uk": "Дозволяє програмам визначати ваше приблизне розташування за допомогою GeoClue2.",
        "kk": "Қолданбаларға GeoClue2 арқылы шамамен орналасқан жеріңізді анықтауға мүмкіндік береді.",
        "ar": "تتيح خدمات الموقع للتطبيقات تحديد موقعك الجغرافي التقريبي باستخدام GeoClue2."
    },
    "privacy.history_desc": {
        "en": "Manage document tracking and application usage history across the system.",
        "ru": "Управление отслеживанием недавних документов и историей использования приложений.",
        "es": "Administre el historial de uso de aplicaciones y documentos recientes.",
        "de": "Verwalten Sie den Verlauf zuletzt verwendeter Dateien und Apps.",
        "fr": "Gérez l'historique des documents et de l'utilisation des applications.",
        "zh_CN": "管理系统级最近使用的文档记录与应用程序使用频次统计。",
        "ja": "最近開いたドキュメントとアプリの使用頻度履歴を管理します。",
        "it": "Gestisci la cronologia dei documenti recenti e delle applicazioni.",
        "pt_BR": "Gerencie o histórico de documentos e uso de aplicativos no sistema.",
        "tr": "Belge geçmişini ve uygulama kullanım kayıtlarını yönetin.",
        "uk": "Керування історією відкритих файлів та запуску додатків.",
        "kk": "Құжаттар мен қолданбаларды пайдалану тарихын басқару.",
        "ar": "إدارة تتبع المستندات وسجل استخدام التطبيقات في النظام."
    },
    "privacy.camera_desc": {
        "en": "Control global camera hardware access for applications and browser portals.",
        "ru": "Управление глобальным доступом приложений и браузеров к веб-камере.",
        "es": "Controlar el acceso a la cámara para aplicaciones y portales web.",
        "de": "Kamerazugriff für Apps und Webportale steuern.",
        "fr": "Contrôler l'accès matériel à la caméra pour les applications.",
        "zh_CN": "统一管理所有已安装应用程序与浏览器门户的摄像头视频捕获权限。",
        "ja": "アプリやブラウザによるカメラハードウェアへのアクセスを制御します。",
        "it": "Controlla l'accesso alla fotocamera per le applicazioni.",
        "pt_BR": "Controle o acesso global à câmera para aplicativos e navegadores.",
        "tr": "Uygulamalar için genel kamera erişim izinlerini denetleyin.",
        "uk": "Керування доступом програм та браузерів до веб-камери.",
        "kk": "Қолданбалар мен веб-порталдар үшін камераға қолжетімділікті басқару.",
        "ar": "التحكم في وصول التطبيقات إلى أجهزة الكاميرا."
    },
    "privacy.microphone_desc": {
        "en": "Control global microphone input and audio capture permissions across PipeWire.",
        "ru": "Управление глобальным доступом приложений к записи звука с микрофона через PipeWire.",
        "es": "Controlar el acceso al micrófono y captura de audio a través de PipeWire.",
        "de": "Mikrofonzugriff und Audioaufnahme über PipeWire steuern.",
        "fr": "Contrôler l'accès au microphone pour les applications via PipeWire.",
        "zh_CN": "统一管理系统所有应用程序通过 PipeWire 音频服务器的录音权限。",
        "ja": "PipeWire 経由でのアプリのマイク録音アクセスを制御します。",
        "it": "Controlla le autorizzazioni di acquisizione audio del microfono tramite PipeWire.",
        "pt_BR": "Controle o acesso global ao microfone e áudio via PipeWire.",
        "tr": "PipeWire üzerinden genel mikrofon erişimini denetleyin.",
        "uk": "Керування доступом програм до запису звуку через PipeWire.",
        "kk": "PipeWire арқылы микрофонға қолжетімділікті басқару.",
        "ar": "التحكم في وصول التطبيقات إلى الميكروفون عبر PipeWire."
    },
    "privacy.device_security_desc": {
        "en": "View device security status and restrict unauthorized physical USB access.",
        "ru": "Просмотр статуса безопасности и блокировка несанкционированного подключения USB-устройств.",
        "es": "Verifique el estado de seguridad y restrinja dispositivos USB no autorizados.",
        "de": "Gerätesicherheitsstatus einsehen und unbefugten USB-Zugriff sperren.",
        "fr": "Afficher la sécurité et restreindre les périphériques USB non autorisés.",
        "zh_CN": "查看设备安全状态并限制锁屏状态下未经授权的物理 USB 设备接入。",
        "ja": "セキュリティ状態を確認し、不正なUSB接続を制限します。",
        "it": "Verifica lo stato di sicurezza e limita l'accesso fisico ai dispositivi USB.",
        "pt_BR": "Visualize o status de segurança e restrinja dispositivos USB não autorizados.",
        "tr": "Cihaz güvenlik durumunu görüntüleyin ve yetkisiz USB erişimini kısıtlayın.",
        "uk": "Перегляд стану безпеки та обмеження неавторизованого доступу USB.",
        "kk": "Қауіпсіздік күйін көру және рұқсатсыз USB қосылыстарын шектеу.",
        "ar": "عرض حالة أمان الجهاز وتقييد وصول أجهزة USB غير المصرح بها."
    },
    "privacy.remote_desktop_desc": {
        "en": "Manage remote desktop connections to this machine using GNOME Remote Desktop (RDP).",
        "ru": "Управление подключениями к удалённому рабочему столу этого ПК по протоколу RDP.",
        "es": "Administrar conexiones de escritorio remoto a este equipo mediante RDP.",
        "de": "Remotedesktop-Verbindungen zu diesem PC über RDP verwalten.",
        "fr": "Gérer les connexions bureau à distance vers cet ordinateur via RDP.",
        "zh_CN": "通过 GNOME Remote Desktop (RDP) 管理对本机的远程桌面访问。",
        "ja": "GNOME Remote Desktop (RDP) によるこのPCへの接続を管理します。",
        "it": "Gestisci le connessioni al desktop remoto su questa macchina tramite RDP.",
        "pt_BR": "Gerencie conexões de área de trabalho remota usando RDP.",
        "tr": "GNOME Uzak Masaüstü (RDP) kullanarak uzak bağlantıları yönetin.",
        "uk": "Керування підключеннями до віддаленого робочого столу через RDP.",
        "kk": "Осы компьютерге RDP арқылы қашықтағы жұмыс үстелі қосылыстарын басқару.",
        "ar": "إدارة اتصالات سطح المكتب البعيد بهذا الجهاز باستخدام RDP."
    },
    "privacy.remote_control_desc": {
        "en": "Configure remote input permissions for keyboard, mouse, and touch events over remote connections.",
        "ru": "Настройка разрешений на ввод с клавиатуры, мыши и сенсорного экрана при удалённом подключении.",
        "es": "Configurar permisos de entrada remota para teclado, ratón y eventos táctiles.",
        "de": "Berechtigungen für Tastatur- und Mauseingaben bei Fernverbindungen konfigurieren.",
        "fr": "Configurer les autorisations de saisie distante pour le clavier et la souris.",
        "zh_CN": "配置远程会话中键盘、鼠标以及触摸屏等输入设备的控制权限。",
        "ja": "リモート接続時のキーボード、マウス、タッチ入力の制御権限を設定します。",
        "it": "Configura i permessi di input remoto per tastiera, mouse e touchscreen.",
        "pt_BR": "Configure permissões de entrada remota para teclado, mouse e toque.",
        "tr": "Uzak bağlantılarda klavye ve fare giriş izinlerini yapılandırın.",
        "uk": "Налаштування дозволів на дистанційне введення з клавіатури та миші.",
        "kk": "Қашықтан қосылғанда пернетақта мен тінтуірдің енгізу рұқсаттарын баптау.",
        "ar": "تكوين أذونات الإدخال عن بعد للوحة المفاتيح والماوس والأجهزة اللمسية."
    },
    "privacy.screen_lock_row": {
        "en": "Screen Lock", "ru": "Блокировка экрана", "es": "Bloqueo de pantalla", "de": "Bildschirmsperre",
        "fr": "Verrouillage de l'écran", "zh_CN": "自动锁定屏幕", "ja": "画面ロック", "it": "Blocco schermo",
        "pt_BR": "Bloqueio de Tela", "tr": "Ekran Kilidi", "uk": "Блокування екрана", "kk": "Экранды құлыптау", "ar": "قفل الشاشة"
    },
    "privacy.lock_notif": {
        "en": "Show Notifications on Lock Screen", "ru": "Уведомления на экране блокировки",
        "es": "Notificaciones en pantalla bloqueada", "de": "Mitteilungen auf Sperrbildschirm",
        "fr": "Notifications sur l'écran verrouillé", "zh_CN": "在锁定屏幕上显示通知提醒",
        "ja": "ロック画面に通知を表示", "it": "Mostra notifiche su schermata di blocco",
        "pt_BR": "Mostrar Notificações na Tela de Bloqueio", "tr": "Kilit Ekranında Bildirimleri Göster",
        "uk": "Сповіщення на екрані блокування", "kk": "Құлыпталған экранда хабарландыруларды көрсету", "ar": "إظهار الإشعارات على شاشة القفل"
    },
    "privacy.sec_timeouts": {
        "en": "TIMEOUTS & DELAYS", "ru": "ТАЙМ-АУТЫ И ЗАДЕРЖКИ", "es": "TIEMPOS DE ESPERA", "de": "TIMEOUTS & VERZÖGERUNGEN",
        "fr": "DÉLAIS D'ATTENTE", "zh_CN": "超时与延迟设置", "ja": "タイムアウトと遅延", "it": "TIMEOUT E RITARDI",
        "pt_BR": "TEMPOS LIMITE E ATRASOS", "tr": "ZAMAN AŞIMLARI VE GECİKMELER", "uk": "ТАЙМ-АУТИ ТА ЗАТРИМКИ", "kk": "КҮТУ УАҚЫТТАРЫ МЕН КІДІРІСТЕР", "ar": "المهلات والتأخير"
    },
    "privacy.turn_off_screen": {
        "en": "Turn Screen Off", "ru": "Выключение экрана", "es": "Apagar pantalla", "de": "Bildschirm ausschalten",
        "fr": "Éteindre l'écran", "zh_CN": "屏幕熄灭时间", "ja": "画面の消灯", "it": "Spegni schermo",
        "pt_BR": "Desligar Tela", "tr": "Ekranı Kapat", "uk": "Вимкнення екрана", "kk": "Экранды өшіру", "ar": "إيقاف تشغيل الشاشة"
    },
    "privacy.lock_delay": {
        "en": "Lock Delay after Screen Off", "ru": "Задержка блокировки", "es": "Retardo de bloqueo tras apagar pantalla",
        "de": "Sperrverzögerung nach Ausschalten", "fr": "Délai de verrouillage après extinction", "zh_CN": "屏幕熄灭后锁定延迟",
        "ja": "消灯後のロック遅延", "it": "Ritardo blocco dopo spegnimento", "pt_BR": "Atraso no Bloqueio após Tela Desligada",
        "tr": "Ekran Kapandıktan Sonra Kilitleme Gecikmesi", "uk": "Затримка блокування після вимкнення", "kk": "Экран өшкеннен кейінгі құлыптау кідірісі", "ar": "تأخير القفل بعد إيقاف الشاشة"
    },
    "privacy.accuracy": {
        "en": "Accuracy Level", "ru": "Уровень точности", "es": "Nivel de precisión", "de": "Genauigkeitsstufe",
        "fr": "Niveau de précision", "zh_CN": "定位精确度", "ja": "精度レベル", "it": "Livello di precisione",
        "pt_BR": "Nível de Precisão", "tr": "Hassasiyet Düzeyi", "uk": "Рівень точності", "kk": "Дәлдік деңгейі", "ar": "مستوى الدقة"
    },
    "privacy.exact": {
        "en": "Exact", "ru": "Точный", "es": "Exacta", "de": "Exakt",
        "fr": "Exact", "zh_CN": "精确坐标", "ja": "正確", "it": "Esatto",
        "pt_BR": "Exato", "tr": "Tam", "uk": "Точний", "kk": "Дәл", "ar": "دقيق"
    },
    "privacy.city": {
        "en": "City", "ru": "Город", "es": "Ciudad", "de": "Stadt",
        "fr": "Ville", "zh_CN": "城市级别", "ja": "都市", "it": "Città",
        "pt_BR": "Cidade", "tr": "Şehir", "uk": "Місто", "kk": "Қала", "ar": "مدينة"
    },
    "privacy.country": {
        "en": "Country", "ru": "Страна", "es": "País", "de": "Land",
        "fr": "Pays", "zh_CN": "国家级别", "ja": "国", "it": "Paese",
        "pt_BR": "País", "tr": "Ülke", "uk": "Країна", "kk": "Ел", "ar": "دولة"
    },
    "privacy.system_daemon": {
        "en": "System Daemon", "ru": "Системный демон", "es": "Demonio del sistema", "de": "Systemdienst",
        "fr": "Démon système", "zh_CN": "系统后台守护进程", "ja": "システムデーモン", "it": "Demone di sistema",
        "pt_BR": "Daemon do Sistema", "tr": "Sistem Arka Plan Hizmeti", "uk": "Системний демон", "kk": "Жүйелік демон", "ar": "برنامج النظام الخفي"
    },
    "privacy.remember_recent": {
        "en": "Remember Recent Files", "ru": "Запоминать недавние файлы", "es": "Recordar archivos recientes", "de": "Zuletzt verwendete Dateien merken",
        "fr": "Mémoriser les fichiers récents", "zh_CN": "记录最近访问的文档与文件", "ja": "最近使ったファイルを記録", "it": "Ricorda file recenti",
        "pt_BR": "Lembrar Arquivos Recentes", "tr": "Son Dosyaları Hatırla", "uk": "Запам'ятовувати недавні файли", "kk": "Соңғы файлдарды есте сақтау", "ar": "تذكر الملفات الأخيرة"
    },
    "privacy.remember_usage": {
        "en": "Remember App Usage Frequency", "ru": "Запоминать частоту использования приложений", "es": "Recordar frecuencia de uso de apps",
        "de": "App-Nutzungshäufigkeit merken", "fr": "Mémoriser la fréquence d'utilisation", "zh_CN": "记录应用程序使用频率与偏好",
        "ja": "アプリの使用頻度を記録", "it": "Ricorda frequenza d'uso app", "pt_BR": "Lembrar Frequência de Uso de Apps",
        "tr": "Uygulama Kullanım Sıklığını Hatırla", "uk": "Запам'ятовувати частоту запуску додатків", "kk": "Қолданбаларды пайдалану жиілігін есте сақтау", "ar": "تذكر تكرار استخدام التطبيقات"
    },
    "privacy.sec_cleanup": {
        "en": "CLEANUP & RETENTION", "ru": "ОЧИСТКА И ХРАНЕНИЕ", "es": "LIMPIEZA", "de": "BEREINIGUNG",
        "fr": "NETTOYAGE", "zh_CN": "清理与保留周期", "ja": "クリーンアップと保持", "it": "PULIZIA",
        "pt_BR": "LIMPEZA E RETENÇÃO", "tr": "TEMİZLEME VE SAKLAMA", "uk": "ОЧИЩЕННЯ ТА ЗБЕРІГАННЯ", "kk": "ТАЗАЛАУ ЖӘНЕ САҚТАУ", "ar": "التنظيف والاحتفاظ"
    },
    "privacy.clear_history": {
        "en": "Clear File History", "ru": "Очистить историю файлов", "es": "Borrar historial de archivos", "de": "Dateiverlauf löschen",
        "fr": "Effacer l'historique des fichiers", "zh_CN": "清除最近文件历史记录", "ja": "ファイル履歴を消去", "it": "Cancella cronologia file",
        "pt_BR": "Limpar Histórico de Arquivos", "tr": "Dosya Geçmişini Temizle", "uk": "Очистити історію файлів", "kk": "Файлдар тарихын тазалау", "ar": "مسح سجل الملفات"
    },
    "privacy.clear_btn": {
        "en": "Clear File History...", "ru": "Очистить историю...", "es": "Borrar historial...", "de": "Verlauf löschen...",
        "fr": "Effacer l'historique...", "zh_CN": "立即清除历史记录...", "ja": "履歴を消去...", "it": "Cancella cronologia...",
        "pt_BR": "Limpar Histórico...", "tr": "Geçmişi Temizle...", "uk": "Очистити історію...", "kk": "Тарихты тазалау...", "ar": "مسح السجل..."
    },
    "privacy.cleared": {
        "en": "✓ Cleared", "ru": "✓ Очищено", "es": "✓ Borrado", "de": "✓ Gelöscht",
        "fr": "✓ Effacé", "zh_CN": "✓ 已清除", "ja": "✓ 消去完了", "it": "✓ Cancellato",
        "pt_BR": "✓ Limpo", "tr": "✓ Temizlendi", "uk": "✓ Очищено", "kk": "✓ Тазаланды", "ar": "✓ تم المسح"
    },
    "privacy.camera_access": {
        "en": "Camera Access", "ru": "Доступ к камере", "es": "Acceso a la cámara", "de": "Kamerazugriff",
        "fr": "Accès caméra", "zh_CN": "摄像头访问权限", "ja": "カメラアクセス", "it": "Accesso fotocamera",
        "pt_BR": "Acesso à Câmera", "tr": "Kamera Erişimi", "uk": "Доступ до камери", "kk": "Камераға қолжетімділік", "ar": "الوصول إلى الكاميرا"
    },
    "privacy.camera_hw": {
        "en": "Camera Hardware", "ru": "Оборудование камеры", "es": "Hardware de cámara", "de": "Kamerahardware",
        "fr": "Matériel caméra", "zh_CN": "摄像头硬件状态", "ja": "カメラハードウェア", "it": "Hardware fotocamera",
        "pt_BR": "Hardware da Câmera", "tr": "Kamera Donanımı", "uk": "Обладнання камери", "kk": "Камера құрылғысы", "ar": "أجهزة الكاميرا"
    },
    "privacy.connected": {
        "en": "Connected", "ru": "Подключена", "es": "Conectada", "de": "Verbunden",
        "fr": "Connectée", "zh_CN": "已连接", "ja": "接続済み", "it": "Collegata",
        "pt_BR": "Conectado", "tr": "Bağlı", "uk": "Підключено", "kk": "Қосылған", "ar": "متصل"
    },
    "privacy.no_cam": {
        "en": "No Camera Connected", "ru": "Камера не подключена", "es": "No hay cámara conectada", "de": "Keine Kamera angeschlossen",
        "fr": "Aucune caméra connectée", "zh_CN": "未检测到摄像头硬件", "ja": "カメラが接続されていません", "it": "Nessuna fotocamera collegata",
        "pt_BR": "Nenhuma Câmera Conectada", "tr": "Kamera Bağlı Değil", "uk": "Камеру не виявлено", "kk": "Камера қосылмаған", "ar": "لا توجد كاميرا متصلة"
    },
    "privacy.capture_pipe": {
        "en": "Capture Pipeline", "ru": "Канал захвата", "es": "Canal de captura", "de": "Aufnahmepipeline",
        "fr": "Pipeline de capture", "zh_CN": "媒体采集管道", "ja": "キャプチャパイプライン", "it": "Pipeline di acquisizione",
        "pt_BR": "Pipeline de Captura", "tr": "Yakalama Hattı", "uk": "Канал захоплення", "kk": "Түсіру арнасы", "ar": "خط أنابيب الالتقاط"
    },
    "privacy.mic_access": {
        "en": "Microphone Access", "ru": "Доступ к микрофону", "es": "Acceso al micrófono", "de": "Mikrofonzugriff",
        "fr": "Accès microphone", "zh_CN": "麦克风访问权限", "ja": "マイクアクセス", "it": "Accesso microfono",
        "pt_BR": "Acesso ao Microfone", "tr": "Mikrofon Erişimi", "uk": "Доступ до мікрофона", "kk": "Микрофонға қолжетімділік", "ar": "الوصول إلى الميكروفون"
    },
    "privacy.default_input": {
        "en": "Default Input Device", "ru": "Основное устройство ввода", "es": "Dispositivo de entrada predeterminado", "de": "Standard-Eingabegerät",
        "fr": "Périphérique d'entrée par défaut", "zh_CN": "默认音频输入设备", "ja": "デフォルト入力デバイス", "it": "Dispositivo di input predefinito",
        "pt_BR": "Dispositivo de Entrada Padrão", "tr": "Varsayılan Giriş Aygıtı", "uk": "Основний пристрій вводу", "kk": "Негізгі енгізу құрылғысы", "ar": "جهاز الإدخال الافتراضي"
    },
    "privacy.audio_server": {
        "en": "Audio Server", "ru": "Звуковой сервер", "es": "Servidor de audio", "de": "Audioserver",
        "fr": "Serveur audio", "zh_CN": "音频后端服务", "ja": "オーディオサーバー", "it": "Server audio",
        "pt_BR": "Servidor de Áudio", "tr": "Ses Sunucusu", "uk": "Аудіосервер", "kk": "Дыбыс сервері", "ar": "خادم الصوت"
    },
    "privacy.usb_protection": {
        "en": "USB Device Protection", "ru": "Защита USB-устройств", "es": "Protección de dispositivos USB", "de": "USB-Geräteschutz",
        "fr": "Protection des périphériques USB", "zh_CN": "USB 物理接口外设防护", "ja": "USBデバイス保護", "it": "Protezione dispositivi USB",
        "pt_BR": "Proteção de Dispositivos USB", "tr": "USB Aygıt Koruması", "uk": "Захист пристроїв USB", "kk": "USB құрылғыларын қорғау", "ar": "حماية أجهزة USB"
    },
    "privacy.protection_lvl": {
        "en": "Protection Level", "ru": "Уровень защиты", "es": "Nivel de protección", "de": "Schutzstufe",
        "fr": "Niveau de protection", "zh_CN": "防护生效级别", "ja": "保護レベル", "it": "Livello di protezione",
        "pt_BR": "Nível de Proteção", "tr": "Koruma Düzeyi", "uk": "Рівень захисту", "kk": "Қорғау деңгейі", "ar": "مستوى الحماية"
    },
    "privacy.lockscreen_opt": {
        "en": "Lock Screen", "ru": "При блокировке", "es": "En pantalla bloqueada", "de": "Bei Sperrbildschirm",
        "fr": "À l'écran verrouillé", "zh_CN": "仅锁屏时生效", "ja": "ロック画面のみ", "it": "In schermata di blocco",
        "pt_BR": "Na Tela de Bloqueio", "tr": "Kilit Ekranında", "uk": "При блокуванні", "kk": "Құлыптау кезінде", "ar": "عند قفل الشاشة"
    },
    "privacy.always_opt": {
        "en": "Always", "ru": "Всегда", "es": "Siempre", "de": "Immer",
        "fr": "Toujours", "zh_CN": "始终拦截未受信任设备", "ja": "常に", "it": "Sempre",
        "pt_BR": "Sempre", "tr": "Her Zaman", "uk": "Завжди", "kk": "Әрқашан", "ar": "دائمًا"
    },
    "privacy.security_status": {
        "en": "Security Status", "ru": "Статус безопасности", "es": "Estado de seguridad", "de": "Sicherheitsstatus",
        "fr": "État de la sécurité", "zh_CN": "安全评估状态", "ja": "セキュリティ状態", "it": "Stato di sicurezza",
        "pt_BR": "Status de Segurança", "tr": "Güvenlik Durumu", "uk": "Стан безпеки", "kk": "Қауіпсіздік күйі", "ar": "حالة الأمان"
    },
    "privacy.rdp_toggle": {
        "en": "Remote Desktop (RDP)", "ru": "Удалённый рабочий стол (RDP)", "es": "Escritorio remoto (RDP)", "de": "Remotedesktop (RDP)",
        "fr": "Bureau à distance (RDP)", "zh_CN": "远程桌面服务 (RDP)", "ja": "リモートデスクトップ (RDP)", "it": "Desktop remoto (RDP)",
        "pt_BR": "Área de Trabalho Remota (RDP)", "tr": "Uzak Masaüstü (RDP)", "uk": "Віддалений робочий стіл (RDP)", "kk": "Қашықтағы жұмыс үстелі (RDP)", "ar": "سطح المكتب البعيد (RDP)"
    },
    "privacy.share_mode": {
        "en": "Screen Share Mode", "ru": "Режим трансляции экрана", "es": "Modo de compartir pantalla", "de": "Bildschirmfreigabe-Modus",
        "fr": "Mode de partage d'écran", "zh_CN": "屏幕共享模式", "ja": "画面共有モード", "it": "Modalità condivisione schermo",
        "pt_BR": "Modo de Compartilhamento de Tela", "tr": "Ekran Paylaşım Modu", "uk": "Режим спільного використання екрана", "kk": "Экранды бөлісу режимі", "ar": "وضع مشاركة الشاشة"
    },
    "privacy.mirror_primary": {
        "en": "Mirror Primary", "ru": "Дублировать основной", "es": "Duplicar principal", "de": "Hauptbildschirm spiegeln",
        "fr": "Dupliquer l'écran principal", "zh_CN": "镜像主显示器", "ja": "主画面をミラーリング", "it": "Duplica principale",
        "pt_BR": "Espelhar Principal", "tr": "Birincil Ekranı Yansıt", "uk": "Дублювати головний", "kk": "Негізгі экранды қайталау", "ar": "مرآة الشاشة الرئيسية"
    },
    "privacy.extend_disp": {
        "en": "Extend Display", "ru": "Расширить дисплей", "es": "Extender pantalla", "de": "Anzeige erweitern",
        "fr": "Étendre l'affichage", "zh_CN": "扩展虚拟显示器", "ja": "ディスプレイを拡張", "it": "Estendi schermo",
        "pt_BR": "Estender Tela", "tr": "Ekranı Genişlet", "uk": "Розширити дисплей", "kk": "Экранды кеңейту", "ar": "توسيع الشاشة"
    },
    "privacy.port": {
        "en": "Port", "ru": "Порт", "es": "Puerto", "de": "Port",
        "fr": "Port", "zh_CN": "监听网络端口", "ja": "ポート", "it": "Porta",
        "pt_BR": "Porta", "tr": "Bağlantı Noktası", "uk": "Порт", "kk": "Порт", "ar": "المنفذ"
    },
    "privacy.service_status": {
        "en": "Service Status", "ru": "Статус службы", "es": "Estado del servicio", "de": "Dienststatus",
        "fr": "État du service", "zh_CN": "后台服务运行状态", "ja": "サービス状態", "it": "Stato del servizio",
        "pt_BR": "Status do Serviço", "tr": "Hizmet Durumu", "uk": "Статус служби", "kk": "Қызмет күйі", "ar": "حالة الخدمة"
    },
    "privacy.active": {
        "en": "Active", "ru": "Активна", "es": "Activo", "de": "Aktiv",
        "fr": "Actif", "zh_CN": "运行中", "ja": "アクティブ", "it": "Attivo",
        "pt_BR": "Ativo", "tr": "Etkin", "uk": "Активно", "kk": "Белсенді", "ar": "نشط"
    },
    "privacy.inactive": {
        "en": "Inactive", "ru": "Неактивна", "es": "Inactivo", "de": "Inaktiv",
        "fr": "Inactif", "zh_CN": "已停止", "ja": "非アクティブ", "it": "Inattivo",
        "pt_BR": "Inativo", "tr": "Devre Dışı", "uk": "Неактивно", "kk": "Белсенді емес", "ar": "غير نشط"
    },
    "privacy.control_mode": {
        "en": "Remote Control Mode", "ru": "Режим удалённого управления", "es": "Modo de control remoto", "de": "Fernsteuerungsmodus",
        "fr": "Mode de contrôle à distance", "zh_CN": "远程控制权限级别", "ja": "リモート制御モード", "it": "Modalità controllo remoto",
        "pt_BR": "Modo de Controle Remoto", "tr": "Uzaktan Denetim Modu", "uk": "Режим віддаленого керування", "kk": "Қашықтан басқару режимі", "ar": "وضع التحكم عن بعد"
    },
    "privacy.supported_input": {
        "en": "Supported Input", "ru": "Поддерживаемый ввод", "es": "Entrada compatible", "de": "Unterstützte Eingabe",
        "fr": "Saisie prise en charge", "zh_CN": "支持的输入设备类型", "ja": "対応する入力形式", "it": "Input supportato",
        "pt_BR": "Entrada Suportada", "tr": "Desteklenen Giriş", "uk": "Підтримуване введення", "kk": "Қолдау көрсетілетін енгізу", "ar": "الإدخال المدعوم"
    },
    "privacy.supported_input_val": {
        "en": "Keyboard, Pointer, Touchscreen", "ru": "Клавиатура, указатель, тачскрин", "es": "Teclado, puntero y táctil", "de": "Tastatur, Zeiger, Touchscreen",
        "fr": "Clavier, pointeur, écran tactile", "zh_CN": "键盘、鼠标指针与触摸手势", "ja": "キーボード、ポインタ、タッチ", "it": "Tastiera, puntatore, touchscreen",
        "pt_BR": "Teclado, Cursor e Toque", "tr": "Klavye, İşaretçi, Dokunmatik", "uk": "Клавіатура, вказівник, сенсорний екран", "kk": "Пернетақта, меңзер, сенсорлық экран", "ar": "لوحة المفاتيح والمؤشر وشاشة اللمس"
    },
    "installer.chk_os": {
        "en": "Operating System", "ru": "Операционная система", "es": "Sistema operativo", "de": "Betriebssystem",
        "fr": "Système d'exploitation", "zh_CN": "操作系统", "ja": "オペレーティングシステム", "it": "Sistema operativo",
        "pt_BR": "Sistema Operacional", "tr": "İşletim Sistemi", "uk": "Операційна система", "kk": "Операциялық жүйе", "ar": "نظام التشغيل"
    },
    "installer.chk_arch": {
        "en": "CPU Architecture", "ru": "Архитектура процессора", "es": "Arquitectura de CPU", "de": "CPU-Architektur",
        "fr": "Architecture CPU", "zh_CN": "处理器架构", "ja": "CPU アーキテクチャ", "it": "Architettura CPU",
        "pt_BR": "Arquitetura da CPU", "tr": "İşlemci Mimarisi", "uk": "Архітектура процесора", "kk": "Процессор архитектурасы", "ar": "معمارية المعالج"
    },
    "installer.chk_desktop": {
        "en": "Desktop Environment", "ru": "Рабочее окружение", "es": "Entorno de escritorio", "de": "Desktop-Umgebung",
        "fr": "Environnement de bureau", "zh_CN": "桌面环境", "ja": "デスクトップ環境", "it": "Ambiente desktop",
        "pt_BR": "Ambiente de Trabalho", "tr": "Masaüstü Ortamı", "uk": "Робоче оточення", "kk": "Жұмыс үстелі ортасы", "ar": "بيئة سطح المكتب"
    },
    "installer.chk_display": {
        "en": "Display Server", "ru": "Сервер отображения", "es": "Servidor de pantalla", "de": "Display-Server",
        "fr": "Serveur d'affichage", "zh_CN": "显示服务器", "ja": "ディスプレイサーバー", "it": "Server di visualizzazione",
        "pt_BR": "Servidor de Exibição", "tr": "Görüntü Sunucusu", "uk": "Сервер відображення", "kk": "Бейнелеу сервері", "ar": "خادم العرض"
    },
    "installer.chk_python": {
        "en": "Python Runtime", "ru": "Среда Python", "es": "Entorno Python", "de": "Python-Laufzeitumgebung",
        "fr": "Environnement Python", "zh_CN": "Python 运行环境", "ja": "Python ランタイム", "it": "Runtime Python",
        "pt_BR": "Ambiente Python", "tr": "Python Çalışma Zamanı", "uk": "Середовище Python", "kk": "Python ортасы", "ar": "بيئة تشغيل بايثون"
    },
    "installer.chk_apis": {
        "en": "System Integration APIs", "ru": "Системные API", "es": "APIs de integración", "de": "Systemintegrations-APIs",
        "fr": "API d'intégration système", "zh_CN": "系统集成 API", "ja": "システム統合 API", "it": "API di integrazione",
        "pt_BR": "APIs de Integração", "tr": "Sistem Entegrasyon API'leri", "uk": "Системні API", "kk": "Жүйелік API", "ar": "واجهات برمجة التطبيقات للنظام"
    },
    "installer.chk_dbus": {
        "en": "System Bus & D-Bus", "ru": "Системная шина D-Bus", "es": "Bus del sistema y D-Bus", "de": "Systembus & D-Bus",
        "fr": "Bus système et D-Bus", "zh_CN": "系统总线与 D-Bus", "ja": "システムバス & D-Bus", "it": "Bus di sistema e D-Bus",
        "pt_BR": "Barramento do Sistema e D-Bus", "tr": "Sistem Veri Yolu & D-Bus", "uk": "Системна шина D-Bus", "kk": "Жүйелік шина D-Bus", "ar": "ناقل النظام و D-Bus"
    },
    "privacy.input_emulation": {
        "en": "Input Emulation", "ru": "Эмуляция ввода", "es": "Emulación de entrada", "de": "Eingabeemulation",
        "fr": "Émulation de saisie", "zh_CN": "输入事件合成器", "ja": "入力エミュレーション", "it": "Emulazione input",
        "pt_BR": "Emulação de Entrada", "tr": "Giriş Emülasyonu", "uk": "Емуляція введення", "kk": "Енгізу эмуляциясы", "ar": "محاكاة الإدخال"
    },
    "privacy.status_usb_disabled": {
        "en": "Disabled (All USB Allowed)", "ru": "Отключено (все USB разрешены)", "es": "Desactivado (todos los USB permitidos)", "de": "Deaktiviert (alle USB erlaubt)",
        "fr": "Désactivé (tous les USB autorisés)", "zh_CN": "已禁用（允许所有USB设备）", "ja": "無効（すべてのUSBを許可）", "it": "Disabilitato (tutti i dispositivi USB consentiti)",
        "pt_BR": "Desativado (todos os USB permitidos)", "tr": "Devre Dışı (Tüm USB'lere İzin Verildi)", "uk": "Вимкнено (усі USB дозволені)", "kk": "Өшірулі (барлық USB рұқсат етілген)", "ar": "معطل (يُسمح بجميع أجهزة USB)"
    },
    "privacy.status_usb_always": {
        "en": "Protected (Always Block New USB)", "ru": "Защищено (всегда блокировать новые USB)", "es": "Protegido (bloquear siempre nuevos USB)", "de": "Geschützt (neue USB immer blockieren)",
        "fr": "Protégé (toujours bloquer les nouveaux USB)", "zh_CN": "受保护（始终阻止新的USB设备）", "ja": "保護（常に新しいUSBをブロック）", "it": "Protetto (blocca sempre nuovi dispositivi USB)",
        "pt_BR": "Protegido (sempre bloquear novos USB)", "tr": "Korumalı (Yeni USB'leri Her Zaman Engelle)", "uk": "Захищено (завжди блокувати нові USB)", "kk": "Қорғалған (жаңа USB-ді әрқашан блоктау)", "ar": "محمي (حظر أجهزة USB الجديدة دائمًا)"
    },
    "privacy.status_usb_lock": {
        "en": "Protected (Block at Lock Screen)", "ru": "Защищено (блокировка на экране блокировки)", "es": "Protegido (bloquear en pantalla bloqueada)", "de": "Geschützt (auf Sperrbildschirm blockieren)",
        "fr": "Protégé (bloquer sur écran verrouillé)", "zh_CN": "受保护（在锁定屏幕上阻止新USB）", "ja": "保護（画面ロック時にブロック）", "it": "Protetto (blocca su schermata di blocco)",
        "pt_BR": "Protegido (bloquear na tela de bloqueio)", "tr": "Korumalı (Kilit Ekranında Engelle)", "uk": "Захищено (блокувати на екрані блокування)", "kk": "Қорғалған (құлыпталған экранда блоктау)", "ar": "محمي (الحظر عند قفل الشاشة)"
    },
    "privacy.std_rdp": {
        "en": "Standard RDP", "ru": "Стандартный RDP", "es": "RDP estándar", "de": "Standard-RDP",
        "fr": "RDP standard", "zh_CN": "标准 RDP", "ja": "標準 RDP", "it": "RDP standard",
        "pt_BR": "RDP Padrão", "tr": "Standart RDP", "uk": "Стандартний RDP", "kk": "Стандартты RDP", "ar": "RDP القياسي"
    },


    # ── Mouse & Keyboard ──
    "mouse.primary_btn": {
        "en": "Primary Button", "ru": "Основная кнопка", "es": "Botón principal", "de": "Primäre Maustaste",
        "fr": "Bouton principal", "zh_CN": "主要按键", "ja": "主ボタン", "it": "Pulsante principale",
        "pt_BR": "Botão Primário", "tr": "Birincil Düğme", "uk": "Основна кнопка", "kk": "Негізгі батырма", "ar": "الزر الأساسي"
    },
    "mouse.left": {
        "en": "Left", "ru": "Левая", "es": "Izquierda", "de": "Links",
        "fr": "Gauche", "zh_CN": "左键", "ja": "左", "it": "Sinistra",
        "pt_BR": "Esquerda", "tr": "Sol", "uk": "Ліва", "kk": "Сол", "ar": "يسار"
    },
    "mouse.right": {
        "en": "Right", "ru": "Правая", "es": "Derecha", "de": "Rechts",
        "fr": "Droite", "zh_CN": "右键", "ja": "右", "it": "Destra",
        "pt_BR": "Direita", "tr": "Sağ", "uk": "Права", "kk": "Оң", "ar": "يمين"
    },
    "mouse.speed": {
        "en": "Pointer Speed", "ru": "Скорость указателя", "es": "Velocidad del puntero", "de": "Zeigergeschwindigkeit",
        "fr": "Vitesse du pointeur", "zh_CN": "指针速度", "ja": "ポインタの速度", "it": "Velocità puntatore",
        "pt_BR": "Velocidade do Ponteiro", "tr": "İşaretçi Hızı", "uk": "Швидкість вказівника", "kk": "Көрсеткіш жылдамдығы", "ar": "سرعة المؤشر"
    },
    "mouse.natural_scroll": {
        "en": "Natural Scrolling", "ru": "Естественная прокрутка", "es": "Desplazamiento natural", "de": "Natürlicher Bildlauf",
        "fr": "Défilement naturel", "zh_CN": "自然滚动", "ja": "ナチュラルなスクロール", "it": "Scorrimento naturale",
        "pt_BR": "Rolagem Natural", "tr": "Doğal Kaydırma", "uk": "Природне прокручування", "kk": "Табиғи айналдыру", "ar": "التمرير الطبيعي"
    },
    "keyboard.repeat_keys": {
        "en": "Repeat Keys", "ru": "Автоповтор клавиш", "es": "Repetición de teclas", "de": "Tastenwiederholung",
        "fr": "Répétition des touches", "zh_CN": "按键重复", "ja": "キーリピート", "it": "Ripetizione tasti",
        "pt_BR": "Repetição de Teclas", "tr": "Tuş Tekrarı", "uk": "Автоповтор клавіш", "kk": "Пернелерді қайталау", "ar": "تكرار المفاتيح"
    },
    "keyboard.delay": {
        "en": "Delay Until Repeat", "ru": "Задержка перед повтором", "es": "Retardo de repetición", "de": "Verzögerung bis Wiederholung",
        "fr": "Délai avant répétition", "zh_CN": "重复前延迟", "ja": "リピート入力までの時間", "it": "Ritardo ripetizione",
        "pt_BR": "Atraso na Repetição", "tr": "Tekrarlama Gecikmesi", "uk": "Затримка перед повторенням", "kk": "Қайталау алдындағы кідіріс", "ar": "التأخير قبل التكرار"
    },
    "keyboard.speed": {
        "en": "Key Repeat Speed", "ru": "Скорость повтора", "es": "Velocidad de repetición", "de": "Wiederholgeschwindigkeit",
        "fr": "Vitesse de répétition", "zh_CN": "按键重复速度", "ja": "キーリピート速度", "it": "Velocità ripetizione",
        "pt_BR": "Velocidade de Repetição", "tr": "Tekrarlama Hızı", "uk": "Швидкість повторення", "kk": "Қайталау жылдамдығы", "ar": "سرعة تكرار المفاتيح"
    },
    "search.placeholder": {
        "en": "Search", "ru": "Поиск", "es": "Buscar", "de": "Suchen",
        "fr": "Rechercher", "zh_CN": "搜索", "ja": "検索", "it": "Cerca",
        "pt_BR": "Buscar", "tr": "Ara", "uk": "Пошук", "kk": "Іздеу", "ar": "بحث"
    },
    "search.no_results": {
        "en": "No Results Found", "ru": "Ничего не найдено", "es": "Sin resultados", "de": "Keine Ergebnisse",
        "fr": "Aucun résultat", "zh_CN": "未找到相关结果", "ja": "結果が見つかりません", "it": "Nessun risultato",
        "pt_BR": "Nenhum Resultado Encontrado", "tr": "Sonuç Bulunamadı", "uk": "Нічого не знайдено", "kk": "Нәтижелер табылмады", "ar": "لم يتم العثور على نتائج"
    },
    "search.no_results_sub": {
        "en": "Check spelling or try a different keyword", "ru": "Проверьте написание или введите другой запрос",
        "es": "Compruebe la ortografía o intente con otra palabra", "de": "Überprüfen Sie die Schreibweise oder versuchen Sie einen anderen Begriff",
        "fr": "Vérifiez l'orthographe ou essayez un autre mot-clé", "zh_CN": "请检查拼写或尝试其他关键词",
        "ja": "スペルを確認するか、別のキーワードをお試しください", "it": "Verifica l'ortografia o prova con un'altra parola",
        "pt_BR": "Verifique a ortografia ou tente outra palavra-chave", "tr": "Yazımı kontrol edin veya başka bir kelime deneyin",
        "uk": "Перевірте написання або спробуйте інше слово", "kk": "Жазылуын тексеріңіз немесе басқа сөзді пайдаланыңыз",
        "ar": "تحقق من الإملاء أو جرب كلمة بحث أخرى"
    },

    # ── Search Index Item & Section Titles (Title Case) ──
    "search.item.theme": {"en": "Theme", "ru": "Тема оформления", "es": "Tema", "de": "Design", "fr": "Thème"},
    "search.item.accent": {"en": "Accent Color", "ru": "Цвет акцента", "es": "Color de acento", "de": "Akzentfarbe", "fr": "Couleur d'accent"},
    "search.item.contrast": {"en": "Increase Contrast", "ru": "Увеличение контраста", "es": "Aumentar contraste", "de": "Kontrast erhöhen", "fr": "Augmenter le contraste"},
    "search.item.workspaces": {"en": "Workspaces & Multitasking", "ru": "Рабочие столы", "es": "Espacios de trabajo", "de": "Arbeitsbereiche", "fr": "Espaces de travail"},
    "search.item.hot_corners": {"en": "Hot Corners", "ru": "Активные углы", "es": "Esquinas activas", "de": "Aktive Ecken", "fr": "Coins actifs"},
    
    "search.item.about": {"en": "About This System", "ru": "О системе", "es": "Acerca de este equipo", "de": "Über dieses System", "fr": "À propos de ce système"},
    "search.item.device_name": {"en": "Device Name", "ru": "Имя устройства", "es": "Nombre del equipo", "de": "Gerätename", "fr": "Nom de l'appareil"},
    "search.item.software_update": {"en": "Software Updates", "ru": "Обновление ПО", "es": "Actualizaciones de software", "de": "Software-Updates", "fr": "Mises à jour logicielles"},
    "search.item.language": {"en": "System Language", "ru": "Язык системы", "es": "Idioma del sistema", "de": "Systemsprache", "fr": "Langue du système"},
    "search.item.airdrop": {"en": "AirDrop & Sharing", "ru": "Общий доступ", "es": "Compartir", "de": "Freigabe", "fr": "Partage"},
    "search.item.startup": {"en": "Startup Items", "ru": "Автозагрузка", "es": "Elementos de inicio", "de": "Startobjekte", "fr": "Ouverture au démarrage"},
    "search.item.browser": {"en": "Default Browser", "ru": "Браузер по умолчанию", "es": "Navegador predeterminado", "de": "Standard-Browser", "fr": "Navigateur par défaut"},
    
    "search.item.resolution": {"en": "Resolution", "ru": "Разрешение экрана", "es": "Resolución", "de": "Auflösung", "fr": "Résolution"},
    "search.item.refresh_rate": {"en": "Refresh Rate", "ru": "Частота обновления", "es": "Frecuencia de actualización", "de": "Bildwiederholrate", "fr": "Fréquence de rafraîchissement"},
    "search.item.scaling": {"en": "Display Scaling", "ru": "Масштабирование", "es": "Escalado", "de": "Skalierung", "fr": "Mise à l'échelle"},
    "search.item.night_shift": {"en": "Night Light", "ru": "Ночной режим", "es": "Luz nocturna", "de": "Nachtmodus", "fr": "Éclairage nocturne"},
    "search.item.arrange": {"en": "Arrange Displays", "ru": "Расположение мониторов", "es": "Organizar pantallas", "de": "Monitore anordnen", "fr": "Disposition des écrans"},
    
    "search.item.volume": {"en": "Output Volume", "ru": "Громкость звука", "es": "Volumen de salida", "de": "Ausgabelautstärke", "fr": "Volume de sortie"},
    "search.item.sound_output": {"en": "Output Device", "ru": "Устройство вывода", "es": "Dispositivo de salida", "de": "Ausgabegerät", "fr": "Périphérique de sortie"},
    "search.item.balance": {"en": "Stereo Balance", "ru": "Баланс звука", "es": "Balance de audio", "de": "Tonbalance", "fr": "Balance audio"},
    "search.item.test_speakers": {"en": "Test Speakers", "ru": "Проверка динамиков", "es": "Probar altavoces", "de": "Lautsprechertest", "fr": "Tester les haut-parleurs"},
    "search.item.effects": {"en": "Sound Effects", "ru": "Звуковые эффекты", "es": "Efectos de sonido", "de": "Toneffekte", "fr": "Effets sonores"},
    
    "search.item.allow_notifications": {"en": "Allow Notifications", "ru": "Разрешить уведомления", "es": "Permitir notificaciones", "de": "Mitteilungen erlauben", "fr": "Autoriser les notifications"},
    "search.item.dnd": {"en": "Do Not Disturb", "ru": "Не беспокоить", "es": "No molestar", "de": "Nicht stören", "fr": "Ne pas déranger"},
    "search.item.lock_screen_notif": {"en": "Lock Screen Notifications", "ru": "Уведомления на экране блокировки", "es": "Notificaciones en pantalla bloqueada", "de": "Mitteilungen im Sperrbildschirm", "fr": "Notifications sur l'écran verrouillé"},
    "search.item.previews": {"en": "Show Previews", "ru": "Показ миниатюр", "es": "Mostrar vistas previas", "de": "Vorschauen anzeigen", "fr": "Afficher les aperçus"},
    "search.item.badges": {"en": "Badge App Icons", "ru": "Наклейки на значках", "es": "Globos en iconos", "de": "Kennzeichen auf App-Symbolen", "fr": "Pastilles sur les icônes"},
    
    "search.item.mouse_speed": {"en": "Tracking Speed", "ru": "Скорость указателя", "es": "Velocidad del cursor", "de": "Zeigergeschwindigkeit", "fr": "Vitesse du curseur"},
    "search.item.natural_scroll": {"en": "Natural Scrolling", "ru": "Естественная прокрутка", "es": "Desplazamiento natural", "de": "Natürlicher Bildlauf", "fr": "Défilement naturel"},
    "search.item.acceleration": {"en": "Pointer Acceleration", "ru": "Ускорение указателя", "es": "Aceleración del puntero", "de": "Zeigerbeschleunigung", "fr": "Accélération du curseur"},
    "search.item.primary_btn": {"en": "Primary Button", "ru": "Основная кнопка", "es": "Botón principal", "de": "Primäre Maustaste", "fr": "Bouton principal"},
    "search.item.double_click": {"en": "Double-Click Speed", "ru": "Скорость двойного щелчка", "es": "Velocidad de doble clic", "de": "Doppelklick-Tempo", "fr": "Vitesse du double-clic"},
    
    "search.item.repeat_rate": {"en": "Key Repeat Rate", "ru": "Скорость повтора клавиш", "es": "Repetición de teclas", "de": "Tastenwiederholung", "fr": "Répétition des touches"},
    "search.item.repeat_delay": {"en": "Delay Until Repeat", "ru": "Задержка до повтора", "es": "Retardo de repetición", "de": "Wiederholungsverzögerung", "fr": "Délai avant répétition"},
    "search.item.backlight": {"en": "Keyboard Backlight", "ru": "Подсветка клавиатуры", "es": "Retroiluminación", "de": "Tastaturbeleuchtung", "fr": "Rétroéclairage"},
    "search.item.input_sources": {"en": "Input Sources", "ru": "Источники ввода", "es": "Fuentes de entrada", "de": "Eingabequellen", "fr": "Sources de saisie"},
    
    "search.item.location": {"en": "Location Services", "ru": "Службы геолокации", "es": "Localización", "de": "Ortungsdienste", "fr": "Services de localisation"},
    "search.item.camera": {"en": "Camera Access", "ru": "Доступ к камере", "es": "Cámara", "de": "Kamera", "fr": "Caméra"},
    "search.item.microphone": {"en": "Microphone Access", "ru": "Доступ к микрофону", "es": "Micrófono", "de": "Mikrofon", "fr": "Microphone"},
    "search.item.screen_lock": {"en": "Screen Lock & Password", "ru": "Блокировка экрана", "es": "Bloqueo de pantalla", "de": "Bildschirmsperre", "fr": "Verrouillage de l'écran"},
    
    "search.item.wifi_power": {"en": "Wi-Fi Power", "ru": "Питание Wi-Fi", "es": "Wi-Fi", "de": "WLAN", "fr": "Wi-Fi"},
    "search.item.wifi_networks": {"en": "Available Wi-Fi Networks", "ru": "Доступные сети Wi-Fi", "es": "Redes disponibles", "de": "Verfügbare Netze", "fr": "Réseaux disponibles"},
    
    "search.item.bt_power": {"en": "Bluetooth Power", "ru": "Питание Bluetooth", "es": "Bluetooth", "de": "Bluetooth", "fr": "Bluetooth"},
    "search.item.bt_devices": {"en": "Paired Devices", "ru": "Подключенные устройства", "es": "Dispositivos vinculados", "de": "Gekoppelte Geräte", "fr": "Appareils jumelés"},
    
    "search.item.ethernet": {"en": "Ethernet & Wired Network", "ru": "Проводная сеть Ethernet", "es": "Red cableada", "de": "Kabelgebundenes Netzwerk", "fr": "Réseau filaire"},
    "search.item.vpn": {"en": "VPN Connections", "ru": "VPN соединения", "es": "Conexiones VPN", "de": "VPN-Verbindungen", "fr": "Connexions VPN"},
    
    "search.item.storage_overview": {"en": "Storage Overview", "ru": "Использование диска", "es": "Almacenamiento", "de": "Speicherplatz", "fr": "Stockage"},
    "search.item.storage_recommendations": {"en": "Storage Recommendations", "ru": "Рекомендации по очистке", "es": "Recomendaciones", "de": "Empfehlungen", "fr": "Recommandations"},
    
    "search.item.power_mode": {"en": "Power Mode", "ru": "Режим питания", "es": "Modo de energía", "de": "Energiemodus", "fr": "Mode d'alimentation"},
    "search.item.screen_sleep": {"en": "Screen Sleep Timeout", "ru": "Отключение экрана", "es": "Apagar pantalla", "de": "Bildschirm ausschalten", "fr": "Éteindre l'écran"},
    "search.item.battery_health": {"en": "Battery Health", "ru": "Состояние аккумулятора", "es": "Salud de la batería", "de": "Batteriezustand", "fr": "État de la batterie"},
    
    "search.item.spotlight_shortcut": {"en": "Echo Search Shortcut", "ru": "Горячая клавиша поиска", "es": "Acceso rápido de búsqueda", "de": "Suchkürzel", "fr": "Raccourci de recherche"},
    "search.item.spotlight_categories": {"en": "Search Categories", "ru": "Категории поиска", "es": "Categorías de búsqueda", "de": "Suchkategorien", "fr": "Catégories de recherche"},
    "search.item.spotlight_preview": {"en": "Preview Panel", "ru": "Панель предпросмотра", "es": "Panel de vista previa", "de": "Vorschaufenster", "fr": "Panneau d'aperçu"},

    # ── Section Breadcrumbs ──
    "search.sec.appearance": {"en": "Appearance", "ru": "Внешний вид", "es": "Aspecto", "de": "Erscheinungsbild", "fr": "Apparence"},
    "search.sec.theme": {"en": "Theme", "ru": "Тема", "es": "Tema", "de": "Design", "fr": "Thème"},
    "search.sec.general": {"en": "General", "ru": "Основные", "es": "General", "de": "Allgemein", "fr": "Général"},
    "search.sec.display": {"en": "Display", "ru": "Дисплеи", "es": "Pantallas", "de": "Monitore", "fr": "Écrans"},
    "search.sec.sound": {"en": "Sound", "ru": "Звук", "es": "Sonido", "de": "Ton", "fr": "Son"},
    "search.sec.notifications": {"en": "Notifications", "ru": "Уведомления", "es": "Notificaciones", "de": "Mitteilungen", "fr": "Notifications"},
    "search.sec.mouse": {"en": "Mouse", "ru": "Мышь", "es": "Ratón", "de": "Maus", "fr": "Souris"},
    "search.sec.pointer": {"en": "Pointer", "ru": "Указатель", "es": "Puntero", "de": "Zeiger", "fr": "Pointeur"},
    "search.sec.buttons": {"en": "Buttons", "ru": "Кнопки", "es": "Botones", "de": "Tasten", "fr": "Boutons"},
    "search.sec.keyboard": {"en": "Keyboard", "ru": "Клавиатура", "es": "Teclado", "de": "Tastatur", "fr": "Clavier"},
    "search.sec.privacy": {"en": "Privacy & Security", "ru": "Конфиденциальность", "es": "Privacidad", "de": "Datenschutz", "fr": "Confidentialité"},
    "search.sec.wifi": {"en": "Wi-Fi", "ru": "Wi-Fi", "es": "Wi-Fi", "de": "WLAN", "fr": "Wi-Fi"},
    "search.sec.bluetooth": {"en": "Bluetooth", "ru": "Bluetooth", "es": "Bluetooth", "de": "Bluetooth", "fr": "Bluetooth"},
    "search.sec.network": {"en": "Network", "ru": "Сеть", "es": "Red", "de": "Netzwerk", "fr": "Réseau"},
    "search.sec.storage": {"en": "Storage", "ru": "Хранилище", "es": "Almacenamiento", "de": "Speicher", "fr": "Stockage"},
    "search.sec.power": {"en": "Power", "ru": "Питание", "es": "Batería", "de": "Batterie", "fr": "Batterie"},
    "search.sec.spotlight": {"en": "Echo Search", "ru": "Echo Search", "es": "Echo Search", "de": "Echo Search", "fr": "Echo Search"},

    # ── Installer Strings ──
    "installer.welcome_title": {
        "en": "Echo Settings", "ru": "Echo Settings", "es": "Echo Settings", "de": "Echo Settings",
        "fr": "Echo Settings", "zh_CN": "Echo Settings", "ja": "Echo Settings", "it": "Echo Settings",
        "pt_BR": "Echo Settings", "tr": "Echo Settings", "uk": "Echo Settings", "kk": "Echo Settings", "ar": "Echo Settings"
    },
    "installer.hello": {
        "en": "Welcome", "ru": "Добро пожаловать", "es": "Bienvenido", "de": "Willkommen",
        "fr": "Bienvenue", "zh_CN": "欢迎使用", "ja": "ようこそ", "it": "Benvenuto",
        "pt_BR": "Bem-vindo", "tr": "Hoş geldiniz", "uk": "Ласкаво просимо", "kk": "Қош келдіңіз", "ar": "مرحباً بك"
    },
    "installer.get_started": {
        "en": "Get Started ›", "ru": "Начать настройку ›", "es": "Comenzar ›", "de": "Loslegen ›",
        "fr": "Démarrer ›", "zh_CN": "开始设置 ›", "ja": "設定を開始 ›", "it": "Inizia ›",
        "pt_BR": "Começar ›", "tr": "Başlayın ›", "uk": "Почати налаштування ›", "kk": "Баптауды бастау ›", "ar": "البدء ›"
    },
    "installer.welcome_hint": {
        "en": "Experience the unified, high-performance control center designed for Linux.",
        "ru": "Познакомьтесь с современным центром управления нового поколения для Linux.",
        "es": "Descubra el centro de control unificado y de alto rendimiento para Linux.",
        "de": "Erleben Sie die moderne, leistungsstarke Systemsteuerung für Linux.",
        "fr": "Découvrez le centre de contrôle moderne et haute performance pour Linux.",
        "zh_CN": "体验专为 Linux 打造的高性能现代化系统控制中心。",
        "ja": "Linux のために設計された高性能で美しいシステムコントロールセンター。",
        "it": "Scopri il centro di controllo moderno e ad alte prestazioni per Linux.",
        "pt_BR": "Experimente o centro de controle moderno e de alto desempenho para Linux.",
        "tr": "Linux için tasarlanmış yüksek performanslı modern kontrol merkezini keşfedin.",
        "uk": "Відкрийте для себе сучасний високопродуктивний центр керування для Linux.",
        "kk": "Linux үшін жасалған заманауи жоғары өнімді басқару орталығын көріңіз.",
        "ar": "استمتع بتجربة مركز التحكم الموحد وعالي الأداء المصمم لنظام Linux."
    },
    "installer.select_lang_title": {
        "en": "Select Language", "ru": "Выберите язык", "es": "Seleccionar idioma", "de": "Sprache auswählen",
        "fr": "Sélectionner la langue", "zh_CN": "选择语言", "ja": "言語を選択", "it": "Seleziona lingua",
        "pt_BR": "Selecionar Idioma", "tr": "Dil Seçin", "uk": "Оберіть мову", "kk": "Тілді таңдаңыз", "ar": "اختر اللغة"
    },
    "installer.select_lang_sub": {
        "en": "Choose your preferred language for Echo Settings and the setup assistant.",
        "ru": "Выберите язык для интерфейса Echo Settings и мастера первоначальной настройки.",
        "es": "Elija su idioma preferido para Echo Settings y el asistente de configuración.",
        "de": "Wählen Sie Ihre bevorzugte Sprache für Echo Settings und den Einrichtungsassistenten.",
        "fr": "Choisissez votre langue préférée pour Echo Settings et l'assistant de configuration.",
        "zh_CN": "为 Echo Settings 和安装向导选择首选界面语言。",
        "ja": "Echo Settings 以及セットアップアシスタントの言語を選択してください。",
        "it": "Scegli la tua lingua preferita per Echo Settings e l'assistente di installazione.",
        "pt_BR": "Escolha o idioma de sua preferência para o Echo Settings e o assistente.",
        "tr": "Echo Settings ve kurulum yardımcısı için tercih ettiğiniz dili seçin.",
        "uk": "Оберіть бажану мову для Echo Settings та майстра встановлення.",
        "kk": "Echo Settings және орнату шебері үшін қалаған тілді таңдаңыз.",
        "ar": "اختر لغتك المفضلة لـ Echo Settings ومساعد الإعداد."
    },
    "installer.search_lang": {
        "en": "Search language...", "ru": "Поиск языка...", "es": "Buscar idioma...", "de": "Sprache suchen...",
        "fr": "Rechercher une langue...", "zh_CN": "搜索语言...", "ja": "言語を検索...", "it": "Cerca lingua...",
        "pt_BR": "Pesquisar idioma...", "tr": "Dil ara...", "uk": "Пошук мови...", "kk": "Тілді іздеу...", "ar": "البحث عن لغة..."
    },
    "installer.tip_title": {
        "en": "Language Tip", "ru": "Совет по языку", "es": "Consejo de idioma", "de": "Sprachtipp",
        "fr": "Astuce de langue", "zh_CN": "语言提示", "ja": "言語のヒント", "it": "Suggerimento lingua",
        "pt_BR": "Dica de Idioma", "tr": "Dil İpucu", "uk": "Порада щодо мови", "kk": "Тіл бойынша кеңес", "ar": "تلميح اللغة"
    },
    "installer.tip_desc": {
        "en": "You can easily change the interface language anytime in Echo Settings.",
        "ru": "Вы сможете легко изменить язык интерфейса в любой момент в настройках.",
        "es": "Puede cambiar fácilmente el idioma de la interfaz en cualquier momento en Echo Settings.",
        "de": "Sie können die Sprache der Benutzeroberfläche jederzeit in Echo Settings ändern.",
        "fr": "Vous pouvez facilement modifier la langue de l'interface à tout moment dans Echo Settings.",
        "zh_CN": "您可以随时在 Echo Settings 中轻松更改界面语言。",
        "ja": "Echo Settings の設定からいつでもインターフェース言語を簡単に変更できます。",
        "it": "Puoi modificare facilmente la lingua dell'interfaccia in qualsiasi momento in Echo Settings.",
        "pt_BR": "Você pode alterar facilmente o idioma da interface a qualquer momento no Echo Settings.",
        "tr": "Arayüz dilini dilediğiniz zaman Echo Settings ayarlarından kolayca değiştirebilirsiniz.",
        "uk": "Ви зможете легко змінити мову інтерфейсу в будь-який момент у налаштуваннях.",
        "kk": "Интерфейс тілін кез келген уақытта Echo Settings баптауларынан өзгерте аласыз.",
        "ar": "يمكنك بسهولة تغيير لغة الواجهة في أي وقت من إعدادات Echo Settings."
    },
    "installer.scope_tip_title": {
        "en": "Access Permissions", "ru": "Права доступа", "es": "Permisos", "de": "Berechtigungen",
        "fr": "Permissions", "zh_CN": "权限说明", "ja": "権限について", "it": "Permessi",
        "pt_BR": "Permissões", "tr": "İzinler", "uk": "Права доступу", "kk": "Қолжетімділік", "ar": "الأذونات"
    },
    "installer.scope_tip_desc": {
        "en": "User installation is recommended and does not require root privileges.",
        "ru": "Установка для текущего пользователя рекомендуется и не требует прав root.",
        "es": "La instalación de usuario es recomendada y no requiere permisos de root.",
        "de": "Die Benutzerinstallation wird empfohlen und erfordert keine Root-Rechte.",
        "fr": "L'installation utilisateur est recommandée et ne nécessite pas de privilèges root.",
        "zh_CN": "推荐当前用户安装，无需 root 管理员权限。",
        "ja": "ユーザーインストールをお勧めします。root 権限は不要です。",
        "it": "L'installazione per utente è consigliata e non richiede permessi di root.",
        "pt_BR": "A instalação de usuário é recomendada e não requer privilégios de root.",
        "tr": "Kullanıcı kurulumu önerilir ve root yetkisi gerektirmez.",
        "uk": "Встановлення для поточного користувача є рекомендованим і не вимагає прав root.",
        "kk": "Ағымдағы пайдаланушы үшін орнату ұсынылады және root құқықтарын талап етпейді.",
        "ar": "يوصى بالتثبيت للمستخدم الحالي ولا يتطلب امتيازات root."
    },
    "installer.space_req": {
        "en": "Required", "ru": "Требуется", "es": "Requerido", "de": "Erforderlich",
        "fr": "Requis", "zh_CN": "所需空间", "ja": "必要容量", "it": "Richiesto",
        "pt_BR": "Necessário", "tr": "Gerekli", "uk": "Потрібно", "kk": "Қажетті", "ar": "المطلوب"
    },
    "installer.space_avail": {
        "en": "Available", "ru": "Доступно", "es": "Disponible", "de": "Verfügbar",
        "fr": "Disponible", "zh_CN": "可用空间", "ja": "利用可能", "it": "Disponibile",
        "pt_BR": "Disponível", "tr": "Kullanılabilir", "uk": "Доступно", "kk": "Қолжетімді", "ar": "المتاح"
    },

    "installer.welcome_desc": {
        "en": "Welcome to the official Echo Settings installer.\n\nEcho Settings delivers a unified, high-performance control center with native GNOME integration, Liquid Glass design, customizable themes, multitasking workspaces, and privacy controls.",
        "ru": "Добро пожаловать в официальный установщик Echo Settings.\n\nEcho Settings предоставляет единый высокопроизводительный центр управления системой с нативной интеграцией в GNOME, дизайном Liquid Glass, настраиваемыми темами, виртуальными рабочими столами и расширенной безопасностью.",
        "es": "Bienvenido al instalador oficial de Echo Settings.\n\nEcho Settings ofrece un centro de control unificado y de alto rendimiento con integración nativa en GNOME, diseño Liquid Glass, temas personalizables, escritorios múltiples y controles de privacidad.",
        "de": "Willkommen beim offiziellen Echo Settings-Installationsprogramm.\n\nEcho Settings bietet eine einheitliche, leistungsstarke Systemsteuerung mit nativer GNOME-Integration, Liquid Glass-Design, anpassbaren Designs, Multitasking-Arbeitsbereichen und Datenschutzkontrollen.",
        "fr": "Bienvenue dans le programme d'installation officiel d'Echo Settings.\n\nEcho Settings offre un centre de contrôle système unifié et performant avec intégration native de GNOME, design Liquid Glass, thèmes personnalisables, espaces de travail multitâches et sécurité.",
        "zh_CN": "欢迎使用 Echo Settings 官方安装程序。\n\nEcho Settings 提供统一、高性能的系统控制中心，深度集成 GNOME 环境，采用 Liquid Glass 现代设计，支持个性化主题、多任务工作区和高级隐私安全控制。",
        "ja": "Echo Settings 公式インストーラーへようこそ。\n\nEcho Settings は、ネイティブ GNOME 統合、Liquid Glass デザイン、カスタマイズ可能なテーマ、マルチタスクワークスペース、プライバシー保護を備えた統合システムコントロールセンターを提供します。",
        "it": "Benvenuto nell'installer ufficiale di Echo Settings.\n\nEcho Settings offre un centro de controllo unificato e ad alte prestazioni con integrazione nativa in GNOME, design Liquid Glass, temi personalizzabili, spazi di lavoro multitasking e controlli della privacy.",
        "pt_BR": "Bem-vindo ao instalador oficial do Echo Settings.\n\nO Echo Settings oferece um centro de controle unificado e de alto desempenho com integração nativa ao GNOME, design Liquid Glass, temas personalizáveis, áreas de trabalho multitarefa e privacidade.",
        "tr": "Resmi Echo Settings yükleyicisine hoş geldiniz.\n\nEcho Settings; yerel GNOME entegrasyonu, Liquid Glass tasarımı, özelleştirilebilir temalar, çoklu görev çalışma alanları ve gizlilik kontrolleri sunan bir sistem kontrol merkezidir.",
        "kk": "Echo Settings ресми орнатушысына қош келдіңіз.\n\nEcho Settings GNOME-мен біріктірілген, Liquid Glass дизайнымен жасалған, көптапсырмалы жұмыс үстелдері мен қауіпсіздікті басқаруға арналған бірыңғай жүйелік басқару орталығын ұсынады.",
        "ar": "مرحبًا بك في برنامج تثبيت Echo Settings الرسمي.\n\nيوفر Echo Settings مركز تحكم موحد وعالي الأداء للنظام مع تكامل أصلي مع GNOME وتصميم Liquid Glass ومساحات عمل متعددة المهام وعناصر تحكم في الخصوصية."
    },
    "installer.edition_badge": {
        "en": "Echo Settings • Version {version}",
        "ru": "Echo Settings • Версия {version}",
        "es": "Echo Settings • Versión {version}",
        "de": "Echo Settings • Version {version}",
        "fr": "Echo Settings • Version {version}",
        "zh_CN": "Echo Settings • 版本 {version}",
        "ja": "Echo Settings • バージョン {version}",
        "it": "Echo Settings • Versione {version}",
        "pt_BR": "Echo Settings • Versão {version}",
        "tr": "Echo Settings • Sürüm {version}",
        "uk": "Echo Settings • Версія {version}",
        "kk": "Echo Settings • Нұсқасы {version}",
        "ar": "Echo Settings • الإصدار {version}"
    },
    "installer.continue": {

        "en": "Continue ›", "ru": "Продолжить ›", "es": "Continuar ›", "de": "Fortfahren ›",
        "fr": "Continuer ›", "zh_CN": "继续 ›", "ja": "続ける ›", "it": "Continua ›",
        "pt_BR": "Continuar ›", "tr": "Devam ›", "uk": "Продовжити ›", "kk": "Жалғастыру ›", "ar": "متابعة ›"
    },
    "installer.back": {
        "en": "‹ Back", "ru": "‹ Назад", "es": "‹ Atrás", "de": "‹ Zurück",
        "fr": "‹ Retour", "zh_CN": "‹ 返回", "ja": "‹ 戻る", "it": "‹ Indietro",
        "pt_BR": "‹ Voltar", "tr": "‹ Geri", "uk": "‹ Назад", "kk": "‹ Артқа", "ar": "‹ رجوع"
    },
    "installer.exit": {
        "en": "Exit", "ru": "Выход", "es": "Salir", "de": "Beenden",
        "fr": "Quitter", "zh_CN": "退出", "ja": "終了", "it": "Esci",
        "pt_BR": "Sair", "tr": "Çıkış", "uk": "Вихід", "kk": "Шығу", "ar": "خروج"
    },
    "installer.system_check_title": {
        "en": "System Compatibility Check", "ru": "Проверка совместимости системы", "es": "Comprobación de compatibilidad", "de": "Systemkompatibilitätsprüfung",
        "fr": "Vérification de la compatibilité système", "zh_CN": "系统兼容性检查", "ja": "システム互換性チェック", "it": "Controllo compatibilità del sistema",
        "pt_BR": "Verificação de Compatibilidade", "tr": "Sistem Uyumluluk Kontrolü", "uk": "Перевірка сумісності системи", "kk": "Жүйенің үйлесімділігін тексеру", "ar": "فحص توافق النظام"
    },
    "installer.system_check_sub": {
        "en": "Validating environment, desktop integration, and system services.",
        "ru": "Проверка операционной системы, рабочего окружения и системных сервисов.",
        "es": "Validando entorno, integración de escritorio y servicios del sistema.",
        "de": "Überprüfung von Umgebung, Desktop-Integration und Systemdiensten.",
        "fr": "Validation de l'environnement, de l'intégration et des services système.",
        "zh_CN": "正在验证操作系统、桌面集成和系统服务。",
        "ja": "環境、デスクトップ統合、およびシステムサービスを検証しています。",
        "it": "Verifica dell'ambiente, dell'integrazione desktop e dei servizi di sistema.",
        "pt_BR": "Validando ambiente, integração de desktop e serviços do sistema.",
        "tr": "Ortam, masaüstü entegrasyonu ve sistem servisleri doğrulanıyor.",
        "uk": "Перевірка операційної системи, робочого середовища та сервісів.",
        "kk": "Операциялық жүйе, жұмыс үстелі және жүйелік қызметтер тексерілуде.",
        "ar": "جارٍ التحقق من البيئة وتكامل سطح المكتب وخدمات النظام."
    },
    "installer.scope_title": {
        "en": "Installation Target", "ru": "Выбор места установки", "es": "Destino de instalación", "de": "Installationsziel",
        "fr": "Cible d'installation", "zh_CN": "安装目标", "ja": "インストール先", "it": "Destinazione di installazione",
        "pt_BR": "Destino da Instalação", "tr": "Yükleme Hedefi", "uk": "Вибір місця встановлення", "kk": "Орнату орны", "ar": "هدف التثبيت"
    },
    "installer.scope_sub": {
        "en": "Select installation scope and destination.",
        "ru": "Выберите область установки и каталог назначения.",
        "es": "Seleccione el alcance y destino de la instalación.",
        "de": "Wählen Sie den Installationsumfang und das Zielverzeichnis.",
        "fr": "Sélectionnez la portée et le répertoire d'installation.",
        "zh_CN": "选择安装范围和目标位置。",
        "ja": "インストールの範囲とインストール先を選択してください。",
        "it": "Seleziona l'ambito di installazione e la destinazione.",
        "pt_BR": "Selecione o escopo e o diretório de destino da instalação.",
        "tr": "Yükleme kapsamını ve hedef dizini seçin.",
        "uk": "Оберіть область встановлення та каталог призначення.",
        "kk": "Орнату ауқымы мен мақсатты каталогты таңдаңыз.",
        "ar": "حدد نطاق التثبيت ودليل الوجهة."
    },
    "installer.scope_user": {
        "en": "Current User", "ru": "Текущий пользователь", "es": "Usuario actual", "de": "Aktueller Benutzer",
        "fr": "Utilisateur actuel", "zh_CN": "当前用户", "ja": "現在のユーザー", "it": "Utente corrente",
        "pt_BR": "Usuário Atual", "tr": "Geçerli Kullanıcı", "uk": "Поточний користувач", "kk": "Ағымдағы пайдаланушы", "ar": "المستخدم الحالي"
    },

    "installer.scope_user_desc": {
        "en": "Installs Echo Settings for your account only. Does not require administrator permissions.",
        "ru": "Устанавливает Echo Settings только для вашей учётной записи. Не требует прав администратора.",
        "es": "Instala Echo Settings solo para su cuenta. No requiere permisos de administrador.",
        "de": "Installiert Echo Settings nur für Ihr Konto. Erfordert keine Administratorrechte.",
        "fr": "Installe Echo Settings uniquement pour votre compte. Ne nécessite aucun droit administrateur.",
        "zh_CN": "仅为当前登录用户安装 Echo Settings。不需要管理员权限。",
        "ja": "現在のアカウントにのみ Echo Settings をインストールします。管理者権限は不要です。",
        "it": "Installa Echo Settings solo per il tuo account. Non richiede privilegi di amministratore.",
        "pt_BR": "Instala o Echo Settings apenas para sua conta. Não requer permissões de administrador.",
        "tr": "Echo Settings'i yalnızca sizin hesabınız için yükler. Yönetici izinleri gerektirmez.",
        "uk": "Встановлює Echo Settings лише для вашого облікового запису. Не потребує прав адміністратора.",
        "kk": "Echo Settings тек сіздің тіркелгіңізге орнатылады. Әкімші құқықтарын қажет етпейді.",
        "ar": "يثبت Echo Settings لحسابك فقط. لا يتطلب صلاحيات المسؤول."
    },
    "installer.scope_system": {
        "en": "All System Users", "ru": "Для всей системы", "es": "Para todo el sistema", "de": "Systemweit",
        "fr": "Pour tout le système", "zh_CN": "全系统所有用户", "ja": "システム全体", "it": "A livello di sistema",
        "pt_BR": "Para Todo o Sistema", "tr": "Tüm Sistem İçin", "uk": "Для всієї системи", "kk": "Бүкіл жүйе үшін", "ar": "لكل النظام"
    },

    "installer.scope_system_desc": {
        "en": "Installs for all users on this system. Requires administrator (polkit) privileges.",
        "ru": "Устанавливает приложение для всех пользователей. Требует права администратора (Polkit).",
        "es": "Instala para todos los usuarios en este sistema. Requiere privilegios de administrador (polkit).",
        "de": "Wird für alle Benutzer auf diesem System installiert. Erfordert Administratorrechte (polkit).",
        "fr": "Installe pour tous les utilisateurs du système. Nécessite des privilèges administrateur (polkit).",
        "zh_CN": "为系统上的所有用户安装。需要管理员权限（Polkit）。",
        "ja": "システム上のすべてのユーザー向けにインストールします。管理者権限（polkit）が必要です。",
        "it": "Installa per tutti gli utenti su questo sistema. Richiede privilegi di amministratore (polkit).",
        "pt_BR": "Instala para todos os usuários neste sistema. Requer privilégios de administrador (polkit).",
        "tr": "Bu sistemdeki tüm kullanıcılar için yükler. Yönetici izinleri (polkit) gerektirir.",
        "uk": "Встановлює застосунок для всіх користувачів. Потребує прав адміністратора (Polkit).",
        "kk": "Қолданбаны барлық пайдаланушылар үшін орнатады. Әкімші құқықтарын талап етеді (Polkit).",
        "ar": "التثبيت لجميع المستخدمين على هذا النظام. يتطلب امتيازات المسؤول (polkit)."
    },
    "installer.check_tip_title": {
        "en": "Hardware & OS", "ru": "Оборудование и ОС", "es": "Hardware y SO", "de": "Hardware & Betriebssystem",
        "fr": "Matériel & OS", "zh_CN": "硬件与操作系统", "ja": "ハードウェアとOS", "it": "Hardware e SO",
        "pt_BR": "Hardware e SO", "tr": "Donanım ve İşletim Sistemi", "uk": "Обладнання та ОС", "kk": "Жабдық және ОЖ", "ar": "العتاد ونظام التشغيل"
    },
    "installer.check_tip_desc": {
        "en": "All core GNOME, Python, and system services are validated.",
        "ru": "Все требования GNOME, Python и сервисы проверяются автоматически.",
        "es": "Se validan todos los servicios centrales de GNOME, Python y del sistema.",
        "de": "Alle Kern-GNOME-, Python- und Systemdienste werden überprüft.",
        "fr": "Tous les services centraux GNOME, Python et système sont validés.",
        "zh_CN": "自动验证 GNOME、Python 和系统核心服务的兼容性。",
        "ja": "すべての GNOME、Python、およびシステムサービスが検証されます。",
        "it": "Tutti i servizi principali di GNOME, Python e di sistema sono convalidati.",
        "pt_BR": "Todos os serviços essenciais do GNOME, Python e do sistema são validados.",
        "tr": "Tüm temel GNOME, Python ve sistem servisleri doğrulanır.",
        "uk": "Усі вимоги GNOME, Python та системні сервіси перевіряються автоматично.",
        "kk": "GNOME, Python және жүйелік қызметтердің барлық талаптары тексеріледі.",
        "ar": "يتم التحقق من جميع خدمات GNOME وPython والنظام الأساسية تلقائيًا."
    },
    "installer.check_all_passed": {
        "en": "All system compatibility checks passed.", "ru": "Все системные проверки успешно пройдены.",
        "es": "Todas las comprobaciones del sistema se superaron.", "de": "Alle Systemkompatibilitätsprüfungen bestanden.",
        "fr": "Toutes les vérifications du système ont réussi.", "zh_CN": "所有系统兼容性检查均已通过。",
        "ja": "すべてのシステム互換性チェックに合格しました。", "it": "Tutti i controlli di compatibilità sono stati superati.",
        "pt_BR": "Todas as verificações do sistema foram aprovadas.", "tr": "Tüm sistem uyumluluk kontrolleri geçti.",
        "uk": "Усі системні перевірки успішно пройдено.", "kk": "Барлық жүйелік тексерулер сәтті өтті.", "ar": "اجتازت جميع فحوصات توافق النظام."
    },
    "installer.check_warn_notice": {
        "en": "Optional warnings detected. Installation can proceed.", "ru": "Обнаружены предупреждения. Установка возможна.",
        "es": "Advertencias opcionales detectadas. La instalación puede continuar.", "de": "Optionale Warnungen erkannt. Die Installation kann fortgesetzt werden.",
        "fr": "Avertissements facultatifs détectés. L'installation peut continuer.", "zh_CN": "检测到可选警告，可以继续安装。",
        "ja": "オプションの警告が検出されました。インストールを続行できます。", "it": "Rilevati avvisi facoltativi. L'installazione può continuare.",
        "pt_BR": "Avisos opcionais detectados. A instalação pode prosseguir.", "tr": "İsteğe bağlı uyarılar algılandı. Yüklemeye devam edilebilir.",
        "uk": "Виявлено попередження. Встановлення можливе.", "kk": "Ескертулер табылды. Орнатуды жалғастыруға болады.", "ar": "تم اكتشاف تحذيرات اختيارية. يمكن متابعة التثبيت."
    },
    "installer.check_fail_notice": {
        "en": "Required dependencies missing. Please resolve to continue.", "ru": "Отсутствуют обязательные зависимости. Устраните для продолжения.",
        "es": "Faltan dependencias requeridas. Resuélvalas para continuar.", "de": "Erforderliche Abhängigkeiten fehlen. Bitte beheben Sie diese.",
        "fr": "Dépendances requises manquantes. Veuillez les résoudre.", "zh_CN": "缺少必需的依赖项，请解决后继续。",
        "ja": "必要な依存関係が不足しています。解決してから続行してください。", "it": "Dipendenze richieste mancanti. Risolvile per continuare.",
        "pt_BR": "Dependências necessárias ausentes. Resolva para continuar.", "tr": "Gerekli bağımlılıklar eksik. Devam etmek için giderin.",
        "uk": "Відсутні обов'язкові залежності. Усуньте їх для продовження.", "kk": "Міндетті тәуелділіктер жоқ. Жалғастыру үшін түзетіңіз.", "ar": "تبعيات مطلوبة مفقودة. يرجى حلها للمتابعة."
    },
    "installer.recheck": {
        "en": "Recheck", "ru": "Повторить", "es": "Recomprobar", "de": "Erneut prüfen",
        "fr": "Revérifier", "zh_CN": "重新检查", "ja": "再チェック", "it": "Ricontrolla",
        "pt_BR": "Reverificar", "tr": "Tekrar Kontrol Et", "uk": "Повторити", "kk": "Қайта тексеру", "ar": "إعادة الفحص"
    },
    "installer.opt_autostart": {
        "en": "Launch Echo Settings at system startup", "ru": "Автозапуск при входе в систему",
        "es": "Iniciar Echo Settings al iniciar el sistema", "de": "Echo Settings beim Systemstart ausführen",
        "fr": "Lancer Echo Settings au démarrage du système", "zh_CN": "开机自动启动 Echo Settings",
        "ja": "システム起動時に Echo Settings を起動する", "it": "Avvia Echo Settings all'avvio del sistema",
        "pt_BR": "Iniciar o Echo Settings na inicialização do sistema", "tr": "Sistem başlangıcında Echo Settings'i başlat",
        "uk": "Автозапуск під час входу в систему", "kk": "Жүйе іске қосылғанда автоіске қосу", "ar": "تشغيل Echo Settings عند بدء تشغيل النظام"
    },

    "installer.opt_desktop_icon": {
        "en": "Create Desktop shortcut", "ru": "Создать ярлык на Рабочем столе",
        "es": "Crear acceso directo en el escritorio", "de": "Desktop-Verknüpfung erstellen",
        "fr": "Créer un raccourci sur le bureau", "zh_CN": "创建桌面快捷方式",
        "ja": "デスクトップショートカットを作成する", "it": "Crea scorciatoia sul desktop",
        "pt_BR": "Criar atalho na Área de Trabalho", "tr": "Masaüstü kısayolu oluştur",
        "uk": "Створити ярлик на Робочому столі", "kk": "Жұмыс үстелінде таңбаша жасау", "ar": "إنشاء اختصار على سطح المكتب"
    },
    "installer.stage_prep": {
        "en": "Preparing", "ru": "Подготовка", "es": "Preparando", "de": "Vorbereiten",
        "fr": "Préparation", "zh_CN": "准备就绪", "ja": "準備中", "it": "Preparazione",
        "pt_BR": "Preparando", "tr": "Hazırlanıyor", "uk": "Підготовка", "kk": "Дайындық", "ar": "التحضير"
    },
    "installer.stage_core": {
        "en": "Core Assets", "ru": "Ресурсы", "es": "Recursos", "de": "Kern-Assets",
        "fr": "Ressources", "zh_CN": "核心资源", "ja": "アセット", "it": "Risorse",
        "pt_BR": "Recursos", "tr": "Kaynaklar", "uk": "Ресурси", "kk": "Ресурстар", "ar": "الموارد"
    },
    "installer.stage_runtime": {
        "en": "Qt6 Runtime", "ru": "Среда Qt6", "es": "Entorno Qt6", "de": "Qt6-Laufzeit",
        "fr": "Moteur Qt6", "zh_CN": "Qt6 运行库", "ja": "Qt6 ランタイム", "it": "Runtime Qt6",
        "pt_BR": "Runtime Qt6", "tr": "Qt6 Çalışma Zamanı", "uk": "Середовище Qt6", "kk": "Qt6 ортасы", "ar": "بيئة تشغيل Qt6"
    },
    "installer.stage_config": {
        "en": "System Links", "ru": "Настройка", "es": "Configuración", "de": "Systemlinks",
        "fr": "Configuration", "zh_CN": "系统配置", "ja": "システム設定", "it": "Configurazione",
        "pt_BR": "Configuração", "tr": "Yapılandırma", "uk": "Налаштування", "kk": "Баптау", "ar": "إعدادات النظام"
    },
    "installer.stage_final": {
        "en": "Integration", "ru": "Интеграция", "es": "Integración", "de": "Integration",
        "fr": "Intégration", "zh_CN": "系统集成", "ja": "デスクトップ統合", "it": "Integrazione",
        "pt_BR": "Integração", "tr": "Entegrasyon", "uk": "Інтеграція", "kk": "Интеграция", "ar": "التكامل"
    },
    "installer.complete_item1": {
        "en": "Registered in GNOME App Grid and Applications Menu",
        "ru": "Зарегистрировано в меню приложений GNOME",
        "es": "Registrado en la cuadrícula de aplicaciones de GNOME",
        "de": "Im GNOME-Anwendungsmenü registriert",
        "fr": "Enregistré dans le menu d'applications GNOME",
        "zh_CN": "已在 GNOME 应用程序菜单中成功注册",
        "ja": "GNOME アプリケーショングリッドに登録されました",
        "it": "Registrato nel menu delle applicazioni GNOME",
        "pt_BR": "Registrado no menu de aplicativos do GNOME",
        "tr": "GNOME Uygulama Menüsüne kaydedildi",
        "uk": "Зареєстровано в меню застосунків GNOME",
        "kk": "GNOME қолданбалар мәзірінде тіркелді",
        "ar": "تم التسجيل في قائمة تطبيقات GNOME"
    },
    "installer.complete_item2": {
        "en": "Terminal CLI command 'echo-settings' available",
        "ru": "Доступна команда терминала 'echo-settings'",
        "es": "Comando de terminal 'echo-settings' disponible",
        "de": "Terminalbefehl 'echo-settings' verfügbar",
        "fr": "Commande de terminal 'echo-settings' disponible",
        "zh_CN": "终端命令 'echo-settings' 已就绪",
        "ja": "ターミナルコマンド 'echo-settings' が利用可能です",
        "it": "Comando del terminale 'echo-settings' disponibile",
        "pt_BR": "Comando de terminal 'echo-settings' disponível",
        "tr": "'echo-settings' terminal komutu kullanılabilir",
        "uk": "Доступна команда терміналу 'echo-settings'",
        "kk": "'echo-settings' терминал командасы қолжетімді",
        "ar": "أمر الطرفية 'echo-settings' متاح الآن"
    },
    "installer.complete_item3": {
        "en": "Isolated Python 3 & Qt6 runtime fully configured",
        "ru": "Автономная среда Python 3 и Qt6 настроена",
        "es": "Entorno aislado de Python 3 y Qt6 configurado",
        "de": "Isolierte Python 3- und Qt6-Laufzeitumgebung konfiguriert",
        "fr": "Environnement isolé Python 3 et Qt6 configuré",
        "zh_CN": "独立的 Python 3 和 Qt6 运行环境已就绪",
        "ja": "独立した Python 3 および Qt6 ランタイムが構成されました",
        "it": "Ambiente isolato Python 3 e Qt6 configurato",
        "pt_BR": "Ambiente isolado do Python 3 e Qt6 configurado",
        "tr": "İzole Python 3 ve Qt6 çalışma zamanı yapılandırıldı",
        "uk": "Автономне середовище Python 3 та Qt6 налаштовано",
        "kk": "Оқшауланған Python 3 және Qt6 ортасы бапталды",
        "ar": "تم تكوين بيئة تشغيل Python 3 وQt6 المعزولة بالكامل"
    },
    "installer.welcome_item1": {
        "en": "All system components and desktop preferences are configured",
        "ru": "Все системные компоненты и параметры рабочего стола настроены",
        "es": "Todos los componentes del sistema y preferencias están configurados",
        "de": "Alle Systemkomponenten und Desktopeinstellungen sind konfiguriert",
        "fr": "Tous les composants système et préférences sont configurés",
        "zh_CN": "所有系统组件和桌面偏好设置均已配置完成",
        "ja": "すべてのシステムコンポーネントと環境設定が構成されました",
        "it": "Tutti i componenti di sistema e le preferenze sono configurati",
        "pt_BR": "Todos os componentes do sistema e preferências estão configurados",
        "tr": "Tüm sistem bileşenleri ve masaüstü tercihleri yapılandırıldı",
        "uk": "Усі системні компоненти та налаштування налаштовані",
        "kk": "Барлық жүйелік компоненттер мен параметрлер бапталды",
        "ar": "تم تكوين جميع مكونات النظام وتفضيلات سطح المكتب"
    },
    "installer.welcome_item2": {
        "en": "Quick launch available in application menu and terminal ('echo-settings')",
        "ru": "Быстрый запуск доступен в меню приложений и терминале ('echo-settings')",
        "es": "Acceso rápido disponible en el menú de aplicaciones y terminal",
        "de": "Schnellstart im Anwendungsmenü und Terminal verfügbar",
        "fr": "Lancement rapide disponible dans le menu des applications et le terminal",
        "zh_CN": "可在应用程序菜单和终端中快速启动 ('echo-settings')",
        "ja": "アプリケーションメニューとターミナルから素早く起動可能 ('echo-settings')",
        "it": "Avvio rapido disponibile nel menu delle applicazioni e nel terminale",
        "pt_BR": "Inicialização rápida disponível no menu de aplicativos e terminal",
        "tr": "Uygulama menüsünden ve terminalden hızlı başlatma kullanılabilir",
        "uk": "Швидкий запуск доступний у меню програм і терміналі ('echo-settings')",
        "kk": "Қолданбалар мәзірінен және терминалдан жылдам іске қосу қолжетімді",
        "ar": "التشغيل السريع متاح في قائمة التطبيقات والطرفية"
    },
    "installer.welcome_item3": {
        "en": "Liquid Glass design and system dark theme synchronized",
        "ru": "Интерфейс Liquid Glass и темная тема синхронизированы",
        "es": "Diseño Liquid Glass y tema oscuro del sistema sincronizados",
        "de": "Liquid Glass Design und dunkles Systemdesign synchronisiert",
        "fr": "Design Liquid Glass et thème sombre synchronisés",
        "zh_CN": "Liquid Glass 设计与系统深色主题已同步",
        "ja": "Liquid Glass デザインとシステムダークテーマが同期されました",
        "it": "Design Liquid Glass e tema scuro di sistema sincronizzati",
        "pt_BR": "Design Liquid Glass e tema escuro sincronizados",
        "tr": "Liquid Glass tasarımı ve sistem koyu teması senkronize edildi",
        "uk": "Дизайн Liquid Glass та темна тема синхронізовані",
        "kk": "Liquid Glass дизайны мен күңгірт тема синхрондалды",
        "ar": "تصميم Liquid Glass والمظهر الداكن للنظام متزامنان"
    },
    "installer.complete_item_autostart": {
        "en": "Autostart at user login enabled",
        "ru": "Автозапуск при входе в систему включен",
        "es": "Inicio automático al iniciar sesión activado",
        "de": "Autostart bei Benutzeranmeldung aktiviert",
        "fr": "Démarrage automatique activé",
        "zh_CN": "开机自动启动已开启",
        "ja": "ログイン時の自動起動が有効になりました",
        "it": "Avvio automatico all'accesso abilitato",
        "pt_BR": "Inicialização automática ativada",
        "tr": "Kullanıcı girişinde otomatik başlatma etkin",
        "uk": "Автозапуск під час входу в систему увімкнено",
        "kk": "Жүйеге кіргенде автоіске қосу қосылды",
        "ar": "تم تمكين التشغيل التلقائي عند تسجيل الدخول"
    },
    "installer.error_title": {
        "en": "Installation Encountered an Issue", "ru": "Ошибка при установке", "es": "Error en la instalación", "de": "Installationsfehler aufgetreten",
        "fr": "Problème lors de l'installation", "zh_CN": "安装过程中出现问题", "ja": "インストール中に問題が発生しました", "it": "Si è verificato un errore durante l'installazione",
        "pt_BR": "Problema durante a instalação", "tr": "Yükleme Sırasında Hata Oluştu", "uk": "Помилка під час встановлення", "kk": "Орнату кезінде қате орын алды", "ar": "واجه التثبيت مشكلة"
    },
    "installer.error_sub": {
        "en": "An unexpected error occurred during the deployment process.",
        "ru": "Произошла непредвиденная ошибка в процессе развертывания.",
        "es": "Ocurrió un error inesperado durante el despliegue.",
        "de": "Während der Bereitstellung ist ein unerwarteter Fehler aufgetreten.",
        "fr": "Une erreur inattendue est survenue lors du déploiement.",
        "zh_CN": "部署过程中发生了非预期的错误。",
        "ja": "デプロイ処理中に予期しないエラーが発生しました。",
        "it": "Si è verificato un errore imprevisto durante la distribuzione.",
        "pt_BR": "Ocorreu um erro inesperado durante a implantação.",
        "tr": "Dağıtım işlemi sırasında beklenmeyen bir hata oluştu.",
        "uk": "Під час розгортання сталася непередбачена помилка.",
        "kk": "Орнату барысында күтпеген қате орын алды.",
        "ar": "حدث خطأ غير متوقع أثناء عملية النشر."
    },
    "installer.copy_diag": {
        "en": "Copy Diagnostics", "ru": "Скопировать отчет", "es": "Copiar diagnósticos", "de": "Diagnose kopieren",
        "fr": "Copier les diagnostics", "zh_CN": "复制诊断信息", "ja": "診断情報をコピー", "it": "Copia diagnostica",
        "pt_BR": "Copiar diagnósticos", "tr": "Teşhis Bilgisini Kopyala", "uk": "Скопіювати звіт", "kk": "Есепті көшіру", "ar": "نسخ بيانات التشخيص"
    },
    "installer.cancel": {
        "en": "Cancel", "ru": "Отмена", "es": "Cancelar", "de": "Abbrechen",
        "fr": "Annuler", "zh_CN": "取消", "ja": "キャンセル", "it": "Annulla",
        "pt_BR": "Cancelar", "tr": "İptal", "uk": "Скасувати", "kk": "Бас тарту", "ar": "إلغاء"
    },
    "installer.retry": {
        "en": "Retry", "ru": "Повторить", "es": "Reintentar", "de": "Wiederholen",
        "fr": "Réessayer", "zh_CN": "重试", "ja": "再試行", "it": "Riprova",
        "pt_BR": "Repetir", "tr": "Yeniden Dene", "uk": "Повторити", "kk": "Қайталау", "ar": "إعادة المحاولة"
    },
    "installer.install_btn": {
        "en": "Install Echo Settings", "ru": "Установить Echo Settings", "es": "Instalar Echo Settings", "de": "Echo Settings installieren",
        "fr": "Installer Echo Settings", "zh_CN": "安装 Echo Settings", "ja": "Echo Settings をインストール", "it": "Installa Echo Settings",
        "pt_BR": "Instalar Echo Settings", "tr": "Echo Settings'i Yükle", "uk": "Встановити Echo Settings", "kk": "Echo Settings орнату", "ar": "تثبيت Echo Settings"
    },
    "installer.finish_setup": {
        "en": "Finish Setup ›", "ru": "Завершить настройку ›", "es": "Finalizar configuración ›", "de": "Einrichtung abschließen ›",
        "fr": "Terminer la configuration ›", "zh_CN": "完成设置 ›", "ja": "設定を完了 ›", "it": "Completa configurazione ›",
        "pt_BR": "Concluir Configuração ›", "tr": "Kurulumu Tamamla ›", "uk": "Завершити налаштування ›", "kk": "Баптауды аяқтау ›", "ar": "إنهاء الإعداد ›"
    },
    "installer.welcome_complete_title": {
        "en": "Echo Settings is Ready!", "ru": "Echo Settings готов к работе!", "es": "¡Echo Settings está listo!", "de": "Echo Settings ist bereit!",
        "fr": "Echo Settings est prêt !", "zh_CN": "Echo Settings 已准备就绪！", "ja": "Echo Settings の準備が整いました！", "it": "Echo Settings è pronto!",
        "pt_BR": "O Echo Settings está pronto!", "tr": "Echo Settings Kullanıma Hazır!", "uk": "Echo Settings готовий до роботи!", "kk": "Echo Settings пайдалануға дайын!", "ar": "Echo Settings جاهز للاستخدام!"
    },
    "installer.welcome_complete_sub": {
        "en": "All system components and desktop preferences are configured.",
        "ru": "Все системные компоненты и параметры рабочего стола успешно настроены.",
        "es": "Todos los componentes del sistema y preferencias están configurados.",
        "de": "Alle Systemkomponenten und Desktopeinstellungen sind konfiguriert.",
        "fr": "Tous les composants système et préférences sont configurés.",
        "zh_CN": "所有系统组件和桌面偏好设置均已配置完成。",
        "ja": "すべてのシステムコンポーネントと環境設定が構成されました。",
        "it": "Tutti i componenti di sistema e le preferenze sono configurati.",
        "pt_BR": "Todos os componentes do sistema e preferências estão configurados.",
        "tr": "Tüm sistem bileşenleri ve masaüstü tercihleri yapılandırıldı.",
        "uk": "Усі системні компоненти та налаштування робочого столу налаштовані.",
        "kk": "Барлық жүйелік компоненттер мен параметрлер сәтті бапталды.",
        "ar": "تم تكوين جميع مكونات النظام وتفضيلات سطح المكتب بنجاح."
    },
    "installer.installing_title": {
        "en": "Installing Echo Settings...", "ru": "Установка Echo Settings...", "es": "Instalando Echo Settings...", "de": "Echo Settings wird installiert...",
        "fr": "Installation d'Echo Settings...", "zh_CN": "正在安装 Echo Settings...", "ja": "Echo Settings をインストール中...", "it": "Installazione di Echo Settings...",
        "pt_BR": "Instalando o Echo Settings...", "tr": "Echo Settings Yükleniyor...", "uk": "Встановлення Echo Settings...", "kk": "Echo Settings орнатылуда...", "ar": "جارٍ تثبيت Echo Settings..."
    },
    "installer.installing_sub": {
        "en": "Deploying standalone Liquid Glass system control center...",
        "ru": "Развертывание центра управления системой Liquid Glass...",
        "es": "Desplegando el centro de control del sistema Liquid Glass...",
        "de": "Eigenständige Liquid Glass-Systemsteuerung wird bereitgestellt...",
        "fr": "Déploiement du centre de contrôle système Liquid Glass...",
        "zh_CN": "正在部署独立的 Liquid Glass 系统控制中心...",
        "ja": "スタンドアロンの Liquid Glass システムコントロールセンターを配置中...",
        "it": "Distribuzione del centro di controllo del sistema Liquid Glass...",
        "pt_BR": "Implantando o centro de controle do sistema Liquid Glass...",
        "tr": "Bağımsız Liquid Glass sistem kontrol merkezi dağıtılıyor...",
        "uk": "Розгортання центру керування системою Liquid Glass...",
        "kk": "Liquid Glass жүйелік басқару орталығы орнатылуда...",
        "ar": "جارٍ نشر مركز التحكم في النظام Liquid Glass المستقل..."
    },
    "installer.complete_title": {
        "en": "Echo Settings is Ready!", "ru": "Echo Settings готов к работе!", "es": "¡Echo Settings está listo!", "de": "Echo Settings ist bereit!",
        "fr": "Echo Settings est prêt !", "zh_CN": "Echo Settings 安装完成！", "ja": "Echo Settings の準備が整いました！", "it": "Echo Settings è pronto!",
        "pt_BR": "O Echo Settings está pronto!", "tr": "Echo Settings Kullanıma Hazır!", "uk": "Echo Settings готовий до роботи!", "kk": "Echo Settings пайдалануға дайын!", "ar": "Echo Settings جاهز للاستخدام!"
    },
    "installer.complete_sub": {
        "en": "Setup finished successfully. Your desktop environment and preferences are configured.",
        "ru": "Настройка успешно завершена. Параметры рабочего стола и системы применены.",
        "es": "Configuración completada con éxito. El entorno de escritorio y preferencias están configurados.",
        "de": "Die Einrichtung wurde erfolgreich abgeschlossen. Ihre Desktop-Umgebung ist konfiguriert.",
        "fr": "Configuration terminée avec succès. Votre environnement de bureau est prêt.",
        "zh_CN": "设置已成功完成。您的桌面环境和偏好设置已就绪。",
        "ja": "セットアップが正常に完了しました。デスクトップ環境と設定が構成されました。",
        "it": "Configurazione completata con successo. Il tuo ambiente desktop è pronto.",
        "pt_BR": "Configuração concluída com sucesso. Seu ambiente de desktop está pronto.",
        "tr": "Kurulum başarıyla tamamlandı. Masaüstü ortamınız ve tercihleriniz yapılandırıldı.",
        "uk": "Налаштування успішно завершено. Параметри робочого столу та системи застосовано.",
        "kk": "Баптау сәтті аяқталды. Жұмыс үстелі параметрлері мен жүйе қолдануға дайын.",
        "ar": "اكتمل الإعداد بنجاح. تم تكوين بيئة سطح المكتب والتفضيلات."
    },
    "installer.launch_btn": {
        "en": "Launch Echo Settings ›", "ru": "Запустить Echo Settings ›", "es": "Iniciar Echo Settings ›", "de": "Echo Settings starten ›",
        "fr": "Lancer Echo Settings ›", "zh_CN": "启动 Echo Settings ›", "ja": "Echo Settings を起動 ›", "it": "Avvia Echo Settings ›",
        "pt_BR": "Iniciar Echo Settings ›", "tr": "Echo Settings'i Başlat ›", "uk": "Запустити Echo Settings ›", "kk": "Echo Settings іске қосу ›", "ar": "تشغيل Echo Settings ›"
    },
    "installer.uninstall_title": {
        "en": "Remove Echo Settings?", "ru": "Удалить Echo Settings?", "es": "¿Eliminar Echo Settings?", "de": "Echo Settings entfernen?",
        "fr": "Supprimer Echo Settings ?", "zh_CN": "卸载 Echo Settings？", "ja": "Echo Settings をアンインストールしますか？", "it": "Rimuovere Echo Settings?",
        "pt_BR": "Remover o Echo Settings?", "tr": "Echo Settings Kaldırılsın mı?", "uk": "Видалити Echo Settings?", "kk": "Echo Settings жою керек пе?", "ar": "إزالة Echo Settings؟"
    },
    "installer.uninstall_desc": {
        "en": "This will remove the application and desktop integration. Personal settings are preserved by default.",
        "ru": "Приложение и интеграция с рабочим столом будут удалены. Пользовательские настройки сохраняются.",
        "es": "Esto eliminará la aplicación y la integración de escritorio. La configuración personal se conserva.",
        "de": "Dadurch werden die Anwendung und die Desktop-Integration entfernt. Persönliche Einstellungen bleiben erhalten.",
        "fr": "Cela supprimera l'application et l'intégration du bureau. Les paramètres personnels sont conservés.",
        "zh_CN": "将卸载应用程序及其桌面集成。个人偏好设置将默认保留。",
        "ja": "アプリケーションとデスクトップ統合が削除されます。個人設定は保持されます。",
        "it": "Questo rimuoverà l'applicazione e l'integrazione desktop. Le impostazioni personali vengono mantenute.",
        "pt_BR": "Isso removerá o aplicativo e a integração com o desktop. As configurações pessoais serão mantidas.",
        "tr": "Bu işlem uygulamayı ve masaüstü entegrasyonunu kaldırır. Kişisel ayarlar korunur.",
        "uk": "Це видалить застосунок та інтеграцію з робочим столом. Особисті налаштування зберігаються.",
        "kk": "Қолданба мен жұмыс үстелі интеграциясы жойылады. Жеке параметрлер сақталады.",
        "ar": "سيؤدي هذا إلى إزالة التطبيق وتكامل سطح المكتب. يتم الاحتفاظ بالإعدادات الشخصية."
    },
    "installer.uninstall_chk_data": {
        "en": "Also remove user settings and configurations (~/.config/EchoSettings)",
        "ru": "Также удалить пользовательские настройки и конфигурации (~/.config/EchoSettings)",
        "es": "Eliminar también la configuración del usuario (~/.config/EchoSettings)",
        "de": "Auch Benutzereinstellungen und Konfigurationen entfernen (~/.config/EchoSettings)",
        "fr": "Supprimer également les paramètres et configurations utilisateur (~/.config/EchoSettings)",
        "zh_CN": "同时删除用户偏好设置与配置文件 (~/.config/EchoSettings)",
        "ja": "ユーザー設定と構成も削除する (~/.config/EchoSettings)",
        "it": "Rimuovi anche le impostazioni e le configurazioni dell'utente (~/.config/EchoSettings)",
        "pt_BR": "Também remover configurações do usuário (~/.config/EchoSettings)",
        "tr": "Kullanıcı ayarlarını ve yapılandırmalarını da kaldır (~/.config/EchoSettings)",
        "uk": "Також видалити налаштування та конфігурації користувача (~/.config/EchoSettings)",
        "kk": "Пайдаланушы параметрлері мен конфигурацияларын да жою (~/.config/EchoSettings)",
        "ar": "إزالة إعدادات وتكوينات المستخدم أيضًا (~/.config/EchoSettings)"
    },
    "installer.uninstall_btn": {
        "en": "Remove Application", "ru": "Удалить приложение", "es": "Eliminar aplicación", "de": "Anwendung entfernen",
        "fr": "Supprimer l'application", "zh_CN": "卸载应用程序", "ja": "アプリケーションを削除", "it": "Rimuovi applicazione",
        "pt_BR": "Remover Aplicativo", "tr": "Uygulamayı Kaldır", "uk": "Видалити застосунок", "kk": "Қолданбаны жою", "ar": "إزالة التطبيق"
    },
    "installer.close_btn": {
        "en": "Done", "ru": "Готово", "es": "Listo", "de": "Fertig",
        "fr": "Terminé", "zh_CN": "完成", "ja": "完了", "it": "Fine",
        "pt_BR": "Concluído", "tr": "Bitti", "uk": "Готово", "kk": "Дайын", "ar": "تم"
    },
    "installer.search_companion_title": {
        "en": "Echo Search Companion", "ru": "Умный поиск Echo Search", "es": "Búsqueda Echo Search", "de": "Echo Search Begleiter",
        "fr": "Recherche Echo Search", "zh_CN": "Echo Search 智能聚焦搜索", "ja": "Echo Search スポットライト検索", "it": "Ricerca Rapida Echo Search",
        "pt_BR": "Busca Rápida Echo Search", "tr": "Echo Search Arama Modülü", "uk": "Розумний пошук Echo Search", "kk": "Echo Search ақылды іздеу", "ar": "مساعد البحث الذكي Echo Search"
    },
    "installer.search_companion_sub": {
        "en": "Spotlight-style instant search, app launcher, and quick calculator for Linux.",
        "ru": "Мгновенный поиск файлов, запуск приложений и умный калькулятор в стиле Spotlight.",
        "es": "Búsqueda instantánea estilo Spotlight, lanzador de aplicaciones y calculadora rápida.",
        "de": "Blitzschnelle Spotlight-Suche, App-Starter und Schnellrechner für Linux.",
        "fr": "Recherche instantanée style Spotlight, lanceur d'applications et calculatrice rapide.",
        "zh_CN": "Spotlight 风格的高速文件搜索、应用启动器与即时计算器。",
        "ja": "Spotlight スタイルの高速ファイル検索、アプリランチャー、即時計算ツール。",
        "it": "Ricerca rapida in stile Spotlight, launcher di app e calcolatrice istantanea.",
        "pt_BR": "Pesquisa instantânea no estilo Spotlight, iniciador de apps e calculadora rápida.",
        "tr": "Spotlight tarzı hızlı dosya arama, uygulama başlatıcı ve anında hesap makinesi.",
        "uk": "Миттєвий пошук файлів, запуск застосунків та розумний калькулятор у стилі Spotlight.",
        "kk": "Spotlight стиліндегі файлдарды жылдам іздеу, қолданбаларды іске қосу және калькулятор.",
        "ar": "بحث فوري عن الملفات بنمط Spotlight، ومشغل تطبيقات، وحاسبة سريعة لنظام Linux."
    },
    "installer.search_tip_title": {
        "en": "Echo Ecosystem", "ru": "Экосистема Echo", "es": "Ecosistema Echo", "de": "Echo-Ökosystem",
        "fr": "Écosystème Echo", "zh_CN": "Echo 生态系统", "ja": "Echo エコシステム", "it": "Ecosistema Echo",
        "pt_BR": "Ecossistema Echo", "tr": "Echo Ekosistemi", "uk": "Екосистема Echo", "kk": "Echo экожүйесі", "ar": "منظومة Echo"
    },
    "installer.search_tip_desc": {
        "en": "Summon instantly anywhere using the Super + Space keyboard shortcut.",
        "ru": "Быстрый вызов комбинацией клавиш Super + Space в любом месте системы.",
        "es": "Invoque al instante en cualquier lugar con el atajo Super + Espacio.",
        "de": "Überall sofort mit dem Tastaturkürzel Super + Leertaste aufrufbar.",
        "fr": "Appelez instantanément n'importe où avec le raccourci Super + Espace.",
        "zh_CN": "在系统的任何位置均可使用 Super + 空格 快捷键即时呼出。",
        "ja": "Super + Space ショートカットでいつでもどこでも即座に呼び出せます。",
        "it": "Richiama istantaneamente ovunque con la combinazione di tasti Super + Spazio.",
        "pt_BR": "Abra instantaneamente em qualquer lugar usando o atalho Super + Espaço.",
        "tr": "Sistemin her yerinde Super + Boşluk kısayoluyla anında açın.",
        "uk": "Швидкий виклик комбінацією клавіш Super + Space у будь-якому місці системи.",
        "kk": "Жүйенің кез келген жерінде Super + Space пернелер тіркесімімен жылдам шақырыңыз.",
        "ar": "يمكنك استدعاؤه فوراً في أي مكان باستخدام اختصار لوحة المفاتيح Super + Space."
    },
    "installer.search_preview_placeholder": {
        "en": "Search files, apps, calculations...", "ru": "Поиск файлов, программ, подсчет...", "es": "Buscar archivos, aplicaciones, cálculos...", "de": "Dateien, Apps, Rechnungen suchen...",
        "fr": "Rechercher des fichiers, applications, calculs...", "zh_CN": "搜索文件、应用程序、快速计算...", "ja": "ファイル、アプリ、計算を検索...", "it": "Cerca file, applicazioni, calcoli...",
        "pt_BR": "Buscar arquivos, apps, cálculos...", "tr": "Dosyaları, uygulamaları, hesaplamaları ara...", "uk": "Пошук файлів, програм, підрахунок...", "kk": "Файлдарды, бағдарламаларды іздеу...", "ar": "ابحث عن الملفات والتطبيقات والحسابات..."
    },
    "installer.search_opt_install": {
        "en": "Install Echo Search (Recommended)", "ru": "Установить Echo Search (Рекомендуется)", "es": "Instalar Echo Search (Recomendado)", "de": "Echo Search installieren (Empfohlen)",
        "fr": "Installer Echo Search (Recommandé)", "zh_CN": "安装 Echo Search 智能搜索模块 (推荐)", "ja": "Echo Search をインストール (推奨)", "it": "Installa Echo Search (Consigliato)",
        "pt_BR": "Instalar Echo Search (Recomendado)", "tr": "Echo Search Yükle (Önerilen)", "uk": "Встановити Echo Search (Рекомендовано)", "kk": "Echo Search орнату (Ұсынылады)", "ar": "تثبيت Echo Search (موصى به)"
    },
    "installer.search_opt_enable": {
        "en": "Enable Echo Search (Recommended)", "ru": "Активировать Echo Search (Рекомендуется)", "es": "Habilitar Echo Search (Recomendado)", "de": "Echo Search aktivieren (Empfohlen)",
        "fr": "Activer Echo Search (Recommandé)", "zh_CN": "启用 Echo Search 智能搜索 (推荐)", "ja": "Echo Search を有効化 (推奨)", "it": "Abilita Echo Search (Consigliato)",
        "pt_BR": "Ativar Echo Search (Recomendado)", "tr": "Echo Search Etkinleştir (Önerilen)", "uk": "Активувати Echo Search (Рекомендовано)", "kk": "Echo Search іске қосу (Ұсынылады)", "ar": "تمكين Echo Search (موصى به)"
    },

    "installer.search_opt_desc": {
        "en": "Instant indexing service and Super+Space global shortcut.",
        "ru": "Фоновый сервис быстрой индексации и горячая клавиша Super+Space.",
        "es": "Servicio de indexación rápida y atajo global Super+Espacio.",
        "de": "Schneller Indizierungsdienst und Super+Leertaste Tastenkürzel.",
        "fr": "Service d'indexation rapide et raccourci global Super+Espace.",
        "zh_CN": "高速索引后台服务与 Super+空格 全局快捷键。",
        "ja": "高速インデックスサービスと Super+Space グローバルショートカット。",
        "it": "Servizio di indicizzazione rapida e scorciatoia globale Super+Spazio.",
        "pt_BR": "Serviço de indexação rápida e atalho global Super+Espaço.",
        "tr": "Hızlı dizin oluşturma hizmeti ve Super+Boşluk genel kısayolu.",
        "uk": "Фонова служба швидкої індексації та гаряча клавіша Super+Space.",
        "kk": "Жылдам индекстеу қызметі мен Super+Space жаһандық пернесі.",
        "ar": "خدمة الفهرسة السريعة واختصار لوحة المفاتيح العام Super+Space."
    },
    "installer.search_github_title": {
        "en": "Echo Search Repository", "ru": "Репозиторий Echo Search", "es": "Repositorio Echo Search", "de": "Echo Search Repository",
        "fr": "Dépôt Echo Search", "zh_CN": "Echo Search 开源仓库", "ja": "Echo Search リポジトリ", "it": "Repository Echo Search",
        "pt_BR": "Repositório Echo Search", "tr": "Echo Search Deposu", "uk": "Репозиторій Echo Search", "kk": "Echo Search репозиторийі", "ar": "مستودع Echo Search"
    },
    "installer.search_github_desc": {
        "en": "Source code, release roadmap and plugins.",
        "ru": "Исходный код, плагины расширений и релизы.",
        "es": "Código fuente, complementos y lanzamientos.",
        "de": "Quellcode, Erweiterungs-Plugins und Releases.",
        "fr": "Code source, extensions et versions.",
        "zh_CN": "源代码、扩展插件库与版本发布日志。",
        "ja": "ソースコード、プラグイン、リリース情報。",
        "it": "Codice sorgente, plugin di estensione e rilasci.",
        "pt_BR": "Código-fonte, plugins de extensão e lançamentos.",
        "tr": "Kaynak kodu, eklenti paketleri ve sürümler.",
        "uk": "Вихідний код, плагіни розширень та релізи.",
        "kk": "Бастапқы код, плагиндер және шығарылымдар.",
        "ar": "شفرة المصدر وإضافات التوسيع والإصدارات."
    },
    "installer.search_github_btn": {
        "en": "GitHub ↗", "ru": "GitHub ↗", "es": "GitHub ↗", "de": "GitHub ↗",
        "fr": "GitHub ↗", "zh_CN": "GitHub ↗", "ja": "GitHub ↗", "it": "GitHub ↗",
        "pt_BR": "GitHub ↗", "tr": "GitHub ↗", "uk": "GitHub ↗", "kk": "GitHub ↗", "ar": "GitHub ↗"
    },
    "installer.spotlight_cat_apps": {
        "en": "APPLICATIONS", "ru": "ПРИЛОЖЕНИЯ", "es": "APLICACIONES", "de": "ANWENDUNGEN",
        "fr": "APPLICATIONS", "zh_CN": "应用程序", "ja": "アプリケーション", "it": "APPLICAZIONI",
        "pt_BR": "APLICATIVOS", "tr": "UYGULAMALAR", "uk": "ПРОГРАМИ", "kk": "БАҒДАРЛАМАЛАР", "ar": "التطبيقات"
    },
    "installer.spotlight_cat_calc": {
        "en": "CALCULATIONS", "ru": "ВЫЧИСЛЕНИЯ", "es": "CÁLCULOS", "de": "BERECHNUNGEN",
        "fr": "CALCULS", "zh_CN": "快速计算", "ja": "計算", "it": "CALCOLI",
        "pt_BR": "CÁLCULOS", "tr": "HESAPLAMALAR", "uk": "ОБЧИСЛЕННЯ", "kk": "ЕСЕПТЕУЛЕР", "ar": "الحسابات"
    },
    "installer.spotlight_app_desc": {
        "en": "Liquid Glass System Control Center", "ru": "Центр управления системой Liquid Glass", "es": "Centro de control del sistema Liquid Glass", "de": "Liquid Glass Systemsteuerung",
        "fr": "Centre de contrôle système Liquid Glass", "zh_CN": "Liquid Glass 系统控制中心", "ja": "Liquid Glass システムコントロールセンター", "it": "Centro di controllo del sistema Liquid Glass",
        "pt_BR": "Centro de controle do sistema Liquid Glass", "tr": "Liquid Glass Sistem Kontrol Merkezi", "uk": "Центр керування системою Liquid Glass", "kk": "Liquid Glass жүйелік басқару орталығы", "ar": "مركز التحكم في النظام Liquid Glass"
    },
    "installer.spotlight_term_name": {
        "en": "Terminal", "ru": "Терминал", "es": "Terminal", "de": "Terminal",
        "fr": "Terminal", "zh_CN": "终端", "ja": "ターミナル", "it": "Terminale",
        "pt_BR": "Terminal", "tr": "Terminal", "uk": "Термінал", "kk": "Терминал", "ar": "الطرفية"
    },
    "installer.spotlight_term_desc": {
        "en": "System Command Line Interface", "ru": "Системная командная строка", "es": "Línea de comandos del sistema", "de": "System-Befehlszeile",
        "fr": "Interface de ligne de commande", "zh_CN": "系统命令行工具", "ja": "システムコマンドライン", "it": "Interfaccia a riga di comando",
        "pt_BR": "Interface de linha de comando", "tr": "Sistem Komut Satırı Arayüzü", "uk": "Системний командний рядок", "kk": "Жүйелік командалық жол", "ar": "واجهة سطر الأوامر"
    },
    "installer.spotlight_calc_desc": {
        "en": "Smart inline calculation", "ru": "Быстрый подсчет", "es": "Cálculo instantáneo", "de": "Schnelle Berechnung",
        "fr": "Calcul instantané", "zh_CN": "智能实时计算", "ja": "スマートインライン計算", "it": "Calcolo istantaneo",
        "pt_BR": "Cálculo instantâneo", "tr": "Akıllı anlık hesaplama", "uk": "Швидкий підрахунок", "kk": "Жылдам есептеу", "ar": "حساب فوري ذكي"
    },
    "installer.search_feature_shortcut": {
        "en": "Super + Space shortcut anywhere", "ru": "Хоткей Super + Space поверх всех окон", "es": "Atajo Super + Espacio en cualquier lugar", "de": "Super + Leertaste Kurzbefehl überall",
        "fr": "Raccourci Super + Espace partout", "zh_CN": "随时随地使用 Super + 空格 呼出", "ja": "どこでも Super + Space で呼び出し", "it": "Scorciatoia Super + Spazio ovunque",
        "pt_BR": "Atalho Super + Espaço em qualquer lugar", "tr": "Her yerde Super + Boşluk kısayolu", "uk": "Хоткей Super + Space поверх усіх вікон", "kk": "Кез келген жерде Super + Space пернесі", "ar": "اختصار Super + Space في أي مكان"
    },
    "installer.search_feature_files": {
        "en": "Instant deep file and app indexing", "ru": "Мгновенный поиск файлов и программ", "es": "Búsqueda instantánea de archivos y apps", "de": "Sofortige Datei- und App-Indizierung",
        "fr": "Indexation instantanée des fichiers et apps", "zh_CN": "秒级文件与应用程序深度索引", "ja": "ファイルとアプリの即時インデックス検索", "it": "Indicizzazione istantanea di file e app",
        "pt_BR": "Indexação instantânea de arquivos e apps", "tr": "Anında dosya ve uygulama dizinleme", "uk": "Миттєвий пошук файлів та програм", "kk": "Файлдар мен қолданбаларды лезде іздеу", "ar": "فهرسة وبحث فوري للملفات والتطبيقات"
    },
    "installer.search_feature_calc": {
        "en": "Inline calculator & currency converter", "ru": "Встроенный калькулятор и конвертер", "es": "Calculadora integrada y conversor", "de": "Integrierter Rechner und Währungsumrechner",
        "fr": "Calculatrice intégrée et convertisseur", "zh_CN": "内置智能计算器与货币换算", "ja": "インライン計算機と通貨換算", "it": "Calcolatrice e convertitore integrati",
        "pt_BR": "Calculadora integrada e conversor", "tr": "Dahili hesap makinesi ve dönüştürücü", "uk": "Вбудований калькулятор та конвертер", "kk": "Кірістірілген калькулятор мен конвертер", "ar": "حاسبة مدمجة ومحول عملات"
    },

    "installer.complete_item_search": {
        "en": "Echo Search companion enabled (Super + Space shortcut)",
        "ru": "Модуль Echo Search активирован (горячая клавиша Super + Space)",
        "es": "Módulo Echo Search activado (atajo Super + Espacio)",
        "de": "Echo Search Begleiter aktiviert (Super + Leertaste)",
        "fr": "Module Echo Search activé (raccourci Super + Espace)",
        "zh_CN": "Echo Search 智能搜索已激活 (Super + 空格 快捷键)",
        "ja": "Echo Search モジュールが有効化されました (Super + Space)",
        "it": "Modulo Echo Search attivato (scorciatoia Super + Spazio)",
        "pt_BR": "Módulo Echo Search ativado (atalho Super + Espaço)",
        "tr": "Echo Search modülü etkinleştirildi (Super + Boşluk kısayolu)",
        "uk": "Модуль Echo Search активовано (гаряча клавіша Super + Space)",
        "kk": "Echo Search модулі белсендірілді (Super + Space пернесі)",
        "ar": "تم تفعيل مساعد Echo Search (اختصار Super + Space)"
    },

    "installer.log_show": {
        "en": "Show Installation Log", "ru": "Показать журнал установки", "es": "Mostrar registro de instalación",
        "de": "Installationsprotokoll anzeigen", "fr": "Afficher le journal d'installation", "zh_CN": "显示安装日志",
        "ja": "インストールログを表示", "it": "Mostra registro di installazione", "pt_BR": "Mostrar registro de instalação",
        "tr": "Kurulum Günlüğünü Göster", "uk": "Показати журнал встановлення", "kk": "Орнату журналын көрсету", "ar": "إظهار سجل التثبيت"
    },
    "installer.log_hide": {
        "en": "Hide Installation Log", "ru": "Скрыть журнал установки", "es": "Ocultar registro de instalación",
        "de": "Installationsprotokoll ausblenden", "fr": "Masquer le journal d'installation", "zh_CN": "隐藏安装日志",
        "ja": "インストールログを非表示", "it": "Nascondi registro di installazione", "pt_BR": "Ocultar registro de instalação",
        "tr": "Kurulum Günlüğünü Gizle", "uk": "Приховати журнал встановлення", "kk": "Орнату журналын жасыру", "ar": "إخفاء سجل التثبيت"
    },
    "installer.log_copy": {
        "en": "Copy Log", "ru": "Скопировать журнал", "es": "Copiar registro", "de": "Protokoll kopieren",
        "fr": "Copier le journal", "zh_CN": "复制日志", "ja": "ログをコピー", "it": "Copia registro",
        "pt_BR": "Copiar registro", "tr": "Günlüğü Kopyala", "uk": "Скопіювати журнал", "kk": "Журналды көшіру", "ar": "نسخ السجل"
    },
    "installer.log_copied": {
        "en": "Copied!", "ru": "Скопировано!", "es": "¡Copiado!", "de": "Kopiert!",
        "fr": "Copié !", "zh_CN": "已复制！", "ja": "コピーしました！", "it": "Copiato!",
        "pt_BR": "Copiado!", "tr": "Kopyalandı!", "uk": "Скопійовано!", "kk": "Көшірілді!", "ar": "تم النسخ!"
    },
    "installer.check_status_ok": {
        "en": "All components compatible. System ready for installation.",
        "ru": "Все компоненты совместимы. Система готова к установке.",
        "es": "Todos los componentes son compatibles. Sistema listo para instalar.",
        "de": "Alle Komponenten kompatibel. System bereit zur Installation.",
        "fr": "Tous les composants sont compatibles. Système prêt pour l'installation.",
        "zh_CN": "所有组件均兼容。系统已准备就绪。",
        "ja": "すべてのコンポーネントが互換性があります。インストールの準備が整いました。",
        "it": "Tutti i componenti sono compatibili. Sistema pronto per l'installazione.",
        "pt_BR": "Todos os componentes compatíveis. Sistema pronto para instalação.",
        "tr": "Tüm bileşenler uyumlu. Sistem kuruluma hazır.",
        "uk": "Всі компоненти сумісні. Система готова до встановлення.",
        "kk": "Барлық компоненттер үйлесімді. Жүйе орнатуға дайын.",
        "ar": "جميع المكونات متوافقة. النظام جاهز للتثبيت."
    },
    "installer.check_status_warn": {
        "en": "Minor warnings detected. Installation can proceed.",
        "ru": "Обнаружены предупреждения. Установка возможна.",
        "es": "Advertencias menores detectadas. La instalación puede continuar.",
        "de": "Warnungen erkannt. Installation möglich.",
        "fr": "Avertissements mineurs détectés. L'installation peut continuer.",
        "zh_CN": "检测到次要警告。可以继续安装。",
        "ja": "軽微な警告が検出されました。インストールを続行できます。",
        "it": "Rilevati avvisi minori. L'installazione può procedere.",
        "pt_BR": "Avisos menores detectados. A instalação pode continuar.",
        "tr": "Küçük uyarılar algılandı. Kuruluma devam edilebilir.",
        "uk": "Виявлено попередження. Встановлення можливе.",
        "kk": "Ескертулер табылды. Орнатуды жалғастыруға болады.",
        "ar": "تم اكتشاف تحذيرات طفيفة. يمكن متابعة التثبيت."
    },
    "installer.check_status_fail": {
        "en": "Critical requirement not met. Please resolve before proceeding.",
        "ru": "Критическое требование не выполнено. Требуется исправление.",
        "es": "Requisito crítico no cumplido. Resuelva antes de continuar.",
        "de": "Kritische Anforderung nicht erfüllt. Bitte beheben.",
        "fr": "Exigence critique non respectée. Veuillez résoudre avant de continuer.",
        "zh_CN": "未满足关键要求。请在继续前解决。",
        "ja": "重要な要件が満たされていません。解決してから続行してください。",
        "it": "Requisito critico non soddisfatto. Risolvere prima di procedere.",
        "pt_BR": "Requisito crítico não atendido. Resolva antes de continuar.",
        "tr": "Kritik gereksinim karşılanmadı. Lütfen devam etmeden önce çözün.",
        "uk": "Критична вимога не виконана. Потрібно виправити.",
        "kk": "Маңызды талап орындалмады. Жалғастырмас бұрын түзетіңіз.",
        "ar": "لم يتم استيفاء متطلب أساسي. يرجى الحل قبل المتابعة."
    },
    "installer.uninstaller_title": {
        "en": "Uninstall Echo Settings?", "ru": "Удалить Echo Settings?", "es": "¿Desinstalar Echo Settings?",
        "de": "Echo Settings deinstallieren?", "fr": "Désinstaller Echo Settings ?", "zh_CN": "卸载 Echo Settings？",
        "ja": "Echo Settings をアンインストールしますか？", "it": "Disinstallare Echo Settings?", "pt_BR": "Desinstalar Echo Settings?",
        "tr": "Echo Settings kaldırılsın mı?", "uk": "Видалити Echo Settings?", "kk": "Echo Settings жою керек пе?", "ar": "هل تريد إلغاء تثبيت Echo Settings؟"
    },
    "installer.uninstaller_desc": {
        "en": "The application binaries, icons, and desktop integration will be cleanly removed.",
        "ru": "Исполняемые файлы приложения, иконки и интеграция с рабочим столом будут удалены.",
        "es": "Los archivos de la aplicación, iconos e integraciones se eliminarán de forma limpia.",
        "de": "Die Anwendungsdateien, Symbole und Desktop-Integrationen werden sauber entfernt.",
        "fr": "L'application, les icônes et les intégrations du bureau seront supprimées proprement.",
        "zh_CN": "应用程序文件、图标以及桌面集成将被完全彻底移除。",
        "ja": "アプリケーションファイル、アイコン、デスクトップ統合が完全に削除されます。",
        "it": "I file dell'applicazione, le icone e l'integrazione desktop verranno rimossi.",
        "pt_BR": "Os arquivos do aplicativo, ícones e integração da área de trabalho serão removidos.",
        "tr": "Uygulama dosyaları, simgeler ve masaüstü entegrasyonu temiz bir şekilde kaldırılacak.",
        "uk": "Файли застосунку, піктограми та інтеграція з робочим столом будуть видалені.",
        "kk": "Қолданба файлдары, белгішелер және жұмыс үстелі интеграциясы толығымен жойылады.",
        "ar": "ستتم إزالة ملفات التطبيق والأيقونات وتكاملات سطح المكتب بشكل نظيف."
    },
    "installer.uninstaller_chk_data": {
        "en": "Also delete user settings & cache (~/.config/EchoSettings)",
        "ru": "Удалить настройки и кэш пользователя (~/.config/EchoSettings)",
        "es": "Eliminar también configuración y caché (~/.config/EchoSettings)",
        "de": "Benutzerkonfigurationen und Cache ebenfalls löschen (~/.config/EchoSettings)",
        "fr": "Supprimer aussi la configuration et le cache (~/.config/EchoSettings)",
        "zh_CN": "同时删除用户配置与缓存目录 (~/.config/EchoSettings)",
        "ja": "ユーザー設定およびキャッシュも削除 (~/.config/EchoSettings)",
        "it": "Elimina anche configurazione e cache (~/.config/EchoSettings)",
        "pt_BR": "Excluir configurações e cache do usuário (~/.config/EchoSettings)",
        "tr": "Kullanıcı ayarları ve önbelleği de sil (~/.config/EchoSettings)",
        "uk": "Видалити налаштування та кеш користувача (~/.config/EchoSettings)",
        "kk": "Баптаулар мен кэш файлдарын да жою (~/.config/EchoSettings)",
        "ar": "حذف إعدادات والذاكرة المؤقتة للمستخدم (~/.config/EchoSettings)"
    },
    "installer.uninstaller_btn_confirm": {
        "en": "Uninstall Application", "ru": "Удалить приложение", "es": "Desinstalar aplicación",
        "de": "Anwendung deinstallieren", "fr": "Désinstaller l'application", "zh_CN": "卸载应用程序",
        "ja": "アプリケーションをアンインストール", "it": "Disinstalla applicazione", "pt_BR": "Desinstalar aplicativo",
        "tr": "Uygulamayı Kaldır", "uk": "Видалити застосунок", "kk": "Қолданбаны жою", "ar": "إلغاء تثبيت التطبيق"
    },
    "installer.uninstaller_removing": {
        "en": "Removing Echo Settings...", "ru": "Удаление Echo Settings...", "es": "Eliminando Echo Settings...",
        "de": "Echo Settings wird entfernt...", "fr": "Suppression de Echo Settings...", "zh_CN": "正在卸载 Echo Settings...",
        "ja": "Echo Settings をアンインストール中...", "it": "Rimozione di Echo Settings...", "pt_BR": "Removendo Echo Settings...",
        "tr": "Echo Settings kaldırılıyor...", "uk": "Видалення Echo Settings...", "kk": "Echo Settings жойылуда...", "ar": "جارٍ إزالة Echo Settings..."
    },
    "installer.uninstaller_done": {
        "en": "Echo Settings successfully uninstalled.", "ru": "Echo Settings успешно удален из системы.",
        "es": "Echo Settings se ha desinstalado correctamente.", "de": "Echo Settings wurde erfolgreich deinstalliert.",
        "fr": "Echo Settings a été désinstallé avec succès.", "zh_CN": "Echo Settings 已成功从系统中卸载。",
        "ja": "Echo Settings は正常にアンインストールされました。", "it": "Echo Settings è stato disinstallato con successo.",
        "pt_BR": "Echo Settings foi desinstalado com sucesso.", "tr": "Echo Settings başarıyla kaldırıldı.",
        "uk": "Echo Settings успішно видалено з системи.", "kk": "Echo Settings жүйеден сәтті жойылды.", "ar": "تم إلغاء تثبيت Echo Settings بنجاح."
    }



}


class I18nManager(QObject):
    language_changed = Signal(str)
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(I18nManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return
        super().__init__()
        self._initialized = True
        self._current_lang = self._load_saved_or_system_language()

    def _load_saved_or_system_language(self) -> str:
        # 1. Try loading from QSettings (TahoeSettings and EchoSettings)
        try:
            for org in ("EchoSettings", "TahoeSettings"):
                settings = QSettings(org, "App")
                saved = settings.value("language", None)
                if saved and saved in SUPPORTED_LANGUAGES:
                    return saved
        except Exception:
            pass

        # 2. Try auto-detecting system locale
        try:
            loc = os.environ.get("LC_MESSAGES", "") or os.environ.get("LANG", "")
            if not loc:
                loc = locale.getdefaultlocale()[0] or "en"
            
            loc_lower = loc.lower()
            if loc_lower.startswith("ru"): return "ru"
            if loc_lower.startswith("es"): return "es"
            if loc_lower.startswith("de"): return "de"
            if loc_lower.startswith("fr"): return "fr"
            if "zh" in loc_lower: return "zh_CN"
            if loc_lower.startswith("ja"): return "ja"
            if loc_lower.startswith("it"): return "it"
            if "pt" in loc_lower: return "pt_BR"
            if loc_lower.startswith("tr"): return "tr"
            if loc_lower.startswith("uk"): return "uk"
            if loc_lower.startswith("kk"): return "kk"
            if loc_lower.startswith("ar"): return "ar"
        except Exception:
            pass

        return "en"

    @property
    def current_language(self) -> str:
        return self._current_lang

    def set_language(self, lang_code: str):
        if lang_code in SUPPORTED_LANGUAGES and lang_code != self._current_lang:
            self._current_lang = lang_code
            try:
                for org in ("EchoSettings", "TahoeSettings"):
                    settings = QSettings(org, "App")
                    settings.setValue("language", lang_code)
            except Exception:
                pass
            self.language_changed.emit(lang_code)

    def t(self, key: str, default: str | None = None, **kwargs) -> str:
        """Translates a key into the current active language."""
        if key in TRANSLATIONS:
            lang_dict = TRANSLATIONS[key]
            text = lang_dict.get(self._current_lang) or lang_dict.get("en", default or key)
            if kwargs:
                try:
                    text = text.format(**kwargs)
                except Exception:
                    pass
            return text
        return default or key


# Global singleton instance and shortcut function
i18n = I18nManager()
Localization = i18n
Localization.get = i18n.t

def t(key: str, default: str | None = None, **kwargs) -> str:
    return i18n.t(key, default, **kwargs)

tr = t

