from PyQt5.QtWidgets import *

from cvrp.ui.mixins import OnCloseCallbackMixin


class PlaceFormWidget(QWidget):
    def __init__(self, *args, **kwargs):
        self._place = kwargs.pop("place")
        self._is_depot = kwargs.pop("is_depot", False)

        super().__init__(*args, **kwargs)

        self.layout = QFormLayout()
        self.setLayout(self.layout)

        self.name_input = QLineEdit()
        self.name_input.setText(self._place.name)
        self.layout.addRow("Nazwa", self.name_input)

        self.lat_input = QDoubleSpinBox()
        self.lat_input.setMinimum(-90.0)
        self.lat_input.setMaximum(90.0)
        self.lat_input.setSingleStep(0.1)
        self.lat_input.setValue(self._place.latitude)
        self.layout.addRow("Długość geo.", self.lat_input)

        self.lng_input = QDoubleSpinBox()
        self.lng_input.setMinimum(-180.0)
        self.lng_input.setMaximum(180.0)
        self.lng_input.setSingleStep(0.1)
        self.lng_input.setValue(self._place.longitude)
        self.layout.addRow("Szerokość geo.", self.lng_input)

        if not self._is_depot:
            self.demand_input = QDoubleSpinBox()
            self.demand_input.setMinimum(0.1)
            self.demand_input.setValue(self._place.demand)
            self.layout.addRow("Zapotrzebowanie", self.demand_input)

        self.save_button = QPushButton("Zapisz")
        self.save_button.clicked.connect(self.save_place)
        self.layout.addWidget(self.save_button)

    def save_place(self):
        self._place.name = self.name_input.text()
        self._place.latitude = self.lat_input.value()
        self._place.longitude = self.lng_input.value()
        self._place.demand = 0.0 if self._is_depot else self.demand_input.value()

        self.window().close()


class PlaceFormWindow(OnCloseCallbackMixin, QMainWindow):
    def closeEvent(self, event):
        self.on_close()
        super().closeEvent(event)

    def __init__(self, *args, **kwargs):
        self._place = kwargs.pop("place")
        self._is_depot = kwargs.pop("is_depot", False)

        super().__init__(*args, **kwargs)

        self.setWindowTitle("Edytuj miejsce")
        self.setFixedSize(300, 150)

        self.main_widget = PlaceFormWidget(place=self._place, is_depot=self._is_depot)
        self.setCentralWidget(self.main_widget)
