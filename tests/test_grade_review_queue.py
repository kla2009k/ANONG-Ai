import unittest

import numpy as np

from scripts.build_grade_expert_review_queue import build_review_rows


class GradeReviewQueueTests(unittest.TestCase):
    def test_queue_is_unreviewed_and_prioritizes_boundary_errors(self):
        manifest = [
            {"group_id": "g1", "cell_id": "1", "bethesda": "LSIL", "path": "a.png"},
            {"group_id": "g2", "cell_id": "2", "bethesda": "HSIL", "path": "b.png"},
            {"group_id": "g3", "cell_id": "3", "bethesda": "SCC", "path": "c.png"},
        ]
        probabilities = np.asarray([
            [0.01, 0.20, 0.78, 0.01],
            [0.01, 0.48, 0.50, 0.01],
            [0.01, 0.01, 0.90, 0.08],
        ])
        rows = build_review_rows(manifest, np.asarray([1, 2, 3]), probabilities, fold=1)
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(row["review_status"] == "pending" for row in rows))
        self.assertTrue(all(row["reviewer"] == "" for row in rows))
        self.assertIn("LSIL-HSIL", rows[0]["review_reason"])
        self.assertIn("HSIL-SCC", rows[2]["review_reason"])


if __name__ == "__main__":
    unittest.main()
