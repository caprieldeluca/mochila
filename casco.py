# -*- coding: utf-8 -*-

from mochila import plog
from mochila.vector import remove_spikes
import threading
import traceback


def locked_task():
    """Run a locked task."""
    try:
        remove_spikes.test()


    except Exception as e:
        plog(*traceback.format_exception(e))
    plog('#####')


t = threading.Thread(target=locked_task, name='locked_task')
t.start()
