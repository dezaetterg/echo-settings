<div align="center">

<img src="assets/echo_icon.png" alt="Echo Settings Logo" width="120">

# Echo Settings

**Современный центр управления и системных настроек для Linux с интерфейсом Liquid Glass (Qt 6 / PySide6 / D-Bus)**

[![Version](https://img.shields.io/badge/version-1.0.1-blue.svg?style=flat-square)](https://github.com/dezaetterg/echo-settings/releases)
[![License](https://img.shields.io/badge/license-GPL--3.0-green.svg?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux-orange.svg?style=flat-square)](https://github.com/dezaetterg/echo-settings)
[![Qt6](https://img.shields.io/badge/UI-Qt6%20%2F%20PySide6-brightgreen.svg?style=flat-square)](https://www.qt.io/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square)](https://www.python.org/)

</div>

## Возможности

* **🎨 Оформление и темы**: переключение светлой/темной темы, выбор акцентных цветов интерфейса и встроенная галерея фирменных 4K-обоев Echo с автоматической сменой день/ночь.
* **🖥 Дисплеи и HDR**: интерактивная расстановка мониторов перетаскиванием, настройка разрешений, частоты обновления (Hz), масштабирования (HiDPI / Fractional Scaling) и ночного режима (Night Light).
* **📶 Сети и подключения**: быстрый Wi-Fi менеджер со сканированием эфира, проводная сеть (Ethernet), VPN, сетевые прокси и Bluetooth-менеджер для сопряжения устройств.
* **🔊 Звук и мультимедиа**: интеграция с PipeWire и PulseAudio, раздельная регулировка громкости источников вывода и микрофонов, селектор звуковых карт.
* **🔋 Питание и батарея**: переключение профилей энергопотребления (производительный, сбалансированный, энергосберегающий), мониторинг аккумулятора и таймеры сна.
* **🖱 Мышь и тачпад**: регулировка скорости курсора, ускорение, естественная прокрутка (Natural Scrolling) и жесты тачпада.
* **⌨️ Клавиатура**: управление раскладками, задержками ввода и глобальными горячими клавишами.
* **🔒 Приватность и безопасность**: контроль доступа приложений к геолокации, камере, микрофону и настройка блокировки экрана.
* **💾 Хранилище**: интерактивная диаграмма занятого места по категориям и быстрая очистка кэша/корзины в один клик.
* **🔔 Уведомления**: глобальный режим «Не беспокоить» (Do Not Disturb) и индивидуальные правила для каждого приложения.
* **🔍 Интеграция с Echo Search**: прямое управление параметрами лаунчера Echo Search (прозрачность, эффекты размытия, горячие клавиши, модули поиска).
* **💎 Дизайн Liquid Glass**: полупрозрачный стеклянный интерфейс с акриловыми панелями, плавными анимациями и адаптивным стилем.

## Совместимость и тестирование

* **Дистрибутивы**: приложение разрабатывалось и тестировалось на Debian-based системах: **PikaOS**, **Debian 13 (Trixie)**, **Ubuntu 22.04+** и **Linux Mint**. Поддерживаются все популярные дистрибутивы Linux (Fedora, Arch Linux, openSUSE).
* **Окружения рабочего стола**: глубокая интеграция с **GNOME** и **Cinnamon** через D-Bus/GSettings, а также поддержка **KDE Plasma**, **XFCE**, **Wayland** и **X11**.

## Установка

### 1. Универсальный установщик (Рекомендуется)
Скрипт проверяет систему, устанавливает необходимые зависимости, регистрирует приложение в системном меню и настраивает иконки:

```bash
git clone https://github.com/dezaetterg/echo-settings.git
cd echo-settings
chmod +x install.sh
./install.sh
```

### 2. Debian / Ubuntu / Linux Mint / PikaOS (.deb)
Готовый пакет доступен на странице [Releases](https://github.com/dezaetterg/echo-settings/releases):

```bash
sudo apt install ./echo-settings_1.0.1_amd64.deb
```

### 3. Сборка своего deb-пакета
```bash
git clone https://github.com/dezaetterg/echo-settings.git
cd echo-settings
./build_deb.sh
```

### 4. Запуск из исходного кода
```bash
git clone https://github.com/dezaetterg/echo-settings.git
cd echo-settings

# Установка зависимостей
pip install -r requirements.txt

# Запуск
python3 main.py
```

### Если пакеты или репозитории недоступны (Linux Mint / Ubuntu)

Если система сообщает, что пакеты PySide6 или Qt6 не найдены, включите репозиторий `universe`:

```bash
sudo add-apt-repository universe
sudo apt update
sudo apt install python3-pyside6.qtcore python3-pyside6.qtgui python3-pyside6.qtwidgets
```

## Управление и навигация

* `Поиск в боковой панели` : мгновенный поиск нужного пункта настроек по ключевым словам на русском и английском языках
* `Клик по карточке / разделу` : плавный переход к соответствующей категории настроек
* `Esc` : очистка строки поиска

## Архитектура и системные шины

Echo Settings взаимодействует с системными сервисами Linux напрямую через стандартизированные шины **D-Bus**:
* **GSettings / dconf** : параметры тем оформления, шрифтов, обоев и таймаутов.
* **NetworkManager D-Bus API** : сканирование точек доступа Wi-Fi и управление подключениями.
* **UPower** : мониторинг состояния батареи и профилей электропитания.
* **PipeWire / PulseAudio** : динамическое управление аудиоустройствами.
* **Mutter / Wayland DisplayConfig** : нативное переключение разрешений и позиционирование мониторов.

## Зависимости

* Python 3.10+
* PySide6 (Qt 6.5+)
* psutil (мониторинг накопителей и процессов)
* dbus-next / jeepney (асинхронное взаимодействие с D-Bus)

## Лицензия

GNU General Public License v3.0 (GPLv3). Подробнее в файле [LICENSE](LICENSE).

Автор: **[@dezaetterg](https://github.com/dezaetterg)**
