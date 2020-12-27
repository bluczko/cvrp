import sys

from PyQt5.QtWidgets import *

from cvrp.data import Network, Place, Vehicle
from cvrp.exceptions import CVRPException
from cvrp.model import get_solvers
from cvrp.ui.places import PlaceFormWindow
from cvrp.ui.vehicles import VehicleFormWindow


class ListTabWidget(QWidget):
    list_class = QListWidget

    def __init__(self, *args, **kwargs):
        self._network = kwargs.pop("network")

        super().__init__(*args, **kwargs)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # Action buttons panel ############################
        self.action_buttons = QWidget(self)
        self.layout.addWidget(self.action_buttons)

        self.ab_layout = QHBoxLayout()
        self.action_buttons.setLayout(self.ab_layout)

        self.ab_add = QPushButton("Dodaj")
        self.ab_add.clicked.connect(self.__add_item)
        self.ab_layout.addWidget(self.ab_add)

        self.ab_edit = QPushButton("Edytuj")
        self.ab_edit.clicked.connect(self.__edit_item)
        self.ab_layout.addWidget(self.ab_edit)

        self.ab_remove = QPushButton("Usuń")
        self.ab_remove.clicked.connect(self.__remove_item)
        self.ab_layout.addWidget(self.ab_remove)

        self.ab_layout.addStretch()

        # Items list #####################################
        self.items_list = self.list_class(network=self._network)
        self.layout.addWidget(self.items_list)

        self.items_list.itemClicked.connect(self.update_action_buttons)
        self.update_action_buttons(None)

        self.items_list.itemDoubleClicked.connect(self.__edit_item)

    def __add_item(self):
        if hasattr(self, "on_item_add"):
            self.on_item_add()

    def __edit_item(self):
        item = self.items_list.currentItem()

        if item is not None and hasattr(self, "on_item_edit"):
            self.on_item_edit(item=item)

    def __remove_item(self):
        item = self.items_list.currentItem()

        if item is not None and hasattr(self, "on_item_remove"):
            self.on_item_remove(item=item)

    def is_selected_item_valid(self, item):
        return item is not None

    def update_action_buttons(self, item):
        is_item_invalid = self.is_selected_item_valid(item) is False

        self.ab_remove.setDisabled(is_item_invalid)
        self.ab_edit.setDisabled(is_item_invalid)


class PlaceListItem(QListWidgetItem):
    def __init__(self, place, removable=True):
        super().__init__(place.name)
        self.place = place
        self.removable = removable


class PlaceList(QListWidget):
    def __init__(self, *args, **kwargs):
        self._network = kwargs.pop("network")

        super().__init__(*args, **kwargs)
        self.setSelectionMode(QListWidget.SingleSelection)
        self.update_places()

    def update_places(self):
        self.clear()

        for place in self._network.all_places:
            self.addItem(PlaceListItem(place))


class PlacesTabWidget(ListTabWidget):
    list_class = PlaceList

    def __on_editor_close(self):
        self.items_list.update_places()
        self.update_action_buttons(None)

    def on_item_add(self):
        new_index = len(self._network.clients) + 1
        new_place = Place(f"Nowy klient ({new_index})", 0.0, 0.0)
        self._network.add_client(new_place)

        form_window = PlaceFormWindow(self, place=new_place)
        form_window.set_on_close(self.__on_editor_close)
        form_window.show()

    def on_item_edit(self, item):
        form_window = PlaceFormWindow(self, place=item.place, is_depot=(item.place == self._network.depot))
        form_window.set_on_close(self.__on_editor_close)
        form_window.show()

    def on_item_remove(self, item):
        self._network.remove_client(item.place)
        self.__on_editor_close()

    def update_action_buttons(self, item):
        super().update_action_buttons(item)

        if self.is_selected_item_valid(item):
            is_depot_selected = item.place == self._network.depot
            self.ab_remove.setDisabled(is_depot_selected)


class VehicleListItem(QListWidgetItem):
    def __init__(self, vehicle):
        super().__init__(vehicle.name)
        self.vehicle = vehicle


class VehicleList(QListWidget):
    def __init__(self, *args, **kwargs):
        self._network = kwargs.pop("network")

        super().__init__(*args, **kwargs)
        self.setSelectionMode(QListWidget.SingleSelection)
        self.update_vehicles()

    def update_vehicles(self):
        self.clear()

        for vehicle in self._network.vehicles:
            self.addItem(VehicleListItem(vehicle))


class VehiclesTabWidget(ListTabWidget):
    list_class = VehicleList

    def __on_editor_close(self):
        self.items_list.update_vehicles()
        self.update_action_buttons(None)

    def on_item_add(self):
        new_index = len(self._network.vehicles) + 1
        new_vehicle = Vehicle(f"Nowy pojazd ({new_index})", 1.0)
        self._network.add_vehicle(new_vehicle)

        form_window = VehicleFormWindow(self, vehicle=new_vehicle)
        form_window.set_on_close(self.__on_editor_close)
        form_window.show()

    def on_item_edit(self, item):
        form_window = VehicleFormWindow(self, vehicle=item.vehicle)
        form_window.set_on_close(self.__on_editor_close)
        form_window.show()

    def on_item_remove(self, item):
        self._network.remove_vehicle(item.vehicle)
        self.__on_editor_close()


class MainTabWidget(QTabWidget):
    def __init__(self, *args, **kwargs):
        self._network = kwargs.pop("network")

        super(MainTabWidget, self).__init__(*args, **kwargs)

        self.places_tab = PlacesTabWidget(self, network=self._network)
        self.addTab(self.places_tab, "Miejsca")

        self.vehicles_tab = VehiclesTabWidget(self, network=self._network)
        self.addTab(self.vehicles_tab, "Pojazdy")


class MainWidget(QWidget):
    def on_click_solve(self):
        self.solve.setDisabled(True)

        try:
            self._network.check_solvability()
        except CVRPException as exc:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Błąd")
            msg.setText(exc.message)
            msg.exec_()

        self.solve.setDisabled(False)

    def __init__(self, *args, **kwargs):
        self._network = kwargs.pop("network")

        super(MainWidget, self).__init__(*args, **kwargs)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.tabs = MainTabWidget(self, network=self._network)
        self.layout.addWidget(self.tabs)

        self.solve = QPushButton("Rozwiąż problem")
        self.solve.clicked.connect(self.on_click_solve)
        self.layout.addWidget(self.solve)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        self._network = kwargs.pop("network", Network())

        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Problem marszrutyzacji")
        self.setFixedSize(600, 400)

        self.main_widget = MainWidget(self, network=self._network)
        self.setCentralWidget(self.main_widget)


def launch_ui():
    app = QApplication(sys.argv)
    main = MainWindow()

    try:
        get_solvers()
    except EnvironmentError:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Błąd")
        msg.setText("Brak dostępnych solverów")
        msg.exec_()
        return

    main.show()
    sys.exit(app.exec())
