# tap-apachelog

`tap-apachelog` is a Singer tap for [Apache's log files](https://httpd.apache.org/docs/current/logs.html).

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Capabilities

* `sync`
* `catalog`
* `discover`

Note: This tap currently does not support incremental state.

The currently supported log format is [_Combined Log Format_](https://httpd.apache.org/docs/current/logs.html) 

```
LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\"" combined
```

## Installation

Currently the project can be installed from Github in any local directory:

```bash
git clone https://github.com/omelark/tap-apachelog
```

Add the plugin in your Meltano project in `meltano.yml` pointing to the directory the repo was cloned

```yaml
plugins:
  extractors:
  ...
  - name: tap-apachelog
    namespace: tap_apachelog
    pip_url: -e /path/to/tap_apachelog
    executable: tap-apachelog
    capabilities:
    - discover
```
See [Meltano doc](https://docs.meltano.com/tutorials/custom-extractor#add-the-plugin-to-your-meltano-project) for more information about using custom plugins.


After the adding of the plugin run `meltano install` to let Meltano know about it and install it:

```bash
meltano install
```

## Configuration

| Setting                   | Required | Default | Description |
|:--------------------------|:--------:|:-------:|:------------|
| files                     | False    | None    | An array of Apache log file stream settings. |
| apachelog_files_definition| False    | None    | A path to the JSON file holding an array of file settings. |

A full list of supported settings and capabilities is available by running: `poetry run tap-apachelog --about`

The `config.json` contains an array called `files` that consists of dictionary objects detailing each destination table to be passed to Singer. Each of those entries contains: 
* `entity`: The entity name to be passed to singer
* `path`: Local path to the file to be ingested. Note that this may be a directory, in which case all files in that directory and any of its subdirectories will be recursively processed

Examples:

For Meltano project place the configuration parameters as the `config:` block:

**meltano.yml**

```yaml
  config:
    plugins:
      extractors:
      - name: tap-apachelog
        config:
          files:
          - entity: file1
            path: /path/to/file1.log
```

For the configuration over the json files:

Place the files into one config file:

**config.json**

```json
{
	"files":	[ 	
					{	"entity" : "file1",
						"path" : "/path/to/file1.log"
					},
					{	"entity" : "file2",
						"path" : "/path/to/file2.log"
					}
				]
}
```

Optionally, the files definition can be provided by an external json file:

**config.json**

```json
{
	"apachelog_files_definition": "files_def.json"
}
```

**files_def.json**

```json
[ 	
	{	"entity" : "file1",
		"path" : "/path/to/file1.log"
	},
	{	"entity" : "file2",
		"path" : "/path/to/file2.log"
	}
]
```

Then the plugin can be tested with this config file, e.g.:

```bash
# check that we can print the catalog
poetry run tap-apachelog --config config.json --discover

# check that we can sync the data
poetry run tap-apachelog --config config.json > output/out.jsonl
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

## Usage

You can easily run `tap-apachelog` by itself or in a pipeline using [Meltano](https://meltano.com/).

## Developer Resources

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap_apachelog/tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-apachelog` CLI interface directly using `poetry run`:

```bash
poetry run tap-apachelog --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any _"TODO"_ items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-apachelog
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-apachelog --version
# OR run a test `elt` pipeline:
meltano elt tap-apachelog target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
