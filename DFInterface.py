"""
Interface for accessing pandas dataframe
"""

import abc

class DFInterface(abc.ABC): #DataFrameInterface
    @abc.abstractmethod
    def __init__(self, df):
        self.df = None

    @abc.abstractmethod
    def get_df_row(self):
        pass

    @abc.abstractmethod
    def df_row_to_str(self):
        pass

from utils_imdb import calc_age, yob

class IMDBInterface(DFInterface):
    def __init__(self, df):
        self.df = df

    def get_df_row(self, search_str):
        return self.df.loc[self.df["full_path"].str.contains(search_str)]

    def df_row_to_str(self, row, delimeter=":    ", line_delimeter="\n"):
        column_names = ["name", "photo_taken"]
        column_name_str = ["name", "taken"]
        column_format_str = ["%s", "%d"]
        text = ""
        if len(row.index) == 1:
            text = text + "index" + delimeter + "%d" % row.index.tolist()[0] + line_delimeter
        for col, col_str, format_str in zip(column_names, column_name_str, column_format_str):
            if col in row.keys():
                text = text + col_str + delimeter + format_str % row.get(col, "<N/A>").iloc[0] + line_delimeter
        text = text + "yob" + delimeter + "%d" % yob(row.get("dob").iloc[0]) + line_delimeter
        text = text + "age" + delimeter + "%d" % calc_age(row.get("photo_taken").iloc[0], row.get("dob").iloc[0]) + line_delimeter
        return text
