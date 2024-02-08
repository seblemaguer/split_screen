from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy

class ParticipantWindow(QWidget):
    """The window presented to the participant

    It only contains a word presented in fullscreen.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Participant window")

        # Define the label
        self._label = QLabel("Default")
        font = self._label.font()
        font.setPointSize(100)
        self._label.setFont(font)
        self._label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # Set the central widget of the Window.

        # Create a QHBoxLayout instance
        self._layout = QHBoxLayout()
        self._layout.addWidget(self._label)
        self._label.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Expanding
        )
        self.setLayout(self._layout)


    def update_word(self, word):
        """Helper to update the word in the label

        parameters
        ----------
        word: str
           The new word to display
        """
        self._label.setText(word)
