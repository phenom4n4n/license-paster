"""
MIT License

Copyright (c) 2021-present phenom4n4n

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging
import re
import os

__all__ = (
    "PasteProtocol",
    "paste_file",
    "paste_directory",
    "find_license",
)

log = logging.getLogger("licensepaster")


class PasteProtocol:
    def __init__(self, license: str, *, pattern: re.Pattern = None):
        self.license = license.strip()
        self.license_pattern = re.compile(re.escape(self.license))
        self.pattern = pattern or self.license_pattern

    def search(self, string: str):
        return self.pattern.search(string)

    def sub(self, string: str):
        return self.pattern.sub(f"\n{self.license}\n", string)

    def should_write(self, string: str) -> bool:
        return not self.license_pattern.match(string)

    def paste(self, string: str) -> bool:
        if self.search(string):
            return self.sub(string)
        return f'"""\n{self.license}\n"""\n\n{string}'


def paste_file(file_name: str, protocol: PasteProtocol):
    with open(file_name, "r+", encoding="utf-8") as code_file:
        text = code_file.read()
        if protocol.should_write(text):
            log.info("pasting to %s", file_name)
            pasted = protocol.paste(text)
            code_file.truncate()
            code_file.seek(0)
            code_file.write(pasted)


def paste_directory(directory: str, protocol: PasteProtocol):
    for file_name in os.listdir(directory):
        if file_name.startswith("."):
            continue
        file_path = os.path.join(directory, file_name)
        if os.path.isdir(file_path):
            paste_directory(file_path, protocol)
        elif os.path.isfile(file_path):
            if file_path.endswith(".py"):
                paste_file(file_path, protocol)


def find_license(directory: str) -> str:
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if file_name.startswith("LICENSE"):
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
