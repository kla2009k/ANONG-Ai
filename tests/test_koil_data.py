import tempfile
import unittest
from pathlib import Path

from ml.koil_data import (
    SIPAK_CLASSES,
    assert_group_disjoint,
    cluster_id_from_filename,
    group_stratified_split,
)
from scripts.prep import bethesda_to_5class, map_sipakmed


class SipakmedKoilDataTests(unittest.TestCase):
    def test_cluster_id_uses_source_image_prefix(self):
        self.assertEqual(cluster_id_from_filename(Path("084_03.bmp")), "084")
        with self.assertRaises(ValueError):
            cluster_id_from_filename(Path("unknown.bmp"))

    def test_koil_is_an_independent_endpoint_not_forced_into_lsil(self):
        rows = self._rows()
        koil = [row for row in rows if row["sipak_class"] == "Koilocytotic"]
        self.assertTrue(koil)
        self.assertTrue(all(row["koil_label"] == 1 for row in koil))
        self.assertTrue(all("bethesda" not in row for row in koil))

    def test_legacy_five_class_mapping_no_longer_drops_koil(self):
        self.assertEqual(bethesda_to_5class("LSIL", 1), 4)
        self.assertEqual(bethesda_to_5class("LSIL", 0), 1)
        label, koil = map_sipakmed(Path("im_Koilocytotic/CROPPED/084_03.bmp"))
        self.assertEqual((label, koil), ("LSIL", 1))

    def test_group_split_has_all_classes_and_no_leakage(self):
        splits = group_stratified_split(self._rows(), seed=7)
        assert_group_disjoint(splits)
        for split in ("train", "val", "test"):
            self.assertEqual({row["sipak_class"] for row in splits[split]}, set(SIPAK_CLASSES))

    def test_leakage_guard_rejects_shared_cluster(self):
        row = self._rows()[0]
        with self.assertRaises(ValueError):
            assert_group_disjoint({"train": [row], "val": [row], "test": []})

    @staticmethod
    def _rows():
        rows = []
        for class_index, class_name in enumerate(SIPAK_CLASSES):
            for cluster in range(10):
                for cell in range(2):
                    rows.append({
                        "path": f"/{class_name}/{cluster:03d}_{cell:02d}.bmp",
                        "source": "sipakmed",
                        "sipak_class": class_name,
                        "sipak_label": class_index,
                        "koil_label": int(class_name == "Koilocytotic"),
                        "group_id": f"sipakmed:{class_name}:{cluster:03d}",
                    })
        return rows


if __name__ == "__main__":
    unittest.main()
