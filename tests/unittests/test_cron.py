import os
import tarfile

from unittest import TestCase, main
from unittest.mock import MagicMock, patch, call, mock_open

from files.image.cron import cron  # noqa: F401


class CronTestCase(TestCase):

    def test_parse_crontab(self):
        with self.assertRaises(SystemExit):
            cron.restore_data("")


if __name__ == "__main__":
    main()
