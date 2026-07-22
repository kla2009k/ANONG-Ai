import csv
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from ml.cric_grade_data import CRIC_LABEL_MAP, CricCellDataset, assert_disjoint_groups, grouped_folds


class CricGradeDataTests(unittest.TestCase):
    def test_ambiguous_asc_labels_are_not_forced_into_four_grade_endpoint(self):
        self.assertNotIn("ASC-US", CRIC_LABEL_MAP)
        self.assertNotIn("ASC-H", CRIC_LABEL_MAP)

    def test_grouped_folds_have_no_parent_image_leakage(self):
        rows = []
        for label in range(4):
            for group in range(10):
                rows.extend({"label5": str(label), "group_id": f"{label}-{group}"} for _ in range(2))
        folds = grouped_folds(rows, folds=5, seed=7)
        self.assertEqual(len(folds), 5)
        for split in folds:
            assert_disjoint_groups(split)

    def test_dataset_crops_edge_cell_with_padding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image_path = root / "parent.png"
            Image.new("RGB", (100, 100), (180, 120, 160)).save(image_path)
            manifest = root / "test.csv"
            with manifest.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["path", "crop_path", "source", "group_id", "cell_id", "bethesda", "label5", "nucleus_x", "nucleus_y"])
                writer.writeheader()
                writer.writerow({"path": image_path, "crop_path": "", "source": "cric", "group_id": "g1", "cell_id": "1", "bethesda": "NILM", "label5": "0", "nucleus_x": "2", "nucleus_y": "3"})
            item = CricCellDataset(manifest, image_size=64, crop_size=80)[0]
            self.assertEqual(tuple(item["image"].shape), (3, 64, 64))
            self.assertFalse(item["mask_available"].item())


if __name__ == "__main__":
    unittest.main()
