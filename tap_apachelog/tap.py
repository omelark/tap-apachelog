"""Apache log tap class."""

import json
import os
from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_apachelog.client import ApacheLogStream


class TapApacheLog(Tap):
    """apachelog tap class."""
    name = "tap-apachelog"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "files",
            th.ArrayType(
                th.ObjectType(
                    th.Property("entity", th.StringType, required=True),
                    th.Property("path", th.StringType, required=True),
                )
            ),
            description="An array of Apache log file stream settings.",
        ),
        th.Property(
            "apachelog_files_definition",
            th.StringType,
            description="A path to the JSON file holding an array of file settings.",
        ),
    ).to_dict()

    def get_file_configs(self) -> List[dict]:
        """Return a list of file configs.
        Either directly from the config.json or in an external file
        defined by apachelog_files_definition.
        """
        apachelog_files = self.config.get("files")
        apachelog_files_definition = self.config.get("apachelog_files_definition")
        if apachelog_files_definition:
            if os.path.isfile(apachelog_files_definition):
                with open(apachelog_files_definition, "r") as f:
                    apachelog_files = json.load(f)
            else:
                self.logger.error(
                    f"tap-apachelog: '{apachelog_files_definition}' file not found")
                exit(1)
        if not apachelog_files:
            self.logger.error("No Apache log file definitions found.")
            exit(1)
        return apachelog_files

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [
            ApacheLogStream(
                tap=self,
                name=file_config.get("entity"),
                file_config=file_config,
            )
            for file_config in self.get_file_configs()
        ]

if __name__ == "__main__":
    TapApacheLog.cli()