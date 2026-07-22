import unittest

from scripts.prepare_apcdata_external import derive_study_id


class ApcDataExternalTests(unittest.TestCase):
    def test_study_id_normalizes_spacing_without_using_field_number(self):
        self.assertEqual(derive_study_id("0051 L SIL C 1541 19 (2).jpg"), "C1541")
        self.assertEqual(derive_study_id("0389 H SIL K 25208 18 (2).jpg"), "K25208")
        self.assertEqual(derive_study_id("0466 Carcinoma C345 21 (1).jpg"), "C345")

    def test_missing_study_identifier_stays_field_specific(self):
        self.assertEqual(derive_study_id("0028 Image_258.jpg"), "UNKNOWN_FIELD_0028")


if __name__ == "__main__":
    unittest.main()
