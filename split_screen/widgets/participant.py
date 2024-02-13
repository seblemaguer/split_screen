from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QKeyEvent

class ParticipantWindow(QWidget):
    """The window presented to the participant

    It only contains a word presented in fullscreen.
    """
    def __init__(self):
        """Initialisation

        Creates the widget and allocate the evaluator UI handle
        """
        super().__init__()

        self.setWindowTitle("Participant window")

        # Define the label
        self._label = QLabel("Default")
        font = self._label.font()
        font.setPointSize(100)
        self._label.setFont(font)
        self._label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # Create a QHBoxLayout instance
        self._layout = QHBoxLayout()
        self._layout.addWidget(self._label)
        self._label.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Expanding
        )
        self.setLayout(self._layout)

        # Handle to the evaluator UI to be able to indicate end of reading
        self._evaluator_ui = None

    def setEvaluatorUI(self, evaluator_ui: QWidget):
        """Set the evaluator widget to be able to signal end of reading

        Parameters
        ----------
        evaluator_ui : QWidget
            the evaluator widget
        """
        self._evaluator_ui = evaluator_ui

    def setWord(self, word: str):
        """Helper to update the word in the label

        parameters
        ----------
        word: str
           The new word to display
        """
        self._label.setText(word)

    def endReading(self):
        """Signal the end of the reading

        This triggers the evaluator window to be ready for the capture

        """
        self._evaluator_ui.activateWindow()
        self._evaluator_ui.startCapture()

    def keyPressEvent(self, event: QKeyEvent):
        """Keyboard event handler

        Only space is captured and signal the end of the reading

        Parameters
        ----------
        event: QKeyEvent
            the captured event

        """
        if event.key() == Qt.Key_Space:
            self.endReading()
