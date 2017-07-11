# -*- coding: UTF-8 -*-
# author: star
# created_at: 17-6-29 11:29
import os

import channels

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
application = channels.asgi.get_channel_layer()
