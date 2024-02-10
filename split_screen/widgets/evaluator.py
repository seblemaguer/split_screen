import pathlib
import pandas as pd
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSizePolicy


class EvaluatorWindow(QWidget):
    """The window presented to the evaluator

    It contains 2 buttons (left and right) which shows two potential words. The evaluator has to click on one of this word to move to the next step
    """

    def __init__(
        self,
        word_list_file: pathlib.Path,
        participant_window: QWidget,
    ):
        super().__init__()

        self.setWindowTitle("Evaluator window")

        # Create a QHBoxLayout instance
        self._layout = QHBoxLayout()

        # Add widgets to the layout
        self._left_button = QPushButton("left")
        font = self._left_button.font()
        font.setPointSize(100)
        self._left_button.setFont(font)
        self._layout.addWidget(self._left_button, stretch=1)
        self._left_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self._left_button.clicked.connect(self.left_button_clicked)

        self._right_button = QPushButton("right")
        font = self._right_button.font()
        font.setPointSize(100)
        self._right_button.setFont(font)
        self._layout.addWidget(self._right_button, stretch=1)
        self._right_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self._right_button.clicked.connect(self.right_button_clicked)

        # Set the layout on the application's window
        self.setLayout(self._layout)

        # Now prepare the data itself
        self._participant_window = participant_window
        self._current_index = -1
        self._word_df = pd.read_csv(word_list_file, sep="\t")
        self.move_to_next()

    def left_button_clicked(self):
        print(self._left_button.text())
        self.move_to_next()

    def right_button_clicked(self):
        print(self._right_button.text())
        self.move_to_next()

    def move_to_next(self) -> bool:
        self._current_index += 1

        if self._current_index >= len(self._word_df.index):
            return True

        self._left_button.setText(
            self._word_df.loc[self._current_index, "Alternative 1"]
        )
        self._right_button.setText(
            self._word_df.loc[self._current_index, "Alternative 2"]
        )
        self._participant_window.setWord(self._word_df.loc[self._current_index, "Word"])
        return False
