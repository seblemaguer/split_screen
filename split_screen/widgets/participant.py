import logging
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy, QStackedWidget
from PyQt5.QtGui import QKeyEvent


class ParticipantWindow(QWidget):
    """The window presented to the participant

    It only contains a word presented in fullscreen.
    """

    FEEDBACK_DURATION = 3000  # ms

    def __init__(self):
        """Initialisation

        Creates the widget and allocate the evaluator UI handle
        """
        super().__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
        self.setWindowTitle("Participant window")

        # Create a QHBoxLayout instance
        self._layout = QHBoxLayout()
        self._wrapping_widget = QStackedWidget()
        self._layout.addWidget(self._wrapping_widget)
        self.setLayout(self._layout)

        # Define and add the word label
        self._word_label = QLabel("Default")
        font = self._word_label.font()
        font.setPointSize(100)
        self._word_label.setFont(font)
        self._word_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self._word_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self._wrapping_widget.addWidget(self._word_label)

        # Define and add the wait for feedback label
        self._waiting_feedback_label = QLabel("Waiting for feedbacks....")
        font = self._waiting_feedback_label.font()
        font.setPointSize(80)
        self._waiting_feedback_label.setFont(font)
        self._waiting_feedback_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self._waiting_feedback_label.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Expanding
        )
        self._wrapping_widget.addWidget(self._waiting_feedback_label)

        # Define and add the wait for feedback label
        self._feedback_label = QLabel("")
        font = self._feedback_label.font()
        font.setPointSize(80)
        self._feedback_label.setFont(font)
        self._feedback_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self._feedback_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self._wrapping_widget.addWidget(self._feedback_label)
        self._wrapping_widget.setCurrentIndex(0)

        # Handle to the evaluator UI to be able to indicate end of reading
        self._evaluator_window = None

    def showFeedback(self):
        self._wrapping_widget.setCurrentIndex(2)
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self.moveOn)
        timer.start(ParticipantWindow.FEEDBACK_DURATION)

    def moveOn(self):
        self._wrapping_widget.setCurrentIndex(0)

    def setFeedback(self, word: str):
        if word == "":
            text = "<div style='text-align: center;'>"
            text += "The listener didn't understand<br> the word"
            text += "</div>"
        else:
            text = "<div style='text-align: center;'>"
            text += "The listener heard the word<br>"
            text += f"\"<span style='font-weight:bold;'>{word}</span>\"<br>"
            text += "</div>"
        self._feedback_label.setText(text)

        self.showFeedback()

    def setEvaluatorWindow(self, evaluator_window: QWidget):
        """Set the evaluator widget to be able to signal end of reading

        Parameters
        ----------
        evaluator_ui : QWidget
            the evaluator widget
        """
        self._evaluator_window = evaluator_window

    def setWord(self, word: str):
        """Helper to update the word in the label

        parameters
        ----------
        word: str
           The new word to display
        """
        self._word_label.setText(word)

    def endReading(self):
        """Signal the end of the reading

        This triggers the evaluator window to be ready for the capture

        """
        self._wrapping_widget.setCurrentIndex(1)
        self._evaluator_window.activateWindow()
        self._evaluator_window.startCapture()

    def keyPressEvent(self, event: QKeyEvent):
        """Keyboard event handler

        Only space is captured and signal the end of the reading

        Parameters
        ----------
        event: QKeyEvent
            the captured event

        """
        if event.key() == Qt.Key_Space:
            if self._wrapping_widget.currentIndex() == 0:
                self.endReading()
            else:
                self._logger.info("Key pressed when not allowed!")

        if event.key() == Qt.Key_F4 and event.modifiers() == Qt.AltModifier:
            print("Alt+F4 pressed")

    def closeEvent(self, event):
        event.ignore()

        self._evaluator_window.end_serialization()
        import sys
        sys.exit(0)
