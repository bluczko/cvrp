from PyQt5.QtWidgets import *


class MainTabWidget(QTabWidget):
    def __init__(self, *args, **kwargs):
        super(MainTabWidget, self).__init__(*args, **kwargs)

        self.places_tab = QWidget(self)
        self.addTab(self.places_tab, "Miejsca")

        self.vehicles_tab = QWidget(self)
        self.addTab(self.vehicles_tab, "Pojazdy")


class MainWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)

        self.layout = QVBoxLayout()
        self.tabs = MainTabWidget(self)
        self.solve = QPushButton("Rozwiąż problem")

        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.solve)
        self.setLayout(self.layout)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("CVRP")
        self.setGeometry(100, 100, 800, 600)
        self.setCentralWidget(MainWidget(self))


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
