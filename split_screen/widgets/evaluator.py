# Python
import pathlib
import logging
import datetime

# UI
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSizePolicy

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
        self._logger = logging.getLogger(self.__class__.__name__)
        self.setWindowTitle("Evaluator window")

        # Define a wrapping widget to facilitate hide/show of the controls
        self._wrapping_widget = QWidget()
        wrapping_layout = QHBoxLayout()
        wrapping_layout.addWidget(self._wrapping_widget)
        self._wrapping_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self._wrapping_widget.hide()
        self.setLayout(wrapping_layout)

        # Create a QHBoxLayout instance
        self._layout = QHBoxLayout()

        # Defines possible answers
        for label in ("too short", "short", "neutral", "long", "too long"):
            # Create button
            cur_button = QPushButton(label)
            font = cur_button.font()
            font.setPointSize(50)
            cur_button.setFont(font)

            # Insert button to the layout
            self._layout.addWidget(cur_button, stretch=1)
            # self._left_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

            # Capture click
            cur_button.clicked.connect(self.buttonClicked)

        # Set the layout on the application's window
        self._wrapping_widget.setLayout(self._layout)

        # Now prepare the data itself
        self._participant_window = participant_window
        self._current_index = -1
        self._word_df = pd.read_csv(word_list_file, sep="\t")
        self._result_file_handle = open(result_file, "w")
        self._result_file_handle.write("step_idx\tstart_scoring_timestamp\treceived_score_timestamp\tdictated_word\tjudgment\n")

        # Ok ready, steady, go!
        self.moveToNext()

    def buttonClicked(self):
        """Click event handler

        Handler activated when the evaluator selected a judgement.
        This triggers the following sequence of operations:
           1. serialize the judgement with the different timestamps (start show of the scoring, click received)
           2. move to the next step
        """
        # Log the time
        current_time = datetime.datetime.now()

        # Log the button clicked
        sender = self.sender()
        self._logger.debug(f"Left button pressed ({sender.text()}")
        self._serializeSelection(current_time, self._word_df.loc[self._current_index, "Word"], sender.text())

        # Move to the next step
        self.moveToNext()

    def moveToNext(self):
        """Prepare the next step of the evaluation

        This function triggers the following sequence:
           1. hide anything from the evaluator to avoid any unwanted interactions
           2. ensure that there is more evaluation to be done:
              - if not just quit
              - if yes select the next word and move the focus to the participant window
        """
        self._wrapping_widget.hide()
        self._current_index += 1

        # End of the test
        # FIXME: a bit hardcore for quitting no ?
        if self._current_index >= len(self._word_df.index):
            self._result_file_handle.close()
            import sys
            sys.exit(0)

        self._participant_window.setWord(self._word_df.loc[self._current_index, "Word"])
        self._participant_window.activateWindow()

    def _serializeSelection(self, response_time, word, judgement):
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
        self._result_file_handle.write(f"{self._current_index}\t{self._start_timer}\t{response_time}\t{word}\t{judgement}\n")

    def startCapture(self):
        """Helper to prepare the judgement stage of the evaluation

        This function is called by an external widget (the participant one)
        """
        self._logger.debug("Ready to capture")
        self._wrapping_widget.show()
        self._start_timer = datetime.datetime.now()
