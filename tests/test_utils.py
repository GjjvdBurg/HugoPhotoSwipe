# -*- coding: utf-8 -*-

import os
import tempfile
import unittest

from hugophotoswipe.utils import yaml_field_to_file


class UtilsTestCase(unittest.TestCase):
    def _write_read_yaml_field(self, *args, **kwargs):
        temp_fd, temp_filename = tempfile.mkstemp("test.yml")
        with os.fdopen(temp_fd, "w") as fp:
            yaml_field_to_file(fp, *args, **kwargs)
        with open(temp_filename, "r") as fp:
            content = fp.read()
        return content

    def test_yaml_field_to_file(self):
        out = self._write_read_yaml_field(None, "key")
        self.assertEqual("key:\n", out)

        out = self._write_read_yaml_field(None, "key", indent="  ")
        self.assertEqual("  key:\n", out)

        out = self._write_read_yaml_field("", "key")
        self.assertEqual("key:\n", out)

        out = self._write_read_yaml_field("abc", "key")
        self.assertEqual("key: abc\n", out)

        out = self._write_read_yaml_field("abc", "field", indent="  ")
        self.assertEqual("  field: abc\n", out)

        out = self._write_read_yaml_field(123, "key")
        self.assertEqual("key: 123\n", out)

        out = self._write_read_yaml_field(
            123, "key", indent="  ", force_string=True
        )
        self.assertEqual('  key: "123"\n', out)


if __name__ == "__main__":
    unittest.main()
