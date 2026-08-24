from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QStackedWidget, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QParallelAnimationGroup, QSequentialAnimationGroup, QEasingCurve, QTimer, QPoint
from PySide6.QtGui import QPainter, QColor, QPen
from theme.colors import Colors
from theme.typography import Typography
from components.network_cards import NetworkSummaryCard, InterfaceCard
from services.network_service import NetworkService
from pages.network_details import NetworkDetailsPage
from theme.manager import ThemeManager
from theme.styler import fix_label_styles

class EmptyNetworkIcon(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 80)
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        color = QColor(Colors.TEXT_SECONDARY)
        color.setAlpha(150)
        p.setPen(QPen(color, 2))
        
        cx, cy = self.width()/2, self.height()/2
        
        p.drawEllipse(cx-20, cy-20, 40, 40)
        p.drawEllipse(cx-10, cy-20, 20, 40)
        p.drawLine(cx-20, cy, cx+20, cy)
        p.drawLine(cx-17, cy-10, cx+17, cy-10)
        p.drawLine(cx-17, cy+10, cx+17, cy+10)

class NetworkListPage(QWidget):
    details_requested = Signal(str, str) # interface, connection_name
    
    def __init__(self, service: NetworkService):
        super().__init__()
        self.service = service
        self.entrance_anim_group = QParallelAnimationGroup(self)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        self.content = QWidget()
        self.content.setStyleSheet("background: transparent;")
        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(40, 30, 40, 40)
        self.layout.setSpacing(24)
        self.layout.setAlignment(Qt.AlignTop)
        
        self.layout.addStretch()
        
        scroll.setWidget(self.content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(scroll)
        
        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)

    def update_style(self, _is_dark=False):
        fix_label_styles(self)
        self.update()
        
        self.refresh_connections()
        
    def refresh_connections(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        global_status = self.service.backend.get_global_status()
        networks = self.service.get_ethernet_connections()
        
        self.animated_widgets = []
        
        # 0. Header Title
        from localization import t
        title = QLabel(t("nav.network", "Network"))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_HEADER}px; font-weight: {Typography.WEIGHT_BOLD};")
        self.layout.addWidget(title)

        self.summary_card = NetworkSummaryCard(global_status)
        self.layout.addWidget(self.summary_card)
        self.animated_widgets.append(self.summary_card)
        
        if networks:
            conn_lbl = QLabel(t("network.interfaces", "INTERFACES"))
            conn_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_NORMAL}; font-size: {Typography.SIZE_SMALL}px; margin-left: 15px; margin-top: 10px; letter-spacing: 0.5px;")
            self.layout.addWidget(conn_lbl)
            self.animated_widgets.append(conn_lbl)
            
            for net in networks:
                card = InterfaceCard(
                    interface=net['interface'],
                    name=net['name'],
                    active=net['active'],
                    ipv4=net['ipv4'],
                    speed=net['link_speed'],
                    icon_type=net['type'],
                    mac=net.get('mac', 'Unavailable')
                )
                card.details_clicked.connect(self.details_requested.emit)
                self.layout.addWidget(card)
                self.animated_widgets.append(card)
        else:
            empty_container = QWidget()
            empty_layout = QVBoxLayout(empty_container)
            empty_layout.setAlignment(Qt.AlignCenter)
            empty_layout.setSpacing(16)
            empty_layout.setContentsMargins(0, 40, 0, 0)
            
            icon = EmptyNetworkIcon()
            lbl = QLabel(t("network.no_interfaces", "No Ethernet interfaces detected"))
            lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_BODY}px;")
            
            empty_layout.addWidget(icon, 0, Qt.AlignCenter)
            empty_layout.addWidget(lbl, 0, Qt.AlignCenter)
            
            self.layout.addWidget(empty_container)
            self.animated_widgets.append(empty_container)
            
        self.layout.addStretch()
        
        # Prepare real animations
        self.entrance_anim_group.clear()
        
        delay = 0
        for w in self.animated_widgets:
            eff = QGraphicsOpacityEffect(w)
            eff.setOpacity(0.0)
            w.setGraphicsEffect(eff)
            
            # Opacity animation
            anim_op = QPropertyAnimation(eff, b"opacity")
            anim_op.setDuration(250)
            anim_op.setStartValue(0.0)
            anim_op.setEndValue(1.0)
            anim_op.setEasingCurve(QEasingCurve.OutQuad)
            
            # Delay wrapper
            seq = QSequentialAnimationGroup()
            seq.addPause(delay)
            seq.addAnimation(anim_op)
            
            self.entrance_anim_group.addAnimation(seq)
            delay += 40

    def showEvent(self, event):
        super().showEvent(event)
        self.entrance_anim_group.stop()
        for w in self.animated_widgets:
            if w.graphicsEffect():
                w.graphicsEffect().setOpacity(0.0)
        self.entrance_anim_group.start()

class NetworkPage(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.service = NetworkService()
        
        self.list_page = NetworkListPage(self.service)
        self.list_page.details_requested.connect(self.show_details)
        
        self.addWidget(self.list_page)
        self.current_details_page = None
        
    def show_details(self, interface, connection_name):
        details = self.service.get_connection_details(interface, connection_name)
        
        if self.current_details_page:
            self.removeWidget(self.current_details_page)
            self.current_details_page.deleteLater()
            
        self.current_details_page = NetworkDetailsPage(details, parent_page_name="Network")
        self.current_details_page.back_requested.connect(self.show_list)
        self.addWidget(self.current_details_page)
        self.setCurrentWidget(self.current_details_page)
        
    def show_list(self):
        self.setCurrentWidget(self.list_page)

    def reset_to_root(self):
        self.show_list()

    def showEvent(self, event):
        super().showEvent(event)
        self.show_list()

    def get_search_target(self, target_id: str) -> QWidget | None:
        self.setCurrentWidget(self.list_page)
        targets = {
            "network.status": getattr(self.list_page, "summary_card", None),
            "network.interfaces": getattr(self.list_page, "summary_card", None),
        }
        return targets.get(target_id)
