import unittest

from import_utils import import_local


class TestNodesImport(unittest.TestCase):
    def test_nodes_imports_outside_comfyui(self):
        nodes = import_local("nodes")
        self.assertTrue(nodes.NODE_CLASS_MAPPINGS)
        self.assertIn("LogicGateCompare", nodes.NODE_CLASS_MAPPINGS)

        try:
            import folder_paths  # noqa: F401
            in_comfyui = True
        except ModuleNotFoundError:
            in_comfyui = False

        if not in_comfyui:
            # io_node is intentionally skipped outside ComfyUI.
            self.assertNotIn("SleepNodeAny", nodes.NODE_CLASS_MAPPINGS)

