import csv
import os
import unittest
from pathlib import Path

from nose_parameterized import parameterized

from lib import csvLib


def clean_test_file(n):
    file_path = Path(n)
    os.remove(file_path)


class TestCSV(unittest.TestCase):

    def test_is_result_file_created(self):
        o = csvLib.CsvOutput("random", "random", "test_is_result_file_created")
        file_path = Path(o.get_output_file_name())
        self.assertTrue(file_path.exists())
        os.remove(file_path)

    def test_get_existing_field_names(self):
        o = csvLib.CsvOutput("random", "test", "test_get_existing_fn")
        self.assertEqual(['random', 'test'], o.get_existing_field_names())
        clean_test_file(o.get_output_file_name())

    def test_result_file(self):
        o = csvLib.CsvOutput("random", "cma", "test_result_file")
        if o.is_selfplay():
            self.assertEqual("test_result_file_selfplay.csv", o.get_output_file_name())
        else:
            self.assertEqual("test_result_file.csv", o.get_output_file_name())
        clean_test_file(o.get_output_file_name())

    @parameterized.expand([
        ["random", "random", "test", "test", "test_adding_column_selfplay", ['random', 'test']],
        ["random", "ga", "test", "random", "test_adding_column", ['random', 'ga', 'test']]
    ])
    def test_adding_column(self, ia1, ia2, iaT1, iaT2, fn, fdn_expected):
        o = csvLib.CsvOutput(ia1, ia2, fn)
        o.check_ia_in_fieldnames(iaT1, iaT2)
        with open(o.get_output_file_name(), 'r') as file:
            csv_reader = csv.DictReader(file)
            header = list(csv_reader.fieldnames)
            self.assertEqual(header, fdn_expected)
        clean_test_file(o.get_output_file_name())

    def test_no_adding_column_on_existing_file(self):
        o = csvLib.CsvOutput("random", "cma", "test/test")
        o.check_ia_in_fieldnames("random", "ppo")
        with open(o.get_output_file_name(), 'r') as file:
            csv_reader = csv.DictReader(file)
            header = list(csv_reader.fieldnames)
            self.assertEqual(header, ['random', 'cma', 'test', 'ppo', 'RNN'])
        # clean_test_file(o.get_output_file_name())

    def test_result_has_been_written_in_selfplay(self):
        o = csvLib.CsvOutput("random", "random", "test_result_has_been_written_in_selfplay")
        o.write_result(2)
        with open(o.get_output_file_name(), 'r') as file:
            csv_reader = csv.DictReader(file)
            row1 = next(csv_reader)
            self.assertEqual(row1['random'], '2')
        clean_test_file(o.get_output_file_name())


if __name__ == '__main__':
    unittest.main()
