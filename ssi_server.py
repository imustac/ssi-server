#!/usr/bin/env python
'''
Use this in the same way as Python's SimpleHTTPServer:

  ./ssi_server.py [port]

The only difference is that, for files ending in '.html', ssi_server will
inline SSI (Server Side Includes) of the form:

  <!-- #include virtual="fragment.html" -->

Run ./ssi_server.py in this directory and visit localhost:8000 for an exmaple.
'''

import os
import ssi
try:
    # This works for Python 2
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    import SimpleHTTPServer
except ImportError:
    # This works for Python 3
    from http.server import SimpleHTTPRequestHandler
    import http.server as SimpleHTTPServer
import tempfile


class SSIRequestHandler(SimpleHTTPRequestHandler):
  """Adds minimal support for <!-- #include --> directives.

  The key bit is translate_path, which intercepts requests and serves them
  using a temporary file which inlines the #includes.
  """

  def __init__(self, request, client_address, server):
    self.temp_files = []
    SimpleHTTPRequestHandler.__init__(self, request, client_address, server)

  def do_GET(self):
    SimpleHTTPRequestHandler.do_GET(self)
    self.delete_temp_files()

  def do_HEAD(self):
    SimpleHTTPRequestHandler.do_HEAD(self)
    self.delete_temp_files()

  def translate_path(self, path):
    fs_path = SimpleHTTPRequestHandler.translate_path(self, path)
    if fs_path[-3:].lower() == ".py" or fs_path[-4:].lower() == ".pyc":
      error = "File not found: %s" % path
      return error

    if self.path.endswith('/'):
      for index in "index.html", "index.htm", "index.shtml":
        index = os.path.join(fs_path, index)
        if os.path.exists(index):
          fs_path = index
          break

    if (fs_path.endswith('.html') or fs_path.endswith(".shtml")) and os.path.exists(fs_path):
      content = ssi.InlineIncludes(fs_path, path)
      fs_path = self.create_temp_file(fs_path, content)
    return fs_path

  def delete_temp_files(self):
    for temp_file in self.temp_files:
      os.remove(temp_file)

  def create_temp_file(self, original_path, content):
    _, ext = os.path.splitext(original_path)
    if ext == ".shtml":
        ext = ".html"
    fd, path = tempfile.mkstemp(suffix=ext)
    try:
        os.write(fd, content)  # This works for Python 2
    except TypeError:
        os.write(fd, bytes(content, 'UTF-8'))  # This works for Python 3
    os.close(fd)

    self.temp_files.append(path)
    return path


if __name__ == '__main__':
  SimpleHTTPServer.test(HandlerClass=SSIRequestHandler)
