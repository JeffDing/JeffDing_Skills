"""
Add validation cases for torch.<module>.<api> on NPU:
1. PyTorch community lacks sufficient and direct API validations for some APIs, so this file is added.
2. This file validates torch.<module>.<api> (extendable).
"""

# NOTE:
# - Only `import torch` if you actually reference `torch.` somewhere; unused imports trigger FLAKE8 F401.
# - Do NOT `import unittest` (run_tests already does).
# - Do NOT `import torch_npu` (loaded automatically on Ascend when torch is imported).
# - If the test involves tensors, they MUST run on NPU — add the device_type line and use .to(device_type).
#   For pure-Python / non-computational APIs (e.g. namedtuple methods), no tensors, no device_type needed.

# Uncomment the next line ONLY if the test uses tensors:
# device_type = acc.type if (acc := torch.accelerator.current_accelerator()) else "cpu"

from torch.<module> import <Symbol>                       # the module under test
from torch.testing._internal.common_utils import TestCase, run_tests


class Test<Module>Api(TestCase):
    def test_<feature>_happy_path(self):
        # TODO: core positive case
        self.assertEqual(expected, actual)

    def test_<feature>_boundary(self):
        # TODO: boundary / edge case
        with self.assertRaises(ValueError):
            <call that should fail>()

    def test_<feature>_error(self):
        # TODO: error case
        with self.assertRaises(<ErrorType>):
            <call>


if __name__ == "__main__":
    run_tests()
