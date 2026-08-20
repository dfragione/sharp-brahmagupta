import unittest
import updater

class TestUpdater(unittest.TestCase):
    def test_version_parsing(self):
        self.assertEqual(updater.parse_version_tuple("1.2.0"), (1, 2, 0))
        self.assertEqual(updater.parse_version_tuple("v1.2.3"), (1, 2, 3))
        self.assertGreater(updater.parse_version_tuple("1.3.0"), updater.parse_version_tuple("1.2.0"))
        self.assertGreater(updater.parse_version_tuple("2.0.0"), updater.parse_version_tuple("1.9.9"))

    def test_get_current_version(self):
        ver = updater.get_current_version()
        self.assertEqual(ver, "1.2.0")

    def test_check_for_updates_graceful(self):
        res = updater.check_for_updates("https://0.0.0.0/nonexistent.json")
        self.assertTrue("success" in res)
        self.assertEqual(res["current_version"], "1.2.0")

if __name__ == "__main__":
    unittest.main()
