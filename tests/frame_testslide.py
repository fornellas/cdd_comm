from testslide import TestCase

import cdd_comm.frame as frame_mod


class FrameTest(TestCase):
    def test_smoke(self):
        frame_mod.Frame(length=0, type=1, address=2, data=[], checksum=0)
