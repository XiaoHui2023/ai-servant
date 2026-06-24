"""冒烟测试。"""

from __future__ import annotations

import unittest

from cli import build_parser


class SmokeTest(unittest.TestCase):
    def test_version_flag(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            build_parser().parse_args(["--version"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
