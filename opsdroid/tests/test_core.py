import os
import signal
import threading

import unittest.mock as amock
import pytest

from opsdroid.core import OpsDroid


@pytest.mark.skipif(os.name == "nt", reason="SIGHUP unsupported on windows")
@pytest.mark.isolate_signal_test
def test_signals(event_loop):
    pid = os.getpid()

    def send_signal(sig):
        # print(f"{pid} <== {sig}")
        os.kill(pid, sig)

    with OpsDroid() as opsdroid:
        opsdroid.load = amock.AsyncMock()
        # bypass task creation in start() and just run the task loop
        opsdroid.start = amock.AsyncMock(return_value=opsdroid._run_tasks)
        opsdroid.unload = amock.AsyncMock()
        opsdroid.reload = amock.AsyncMock()
        threading.Timer(2, lambda: send_signal(signal.SIGHUP)).start()
        threading.Timer(3, lambda: send_signal(signal.SIGINT)).start()
        with pytest.raises(SystemExit):
            opsdroid.run()
        assert opsdroid.reload.called
