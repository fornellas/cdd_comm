from testslide import TestCase

import cdd_comm.frame as frame_mod


class FrameTest(TestCase):
    def test_get_kebab_case_description(self):
        self.assertEqual(
            frame_mod.Frame(
                length=0, type=1, address=2, data=[], checksum=0
            ).get_kebab_case_description(),
            "frame",
        )

    def test_eq(self):
        self.assertTrue(
            frame_mod.Frame(length=0, type=1, address=2, data=[], checksum=0)
            == frame_mod.Frame(length=0, type=1, address=2, data=[], checksum=0)
        )
        self.assertFalse(
            frame_mod.Frame(length=0, type=1, address=2, data=[], checksum=0)
            == frame_mod.Frame(length=1, type=1, address=2, data=[0], checksum=0)
        )
        self.assertFalse(
            frame_mod.Frame(length=0, type=1, address=2, data=[], checksum=0)
            == frame_mod.Frame(length=0, type=11, address=2, data=[], checksum=0)
        )
        self.assertFalse(
            frame_mod.Frame(length=0, type=1, address=2, data=[], checksum=0)
            == frame_mod.Frame(length=0, type=1, address=22, data=[], checksum=0)
        )
        self.assertFalse(
            frame_mod.Frame(length=2, type=1, address=2, data=[0, 1], checksum=0)
            == frame_mod.Frame(length=2, type=1, address=2, data=[0, 2], checksum=0)
        )
        self.assertFalse(
            frame_mod.Frame(length=0, type=1, address=2, data=[], checksum=0)
            == frame_mod.Frame(length=0, type=1, address=2, data=[], checksum=1)
        )

    def test_calculate_checksum(self):
        self.assertEqual(
            frame_mod.Frame.calculate_checksum(
                length=3, frame_type=244, address=134, data=[0, 1, 2]
            ),
            128,
        )
        self.assertEqual(
            frame_mod.Frame.calculate_checksum(
                length=2, frame_type=3, address=134, data=[0, 1]
            ),
            116,
        )

    def test_is_checksum_valid(self):
        self.assertTrue(
            frame_mod.Frame(
                length=3, type=244, address=134, data=[0, 1, 2], checksum=128
            ).is_checksum_valid()
        )
        self.assertFalse(
            frame_mod.Frame(
                length=3, type=244, address=134, data=[0, 1, 2], checksum=127
            ).is_checksum_valid()
        )

    def test_bytes(self):
        self.assertEqual(
            frame_mod.Frame(
                length=3, type=244, address=134, data=[0, 1, 2], checksum=128
            ).bytes(),
            b":03F4860000010280",
        )
        self.assertEqual(
            frame_mod.Frame(
                length=3, type=234, address=55, data=[0, 1, 2], checksum=34
            ).bytes(),
            b":03EA370000010222",
        )

    def test_from_data(self):
        self.assertTrue(
            type(
                frame_mod.Frame.from_data(
                    length=frame_mod.Directory.LENGTH,
                    frame_type=frame_mod.Directory.TYPE,
                    address=frame_mod.Directory.ADDRESS,
                    data=[0, 0],
                    checksum=0,
                )
            )
            == frame_mod.Directory
        )
        self.assertTrue(
            type(
                frame_mod.Frame.from_data(
                    length=frame_mod.Directory.LENGTH,
                    frame_type=frame_mod.Directory.TYPE,
                    address=frame_mod.Directory.ADDRESS,
                    data=frame_mod.TelephoneDirectory.DATA,
                    checksum=0,
                )
            )
            == frame_mod.TelephoneDirectory
        )
