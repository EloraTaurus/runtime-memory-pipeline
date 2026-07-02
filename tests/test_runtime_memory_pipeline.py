from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_CODE = ROOT / "sample-code"
sys.path.insert(0, str(SAMPLE_CODE))

from runtime_memory.benchmark.runner import run
from runtime_memory.builder import build
from runtime_memory.validation import validate_binary_store


class RuntimeMemoryPipelineTests(unittest.TestCase):
    def test_build_validate_and_benchmark(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            markdown = work / "markdown"
            binary = work / "binary"
            sqlite = work / "sqlite" / "runtime_memory.sqlite3"
            shutil.copytree(ROOT / "sample-artifacts" / "markdown", markdown)

            result = build(markdown, binary, sqlite)
            validation = validate_binary_store(binary)

            self.assertEqual(result["manifest"]["fragment_count"], 5)
            self.assertTrue(sqlite.exists())
            self.assertTrue(validation["ok"], validation["errors"])
            self.assertEqual(validation["validated_count"], 5)

    def test_benchmark_report_shape(self) -> None:
        report = run(iterations=2)

        self.assertEqual({row["backend"] for row in report["summary"]}, {"markdown", "sqlite", "binary"})
        self.assertGreater(report["build"]["total_build_time_ms"], 0)
        self.assertGreater(report["storage_bytes"]["binary"], 0)
        self.assertGreater(report["storage_bytes"]["sqlite"], 0)
        self.assertGreater(report["storage_bytes"]["markdown"], 0)
        self.assertIn("No superiority claim", report["conclusion"])
        for rows in report["backends"].values():
            for row in rows:
                self.assertGreaterEqual(row["retrieval_latency_ms_avg"], 0)
                self.assertGreaterEqual(row["context_assembly_latency_ms_avg"], 0)
                self.assertGreaterEqual(row["end_to_end_latency_ms_avg"], 0)
                self.assertGreaterEqual(row["end_to_end_latency_ms_stddev"], 0)


if __name__ == "__main__":
    unittest.main()
