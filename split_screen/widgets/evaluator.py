# Python
import pathlib
import logging
import datetime

# UI
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
)
from PyQt5.QtGui import QKeyEvent, QFont

# Data
import pandas as pd


class EvaluatorWindow(QWidget):
    """The window presented to the evaluator

    It contains 2 buttons (left and right) which shows two potential words. The evaluator has to click on one of this word to move to the next step
    """

    def __init__(
        self,
        word_list_file: pathlib.Path,
        result_file: pathlib.Path,
        participant_window: QWidget,
        n_decks: int = 10,
        random_overall: bool = False,
    ):
        super().__init__()

        # Initialise some helpers
        self._participant_window = participant_window
        self._logger = logging.getLogger(self.__class__.__name__)
        self.setWindowTitle("Evaluator window")

        # Load words ad prepare decks
        self._current_index = -1
        self._word_df = pd.read_csv(word_list_file, sep="\t")
        self._word_df = pd.concat(
            [self._word_df.sample(frac=1) for _ in range(n_decks)]
        )

        if random_overall:
            self._word_df = self._word_df.sample(frac=1)
        self._word_df = self._word_df.reset_index(drop=True)


        # Prepare the two panels (hidden for now)
        self._word_panel = WordPanel(self, "", "")  # FIXME: define the words

        # Define the wrapping widget to facilitate hide/show of the controls
        self._wrapping_widget = QStackedWidget()
        wrapping_layout = QHBoxLayout()
        wrapping_layout.addWidget(self._wrapping_widget)
        self._wrapping_widget.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Expanding
        )
        self._wrapping_widget.hide()
        self.setLayout(wrapping_layout)

        #
        self._wrapping_widget.addWidget(self._word_panel)

        # Prepare the output data serialisation
        self._result_file_handle = open(result_file, "w")
        self._result_file_handle.write(
            "step_idx\tstart_scoring_timestamp\treceived_score_timestamp\tspoken_word\tperceived_word\n"
        )

        # Ok ready, steady, go!
        self.moveToNext()

    def startCapture(self):
        """Helper to prepare the judgement stage of the evaluation

        This function is called by an external widget (the participant one)
        """
        self._logger.debug("Ready to capture")
        self._wrapping_widget.show()
        self._start_timer = datetime.datetime.now()

    def moveToNext(self):
        """Prepare the next step of the evaluation

        This function triggers the following sequence:
           1. hide anything from the evaluator to avoid any unwanted interactions
           2. ensure that there is more evaluation to be done:
              - if not just quit
              - if yes select the next word and move the focus to the participant window
        """
        # End the step
        current_time = datetime.datetime.now()
        self._wrapping_widget.hide()
        if self._current_index >= 0:
            self._serializeSelection(
                current_time,
                self._word_df.loc[self._current_index, "Stimulus"],
                self._word_panel.selected_word,
            )
            # Prepare the feedback to the participant
            self._participant_window.setFeedback(self._word_panel.selected_word)

        # Check if we are at the end or not
        self._current_index += 1
        if self._current_index >= len(
            self._word_df.index
        ):  # FIXME: a bit hardcore for quitting no ?
            self._result_file_handle.close()
            import sys

            sys.exit(0)

        # Prepare the next step
        self._word_panel.updateWords(
            self._word_df.loc[self._current_index, "Short"],
            self._word_df.loc[self._current_index, "Long"],
        )
        self._wrapping_widget.setCurrentIndex(0)

        # Prepare and activate the participant window
        self._participant_window.setWord(
            self._word_df.loc[self._current_index, "Stimulus"]
        )
        self._participant_window.activateWindow()

    def _serializeSelection(self, response_time, spoken_word, perceived_word):
        """Wrapper to serialize the output of the current step

        Parameters
        ----------
        response_time : datetime
            the time for which the button was clicked on
        word : str
            the word displayed to the participant
        judgement : str
            the selected judgement
        """
        self._result_file_handle.write(
            f"{self._current_index}\t{self._start_timer}\t{response_time}\t{spoken_word}\t{perceived_word}\n"
        )

    def end_serialization(self):
        self._logger.info("End Serialization")
        self._result_file_handle.close()

    def closeEvent(self, event):
        event.ignore()

        self.end_serialization()
        import sys

        sys.exit(0)


class WordPanel(QWidget):
    def __init__(self, window: EvaluatorWindow, w1: str, w2: str):
        super().__init__()

        self.selected_word = ""
        self._evaluator_window = window
        self.initUI(w1, w2)

    def initUI(self, w1: str, w2: str):
        # Create alternative buttons
        self._button_word1 = QPushButton(w1)
        self._button_unknown = QPushButton("<Unknown>")
        self._button_word2 = QPushButton(w2)

        # Set a fixed height
        button_height = 200
        self._button_word1.setFixedHeight(button_height)
        self._button_word2.setFixedHeight(button_height)
        self._button_unknown.setFixedHeight(button_height)

        # Update the font to be more readable
        font = QFont()
        font.setPointSize(40)
        self._button_word1.setFont(font)
        self._button_word2.setFont(font)
        self._button_unknown.setFont(font)

        # Connect to the their signals
        self._button_word1.clicked.connect(self.buttonClicked)
        self._button_unknown.clicked.connect(self.buttonClicked)
        self._button_word2.clicked.connect(self.buttonClicked)

        # Set the layout
        layout = QGridLayout()
        layout.addWidget(self._button_word1, 1, 0, 1, 1)
        layout.addWidget(self._button_word2, 1, 2, 1, 1)
        layout.addWidget(self._button_unknown, 0, 1, 1, 1)
        self.setLayout(layout)

    def updateWords(self, w1: str, w2: str):
        self._button_word1.setText(w1)
        self._button_word2.setText(w2)

    def buttonClicked(self):
        sender = self.sender()
        self.selected_word = sender.text()
        self._evaluator_window.moveToNext()

    def keyPressEvent(self, event: QKeyEvent):
        """Keyboard event handler

        Only space is captured and signal the end of the reading

        Parameters
        ----------
        event: QKeyEvent
            the captured event

        """

        if event.key() == Qt.Key_F4 and event.modifiers() == Qt.AltModifier:
            print("Alt+F4 pressed (Ev)")

        if event.key() == Qt.Key_1:
            self.selected_word = self._button_word1.text()
        elif event.key() == Qt.Key_3:
            self.selected_word = self._button_word2.text()
        elif event.key() == Qt.Key_5:
            self.selected_word = ""
        else:
            return
        self._evaluator_window.moveToNext()

    def closeEvent(self, event):
        event.ignore()

        self._evaluator_window.end_serialization()
        import sys

        sys.exit(0)
