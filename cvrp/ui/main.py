import sys

from PyQt5.QtWidgets import *

from cvrp.data import Network, Place
from cvrp.ui.places import PlaceFormWindow


class PlaceListItem(QListWidgetItem):
    def __init__(self, place, removable=True):
        super().__init__(place.name)
        self.place = place
        self.removable = removable


class PlaceList(QListWidget):
    def __init__(self, *args, **kwargs):
        self._network = kwargs.pop("network")

        super(PlaceList, self).__init__(*args, **kwargs)
        self.setSelectionMode(QListWidget.SingleSelection)

        self.update_places()

    def update_places(self):
        self.clear()

        for place in self._network.all_places:
            self.addItem(PlaceListItem(place))


class PlacesTabWidget(QWidget):
    def __init__(self, *args, **kwargs):
        self._network = kwargs.pop("network")

        super(PlacesTabWidget, self).__init__(*args, **kwargs)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # Action buttons panel ############################
        self.action_buttons = QWidget(self)
        self.layout.addWidget(self.action_buttons)

        self.ab_layout = QHBoxLayout()
        self.action_buttons.setLayout(self.ab_layout)

        self.ab_add_place = QPushButton("Dodaj")
        self.ab_add_place.clicked.connect(self.add_place)
        self.ab_layout.addWidget(self.ab_add_place)

        self.ab_edit_place = QPushButton("Edytuj")
        self.ab_edit_place.clicked.connect(self.edit_place)
        self.ab_layout.addWidget(self.ab_edit_place)

        self.ab_remove_place = QPushButton("Usuń")
        self.ab_remove_place.clicked.connect(self.remove_place)
        self.ab_layout.addWidget(self.ab_remove_place)

        self.ab_layout.addStretch()

        # Places list #####################################
        self.places_list = PlaceList(network=self._network)
        self.layout.addWidget(self.places_list)

        self.places_list.itemClicked.connect(self.update_action_buttons)
        self.update_action_buttons(None)

        self.places_list.itemDoubleClicked.connect(self.edit_place)

    def add_place(self):
        new_index = len(self._network.clients) + 1
        new_place = Place(f"Nowy klient ({new_index})", 0.0, 0.0)
        self._network.add_client(new_place)

        form_window = PlaceFormWindow(self, place=new_place)
        form_window.set_on_close(self.places_list.update_places)
        form_window.show()

    def edit_place(self):
        item = self.places_list.currentItem()

        if item is None or not hasattr(item, "place"):
            return

        form_window = PlaceFormWindow(self, place=item.place, is_depot=(item.place == self._network.depot))
        form_window.set_on_close(self.places_list.update_places)
        form_window.show()

    def remove_place(self):
        item = self.places_list.currentItem()

        if item is None or not hasattr(item, "place"):
            return

        self._network.remove_client(item.place)
        self.places_list.update_places()

    def update_action_buttons(self, item):
        is_item_invalid = item is None or not hasattr(item, "place")

        self.ab_remove_place.setDisabled(is_item_invalid)
        self.ab_edit_place.setDisabled(is_item_invalid)

        if is_item_invalid:
            return

        is_depot_selected = item.place == self._network.depot

        self.ab_remove_place.setDisabled(is_depot_selected)


class MainTabWidget(QTabWidget):
    def __init__(self, *args, **kwargs):
        self._network = kwargs.pop("network")

        super(MainTabWidget, self).__init__(*args, **kwargs)

        self.places_tab = PlacesTabWidget(self, network=self._network)
        self.addTab(self.places_tab, "Miejsca")

        self.vehicles_tab = QWidget(self)
        self.addTab(self.vehicles_tab, "Pojazdy")


class MainWidget(QWidget):
    def __init__(self, *args, **kwargs):
        self._network = kwargs.pop("network")

        super(MainWidget, self).__init__(*args, **kwargs)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.tabs = MainTabWidget(self, network=self._network)
        self.layout.addWidget(self.tabs)

        self.solve = QPushButton("Rozwiąż problem")
        self.layout.addWidget(self.solve)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        self._network = kwargs.pop("network", Network())

        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("CVRP")
        self.setFixedSize(600, 400)

        self.main_widget = MainWidget(self, network=self._network)
        self.setCentralWidget(self.main_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
