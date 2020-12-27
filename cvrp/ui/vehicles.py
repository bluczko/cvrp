from PyQt5.QtWidgets import *

from cvrp.ui.mixins import OnCloseCallbackMixin


class VehicleFormWidget(QWidget):
    def __init__(self, *args, **kwargs):
        self._vehicle = kwargs.pop("vehicle")

        super().__init__(*args, **kwargs)

        self.layout = QFormLayout()
        self.setLayout(self.layout)

        self.name_input = QLineEdit()
        self.name_input.setText(self._vehicle.name)
        self.layout.addRow("Nazwa", self.name_input)

        self.max_capacity_input = QDoubleSpinBox()
        self.max_capacity_input.setMinimum(0.1)
        self.max_capacity_input.setSingleStep(0.1)
        self.max_capacity_input.setValue(self._vehicle.max_capacity)
        self.layout.addRow("Maks. pojemność", self.max_capacity_input)

        self.save_button = QPushButton("Zapisz")
        self.save_button.clicked.connect(self.save_vehicle)
        self.layout.addWidget(self.save_button)

    def save_vehicle(self):
        self._vehicle.name = self.name_input.text()
        self._vehicle.max_capacity = self.max_capacity_input.value()

        self.window().close()


class VehicleFormWindow(OnCloseCallbackMixin, QMainWindow):
    def closeEvent(self, event):
        self.on_close()
        super().closeEvent(event)

    def __init__(self, *args, **kwargs):
        self._vehicle = kwargs.pop("vehicle")

        super().__init__(*args, **kwargs)

        self.setWindowTitle("Edytuj pojazd")
        self.setFixedSize(300, 150)

        self.main_widget = VehicleFormWidget(vehicle=self._vehicle)
        self.setCentralWidget(self.main_widget)
