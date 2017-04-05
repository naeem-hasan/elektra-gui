from PyQt4 import QtGui, QtCore, uic
from elektra import ElektraSearch
from PIL import ImageQt
from os.path import join, dirname, realpath, expanduser


class ElektraMainWindow(QtGui.QMainWindow):
    GRID_SIZES = [(7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14)]
    BOX_SIZES = [(50, 50), (60, 60), (70, 70), (80, 80), (90, 90), (100, 100)]
    FONT_SIZES = [20, 30, 40, 50, 60, 70]
    ITERATIONS = [10, 20, 30, 50, 80, 100]

    def __init__(self):
        super(ElektraMainWindow, self).__init__()
        uic.loadUi('elektra_main.ui', self)

        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(QtGui.QPixmap(":/window/bg.jpg")))
        self.setPalette(palette)

        self.connect_events()
        self.initialize()
        self.display_puzzle()

        self.showMaximized()
        self.elektra_status.showMessage("Elektra is at your service :)")

    def connect_events(self):
        self.button_add_word.clicked.connect(self.add_word)
        self.button_remove_word.clicked.connect(self.remove_word)
        self.button_render_photo.clicked.connect(self.render_photo)
        self.button_make_puzzle.clicked.connect(self.make_puzzle)
        self.button_border_color.clicked.connect(self.get_border_color)
        self.button_font_color.clicked.connect(self.get_font_color)
        self.button_font_path.clicked.connect(self.get_font_path)
        self.check_border.stateChanged.connect(self.border_state_changed)
        self.about_button.clicked.connect(self.show_about)
        self.button_export.clicked.connect(self.export_puzzle)
        self.button_export_sol.clicked.connect(self.export_solution)

    def border_state_changed(self, i):
        self.combo_border.setEnabled(bool(i))
        self.label_border.setEnabled(bool(i))
        self.button_border_color.setEnabled(bool(i))

    def get_font_path(self):
        file_name = QtGui.QFileDialog.getOpenFileName(self.main_widget, "Open font file", "", "Font files (*.ttf *.otf)")
        if file_name:
            self.font_path = file_name
            self.elektra_status.showMessage("New font chosen!")
        else:
            self.elektra_status.showMessage("Font not chosen!")

    def get_font_color(self):
        color = QtGui.QColorDialog.getColor(QtGui.QColor(*self.font_color))
        self.font_color = (color.red(), color.green(), color.blue())
        self.elektra_status.showMessage("Font color set to %r!" % self.font_color)

    def get_border_color(self):
        color = QtGui.QColorDialog.getColor(QtGui.QColor(*self.border_color))
        self.border_color = (color.red(), color.green(), color.blue())
        self.elektra_status.showMessage("Border color set to %r!" % self.border_color)

    def load_variables(self):
        self.words = [str(self.list_words.item(i).text()) for i in range(self.list_words.count())]
        self.difficulty = self.combo_difficulty.currentIndex()
        self.grid_size = ElektraMainWindow.GRID_SIZES[self.combo_grid_size.currentIndex()]
        self.box_size = ElektraMainWindow.BOX_SIZES[self.combo_box_size.currentIndex()]
        self.use_capital = self.check_capital.isChecked()
        self.use_shade = self.check_shade.isChecked()
        self.use_border = self.check_border.isChecked()
        self.border_width = self.combo_border.currentIndex() + 1
        self.font_size = ElektraMainWindow.FONT_SIZES[self.combo_font_size.currentIndex()]
        self.iterations = ElektraMainWindow.ITERATIONS[self.combo_iterations.currentIndex()]

    def initialize(self):
        self.font_path = join(dirname(realpath(__file__)), ElektraSearch.DEFAULT_FONT)
        self.border_color = (62, 44, 26)
        self.font_color = (255, 255, 255)
        self.puzzle = ElektraSearch()
        self.puzzle_image = self.puzzle.get_image()

    def clear_layout(self):
        for i in reversed(range(self.verticalLayout_9.count())):
            self.verticalLayout_9.itemAt(i).widget().setParent(None)

    def display_puzzle(self):
        self.clear_layout()
        self.scene = QtGui.QGraphicsScene(self.main_widget)
        self.graphics_view = GraphicsView(self.scene)
        self.verticalLayout_9.addWidget(self.graphics_view)
        w, h = self.puzzle_image.size
        self.imgQ = ImageQt.ImageQt(self.puzzle_image)
        pixMap = QtGui.QPixmap.fromImage(self.imgQ)
        self.scene.addPixmap(pixMap)
        self.graphics_view.fitInView(QtCore.QRectF(0, 0, w, h), QtCore.Qt.KeepAspectRatio)
        self.scene.update()

    def add_word(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Input word', 'Enter a new word:')
        if ok:
            self.list_words.addItem(text)
            self.elektra_status.showMessage("%s added to the list" % text)
        self.list_words.setItemSelected(self.list_words.currentItem(), False)

    def remove_word(self):
        text = self.list_words.currentItem().text()
        self.list_words.takeItem(self.list_words.row(self.list_words.currentItem()))
        self.list_words.setItemSelected(self.list_words.currentItem(), False)
        self.elektra_status.showMessage("%s removed from the list" % text)

    def make_puzzle(self):
        self.load_variables()
        self.puzzle.clear_words()
        self.puzzle.add_words(*self.words)
        self.puzzle.set_difficulty(self.difficulty)
        self.puzzle.set_grid_size(self.grid_size)
        self.puzzle.set_iterations(self.iterations)
        self.puzzle.make_puzzle()
        self.render_photo()

    def render_photo(self):
        self.load_variables()
        self.puzzle.set_box_size(self.box_size)
        self.puzzle.use_capital(self.use_capital)
        self.puzzle.use_shade(self.use_shade)
        self.puzzle.use_border(self.use_border)
        self.puzzle.set_border_width(self.border_width)
        self.puzzle.set_font_size(self.font_size)
        self.puzzle.set_font_path(self.font_path)
        self.puzzle.set_font_color(self.font_color)
        self.puzzle.set_border_color(self.border_color)
        self.puzzle.render_image()
        self.puzzle_image = self.puzzle.get_image()
        self.display_puzzle()
        self.display_solutions()
        if self.puzzle.words:
            self.elektra_status.showMessage("Puzzle successfully rendered!")
        else:
            self.elektra_status.showMessage("Puzzle rendered, but there are no words!")

    def display_solutions(self):
        self.list_solutions.clear()
        try:
            for x in self.puzzle.get_solutions():
                self.list_solutions.addItem("%s : %r, %s" % (x[0], (x[1][0] + 1, x[1][1] + 1), x[2]))
        except:
            pass

    def export_puzzle(self):
        file_name, filter = QtGui.QFileDialog.getSaveFileNameAndFilter(self.main_widget, "Export word search", join(expanduser("~"), "word search.png"), "PNG image (*.png);;JPG image (*.jpg *.jpeg)")
        if ".jpg" in str(filter):
            form = ".jpg"
        else:
            form = ".png"
        if file_name:
            file_name = str(file_name)
            if not file_name.endswith(form):
                file_name = file_name + form
            self.puzzle.save_image(file_name)
            self.elektra_status.showMessage("Puzzle successfully exported to: %s" % file_name)

    def export_solution(self):
        file_name = QtGui.QFileDialog.getSaveFileName(self.main_widget, "Export word search solutions", join(expanduser("~"), "search solutions.txt"), "Text file (*.txt)")
        if file_name:
            sol = "\n".join(["%s : %r, %s" % (x[0], (x[1][0] + 1, x[1][1] + 1), x[2]) for x in self.puzzle.get_solutions()])
            with open(file_name, 'w') as e:
                e.write(sol)
                e.close()
            self.elektra_status.showMessage("Solution successfully exported to: %s" % file_name)

    def show_about(self):
        QtGui.QMessageBox.about(self.main_widget, "About Elektra", "Elektra<br><br>A simple yet powerful word search generator.\n<br>Developer: Naeem Hasan<br><a href='http://naeemhasan.tk'>My website...</a><br><a href='http://www.facebook.com/wizard.naeemhasan'>I am on Facebook...</a><br><a href='http://github.com/naeem-hasan'>I am on GitHub...</a>")


class GraphicsView(QtGui.QGraphicsView):
    def __init__(self, parent=None):
        super(GraphicsView, self).__init__(parent)

    def wheelEvent(self, event):
        factor = 1.41 ** (event.delta() / 240.0)
        self.scale(factor, factor)


if __name__ == '__main__':
    from sys import exit, argv
    import icons
    app = QtGui.QApplication(argv)
    window = ElektraMainWindow()
    exit(app.exec_())
