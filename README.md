# SplitScreen

Helper to run an experiment which assumes 2 monitors:
  - **participant monitor**: showing a word
  - **evaluator monitor**: show 2 possible words that the evaluator has to select


## Pre-requisites

This helper requires the following packages:
  - **pandas** for data processing
  - **pyqt5** for UI rendering

If you have conda, it is easier to install the environment described by **env.yaml**:

```sh
conda env create -f env.yml
```

## How to run

Simply run the following command:

```sh
python split_screen/main.py examples/word_list.tsv
```
