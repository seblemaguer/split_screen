# Python
import pathlib
import logging
import datetime

# UI
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSizePolicy, QStackedWidget

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
    ):
        super().__init__()

        # Initialise some helpers
        self._participant_window = participant_window
        self._logger = logging.getLogger(self.__class__.__name__)
        self.setWindowTitle("Evaluator window")

        # Load words
        self._current_index = -1
        self._word_df = pd.read_csv(word_list_file, sep="\t")

        # Prepare the two panels (hidden for now)
        self._word_panel = WordPanel(self, "", "")  # FIXME: define the words
        self._degree_panel = DegreePanel(self)

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
        self._wrapping_widget.addWidget(self._degree_panel)


        # Prepare the output data serialisation
        self._result_file_handle = open(result_file, "w")
        self._result_file_handle.write(
            "step_idx\tstart_scoring_timestamp\treceived_score_timestamp\tdictated_word\tselected_word\tjudgement\n"
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

    def selectDegree(self):
        self._wrapping_widget.setCurrentIndex(1)

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
                self._word_df.loc[self._current_index, "Word"],
                self._word_panel.selected_word,
                self._degree_panel.selected_degree,
            )

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
            self._word_df.loc[self._current_index, "Alternative 1"],
            self._word_df.loc[self._current_index, "Alternative 2"],
        )
        self._wrapping_widget.setCurrentIndex(0)

        # Prepare and activate the participant window
        self._participant_window.setWord(self._word_df.loc[self._current_index, "Word"])
        self._participant_window.activateWindow()

    def _serializeSelection(
        self, response_time, dictated_word, selected_word, judgement
    ):
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
            f"{self._current_index}\t{self._start_timer}\t{response_time}\t{dictated_word}\t{selected_word}\t{judgement}\n"
        )


class WordPanel(QWidget):
    def __init__(self, window: EvaluatorWindow, w1: str, w2: str):
        super().__init__()

        self._window = window

        # Create alternative buttons
        self._button_word1 = QPushButton(w1)
        self._button_word1.clicked.connect(self.buttonClicked)

        self._button_word2 = QPushButton(w2)
        self._button_word2.clicked.connect(self.buttonClicked)

        # Set the layout
        self._layout = QHBoxLayout()
        self._layout.addWidget(self._button_word1, stretch=1)
        self._layout.addWidget(self._button_word2, stretch=1)
        self.setLayout(self._layout)

    def updateWords(self, w1: str, w2: str):
        self._button_word1.setText(w1)
        self._button_word2.setText(w2)

    def buttonClicked(self):
        sender = self.sender()
        self.selected_word = sender.text()
        self._window.selectDegree()


class DegreePanel(QWidget):
    DEGREES = ["Too Short", "Good", "Too Long"]

    def __init__(self, window: EvaluatorWindow):
        super().__init__()
        self._window = window

        self._layout = QHBoxLayout()
        for degree in DegreePanel.DEGREES:
            button = QPushButton(degree)
            button.clicked.connect(self.buttonClicked)
            self._layout.addWidget(button, stretch=1)

        self.setLayout(self._layout)

    def buttonClicked(self):
        sender = self.sender()
        self.selected_degree = sender.text()
        self._window.moveToNext()
