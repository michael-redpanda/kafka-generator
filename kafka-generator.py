#!/usr/bin/env python3

from argparse import ArgumentParser
import glob
import io
import json
import os
import random
import re
import subprocess
import sys

REQ_FORMAT = "-api={api} -binary-output=true -is-request={is_request} -version={version}"


class ApiMessage(object):
    def __init__(self, api_key: str, msg_type: str, valid_versions: str):
        self._api_key = int(api_key)
        if msg_type == "request":
            self._is_request = True
        elif msg_type == "response":
            self._is_request = False
        else:
            raise ValueError(f"Unknown type: {msg_type}")
        # Below will convert a possible range to of valid versions to a list
        # of number, e.g. (0-4) will turn into [0,1,2,3,4] or 1 will turn into [1]
        results = re.match('(\d+)(-(\d+))?', valid_versions)
        if results.group(1) is None:
            raise ValueError(f"Invalid valid versions string {valid_versions}")
        if results.group(3) is None:
            self._valid_versions = [int(results.group(1))]
        else:
            self._valid_versions = [*range(int(results.group(1)), int(results.group(3)) + 1)]

    def __str__(self):
        return f'API Key: {self._api_key}, Is Request: {self._is_request}, Valid Versions: {self._valid_versions}'

    def __repr__(self):
        result = {"apiKey": self._api_key, "type": "request" if self._is_request else "response",
                  "validVersions": self._valid_versions}
        return json.dumps(result)

    def file_name(self, version: int):
        return f'{self._api_key}_{"request" if self._is_request else "response"}_{version}_{random.randint(10000, 99999)}'

    @property
    def api_key(self):
        return self._api_key

    @property
    def is_request(self):
        return self._is_request

    @property
    def valid_versions(self):
        return self._valid_versions


def request_gen(api: int, is_request: bool, version: int):
    return REQ_FORMAT.format(api=api, is_request="true" if is_request else "false", version=version).split(' ')


def main():
    parser = ArgumentParser(description="Kafka Protocol Parser Generator")
    parser.add_argument('-d', '--schemata-dir', required=True, help="Path containing schemata json files")
    parser.add_argument('-g', '--kafka-req-gen', required=True, help="Path to the kafka request generator")
    parser.add_argument('--request-output-dir', required=True, help="Output directory for generated requests")
    parser.add_argument('--response-output-dir', required=True, help="Output directory for generated responses")

    args = parser.parse_args()

    schemata_dir = args.schemata_dir
    kreq_gen = args.kafka_req_gen
    request_output_dir = args.request_output_dir
    response_output_dir = args.response_output_dir

    if not os.path.isdir(schemata_dir):
        raise RuntimeError(f"{schemata_dir} is not a directory!")

    if not os.path.isfile(kreq_gen) and not os.access(kreq_gen, os.X_OK):
        raise RuntimeError(f"{kreq_gen} is not a valid executable")

    if not os.path.isdir(request_output_dir):
        raise RuntimeError(f"{request_output_dir} does not exist or is not a directory")

    if not os.path.isdir(response_output_dir):
        raise RuntimeError(f"{response_output_dir} does not exist or is not a directory")

    valid_apis: [ApiMessage] = []
    for filename in glob.glob(os.path.join(schemata_dir, '*.json')):
        schema = io.StringIO()
        with open(filename, 'r') as f:
            for line in f.readlines():
                line = re.sub("\/\/.*", "", line)
                if line.strip():
                    schema.write(line)
        msg = json.loads(schema.getvalue())

        api_msg = ApiMessage(msg["apiKey"], msg["type"], msg["validVersions"])
        valid_apis.append(api_msg)

    for msg in valid_apis:
        for ver in msg.valid_versions:
            args = request_gen(msg.api_key, msg.is_request, ver)
            args.insert(0, kreq_gen)
            result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                raise RuntimeError(f'Failed to execute {args}: {result.stderr}')

            output_dir = request_output_dir if msg.is_request else response_output_dir
            output_file = os.path.join(output_dir, msg.file_name(ver))
            while os.path.exists(output_file):
                output_file = os.path.join(output_dir, msg.file_name(ver))
            with open(output_file, "wb") as f:
                f.write(result.stdout)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Error running main: {e}")
        sys.exit(1)
