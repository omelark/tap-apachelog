"""Custom client handling, including ApacheLogStream base class."""

import os
from typing import Optional, List, Iterable

from singer_sdk import typing as th
from singer_sdk.streams import Stream

from apachelogs import LogParser


class ApacheLogStream(Stream):
    """Stream class for Apache log streams.
    Currently only the combined log format is supported."""

    file_paths: List[str] = []

    COMBINED_LOG_FORMAT = '%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\"'

    RECORD_KEYS = [
        'remote_host',
        'remote_logname',
        'remote_user',
        'timestamp',
        'request_line',
        'final_status',
        'bytes_sent',
        'referer',
        'user_agent',
    ]

    def __init__(self, *args, **kwargs):
        """Init ApacheLogStream."""
        # cache file_config so we dont need to go iterating the config list again later
        self.file_config = kwargs.pop("file_config")
        super().__init__(*args, **kwargs)

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects.

        The optional `context` argument is used to identify a specific slice of the
        stream if partitioning is required for the stream. Most implementations do not
        require partitioning and should ignore the `context` argument.
        """
        for file_path in self.get_file_paths():
            for row in self.get_rows(file_path):
                yield dict(zip(self.RECORD_KEYS, row))

    def get_file_paths(self) -> list:
        """Return a list of file paths to read.
        This tap accepts file names and directories so it will detect
        directories and iterate files inside.
        """
        # Cache file paths so we dont have to iterate multiple times
        if self.file_paths:
            return self.file_paths

        file_path = self.file_config["path"]
        if not os.path.exists(file_path):
            raise Exception(f"File path does not exist {file_path}")

        file_paths = []
        if os.path.isdir(file_path):
            clean_file_path = os.path.normpath(file_path) + os.sep
            for filename in os.listdir(clean_file_path):
                file_path = clean_file_path + filename
                if self.is_valid_filename(file_path):
                    file_paths.append(file_path)
        else:
            if self.is_valid_filename(file_path):
                file_paths.append(file_path)

        if not file_paths:
            raise Exception(
                f"Stream '{self.name}' has no acceptable files. \
                    See warning for more detail."
            )
        self.file_paths = file_paths
        return file_paths

    def is_valid_filename(self, file_path: str) -> bool:
        """Return a boolean of whether the file includes log extension."""
        is_valid = True
        if file_path[-4:] != ".log":
            is_valid = False
            self.logger.warning(f"Skipping non-log file '{file_path}'")
            self.logger.warning(
                "Please provide a log file that ends with '.log'; e.g. 'access.log'"
            )
        return is_valid

    def get_rows(self, file_path: str) -> Iterable[list]:
        """Return a generator of the rows in a particular Apache log file."""

        parser = LogParser(self.COMBINED_LOG_FORMAT)

        with open(file_path, "r") as f:
            for row in f.readlines():
                entry = parser.parse(row)

                yield [
                    entry.remote_host,
                    entry.remote_logname,
                    entry.remote_user,
                    entry.request_time_fields["timestamp"],
                    entry.request_line,
                    str(entry.final_status),
                    str(entry.bytes_sent),
                    entry.headers_in["Referer"],
                    entry.headers_in["User-Agent"]
                ]

    @property
    def schema(self) -> dict:
        """Return dictionary of record schema.
        Currently only the combined log format is supported
        and the schema is static in RECORD_KEYS.
        """
        properties: List[th.Property] = []

        for column in self.RECORD_KEYS:
            # Set all types to string
            properties.append(th.Property(column, th.StringType()))

        return th.PropertiesList(*properties).to_dict()
