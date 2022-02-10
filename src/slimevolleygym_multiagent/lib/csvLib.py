import csv
import os
from pathlib import Path


# noinspection PyTypeChecker
class CsvOutput:
    """
    Creation of the object Csv
    Give only the IA names in little letters
    The result file name MUST be written without .csv

    Example of initialisation
    csvObject = CsvOutput("random", "ppo", "slimeV5") # Don't forget to give json args !
    """

    def __init__(self, team_right_ia, team_left_ia, output_file_name="slimev0"):
        if team_right_ia == team_left_ia:
            self._selfplay: bool = True
            self._output_file_name = output_file_name + '_selfplay.csv'
            self._ia_name = team_right_ia
        else:
            self._output_file_name = output_file_name + ".csv"
            self._selfplay: bool = False
            self._ia_name = team_left_ia, team_right_ia
        self._field_names = self.get_existing_field_names()
        self.check_ia_in_fieldnames(team_right_ia, team_left_ia)

    """
    called in init
    """
    def get_existing_field_names(self):
        if self._is_file_just_created():
            return []
        else:
            with open(self._output_file_name, 'r') as file:
                csv_reader = csv.DictReader(file)
                fn = csv_reader.fieldnames
                return list(fn)

    def _is_file_just_created(self):
        file_path = Path(self._output_file_name)
        if file_path.exists():
            return False
        file = open(self._output_file_name, 'x')
        file.close()
        return True

    def check_ia_in_fieldnames(self, ia1, ia2):
        if not self._field_names:
            self._field_names.append(ia1)
            if not self._selfplay:
                self._field_names.append(ia2)
            self.write_fieldnames()
        else:
            if ia1 not in self._field_names:
                self._add_column(ia1)
                self._field_names.append(ia1)
            if ia2 not in self._field_names:
                self._add_column(ia2)
                self._field_names.append(ia2)

    def write_fieldnames(self):
        with open(self._output_file_name, 'w', newline='') as file:
            csv_writer = csv.DictWriter(file, self._field_names)
            csv_writer.writeheader()

    """
    getters and setters
    """
    def get_output_file_name(self):
        return self._output_file_name

    def get_field_names(self):
        return self._field_names

    def is_selfplay(self):
        return self._selfplay

    def write_result(self, cumulative_score):
        with open(self._output_file_name, 'a+', newline='') as file:
            fileWriter = csv.DictWriter(file, self._field_names)
            if self._selfplay:
                fileWriter.writerow({self._ia_name: cumulative_score})
            else:
                fileWriter.writerow({self._ia_name[0]: -cumulative_score, self._ia_name[1]: cumulative_score})

    def print_all_file(self):
        with open(self._output_file_name, 'r') as file:
            csv_reader = csv.DictReader(file)
            for line in csv_reader:
                print(line)

    def _add_column(self, new_column_name):
        """ Append a column in existing csv using csv.reader / csv.writer classes"""
        with open(self._output_file_name, 'r') as read_obj, \
                open("tmp.csv", 'w', newline='') as write_obj:
            csv_reader = csv.reader(read_obj)
            csv_writer = csv.writer(write_obj)
            header = next(csv_reader)
            header.append(new_column_name)
            csv_writer.writerow(header)
            for row in csv_reader:
                row.append('')
                csv_writer.writerow(row)
        os.remove(self._output_file_name)
        os.rename("tmp.csv", self._output_file_name)
