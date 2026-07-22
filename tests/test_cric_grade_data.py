import csv
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from ml.cric_grade_data import (
    CRIC_LABEL_MAP,
    CricCellDataset,
    assert_disjoint_groups,
    grouped_folds,
    parent_balanced_sample_weights,
    relative_crop_box,
)


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
            self.assertEqual(tuple(item["context_image"].shape), (3, 64, 64))
            self.assertFalse(item["mask_available"].item())

    def test_parent_balanced_weights_prevent_cell_rich_parent_domination(self):
        rows = [
            {"group_id": "many", "label5": "1"} for _ in range(10)
        ] + [
            {"group_id": "few", "label5": "1"},
            {"group_id": "scc", "label5": "3"},
        ]
        weights = parent_balanced_sample_weights(rows, class_power=0.5)
        many_mass = float(weights[:10].sum())
        few_mass = float(weights[10])
        self.assertAlmostEqual(many_mass, few_mass, places=6)
        self.assertGreater(float(weights[11]), float(weights[10]))

    def test_multiscale_crop_uses_the_same_relative_geometry(self):
        params = {"scale": 0.81, "ratio": 1.0, "top": 0.25, "left": 0.75}
        small = relative_crop_box(100, 100, params)
        large = relative_crop_box(200, 200, params)
        self.assertAlmostEqual(small[0] / 100, large[0] / 200, delta=0.006)
        self.assertAlmostEqual(small[1] / 100, large[1] / 200, delta=0.006)
        self.assertAlmostEqual(small[2] / 100, large[2] / 200, delta=0.006)
        self.assertAlmostEqual(small[3] / 100, large[3] / 200, delta=0.006)


if __name__ == "__main__":
    unittest.main()
