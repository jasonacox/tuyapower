"""Offline tests for tuyapower.deviceInfo() using a mocked tinytuya device."""

import unittest
from unittest import mock

import tuyapower


def fake_device(responses):
    """Return an OutletDevice replacement whose status() yields responses."""
    calls = {"n": 0}
    it = iter(responses)

    class Dev(object):
        def __init__(self, *args, **kwargs):
            pass

        def set_version(self, v):
            pass

        def status(self):
            calls["n"] += 1
            return next(it)

    return Dev, calls


@unittest.skipUnless(tuyapower.api == "tinytuya", "requires tinytuya")
class DeviceInfoTest(unittest.TestCase):
    def run_info(self, responses):
        dev, calls = fake_device(responses)
        with mock.patch.object(tuyapower.tinytuya, "OutletDevice", dev), \
                mock.patch.object(tuyapower, "sleep") as slept:
            result = tuyapower.deviceInfo("id", "10.0.0.1", "key", "3.3")
        return result, calls["n"], slept.call_count

    def test_power_data(self):
        (on, w, mA, V, err), n, _ = self.run_info(
            [{"dps": {"1": True, "18": 120, "19": 345, "20": 1201}}])
        self.assertEqual((on, w, mA, V, err), (True, 34.5, 120.0, 120.1, "OK"))
        self.assertEqual(n, 1)

    def test_tinytuya_error_is_reported_without_extra_retries(self):
        # tinytuya returns (not raises) an error dict when the device is
        # unreachable, and has already retried internally.
        err_resp = {"Error": "Network Error: Device Unreachable",
                    "Err": "905", "Payload": None}
        (on, w, mA, V, err), n, slept = self.run_info([err_resp] * 10)
        self.assertEqual(err, "Network Error: Device Unreachable")
        self.assertEqual((on, w, mA, V), (False, 0, 0, 0))
        self.assertEqual(n, 1)
        self.assertEqual(slept, 0)

    def test_no_power_dps(self):
        (on, w, mA, V, err), _, _ = self.run_info([{"dps": {"1": False}}])
        self.assertEqual((on, err), (False, "Power data unavailable"))


if __name__ == "__main__":
    unittest.main()
