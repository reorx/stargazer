#!/usr/bin/env python
# -*- coding: utf-8 -*-

from torext.app import TorextApp
import settings


app = TorextApp(settings)
app.setup()


app.route_many([
    ('', 'handlers')
])


if __name__ == '__main__':

    app.command_line_config()
    app.run()
