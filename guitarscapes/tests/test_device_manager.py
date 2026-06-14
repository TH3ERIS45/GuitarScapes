"""Tests for audio device manager."""

from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

from guitarscapes.audio.device_manager import AudioDeviceManager, AudioDeviceInfo


class TestAudioDeviceManager:
    """Test suite for AudioDeviceManager."""

    def _mock_devices(self):
        """Create mock sounddevice query results."""
        return [
            {
                "name": "Built-in Microphone",
                "max_input_channels": 2,
                "max_output_channels": 0,
                "default_samplerate": 44100.0,
            },
            {
                "name": "USB Audio Interface",
                "max_input_channels": 2,
                "max_output_channels": 2,
                "default_samplerate": 48000.0,
            },
            {
                "name": "Speakers",
                "max_input_channels": 0,
                "max_output_channels": 2,
                "default_samplerate": 44100.0,
            },
        ]

    @patch("guitarscapes.audio.device_manager.sd")
    def test_lists_input_devices_only(self, mock_sd):
        """Should filter out output-only devices."""
        mock_sd.query_devices.return_value = self._mock_devices()
        mock_sd.default.device = (0, 2)

        dm = AudioDeviceManager()
        dm.refresh_devices()
        devices = dm.get_input_devices()

        # Only devices with max_input_channels > 0
        assert len(devices) == 2
        assert all(d.channels > 0 for d in devices)

    @patch("guitarscapes.audio.device_manager.sd")
    def test_get_default_device(self, mock_sd):
        """Should identify the default input device."""
        mock_sd.query_devices.return_value = self._mock_devices()
        mock_sd.default.device = (0, 2)

        dm = AudioDeviceManager()
        dm.refresh_devices()
        default = dm.get_default_device()

        assert default is not None
        assert default.is_default

    @patch("guitarscapes.audio.device_manager.sd")
    def test_select_device_by_index(self, mock_sd):
        """Should select a device by its index."""
        mock_sd.query_devices.return_value = self._mock_devices()
        mock_sd.default.device = (0, 2)

        dm = AudioDeviceManager()
        dm.refresh_devices()
        device = dm.select_device(1)

        assert device.name == "USB Audio Interface"

    @patch("guitarscapes.audio.device_manager.sd")
    def test_select_invalid_device_raises(self, mock_sd):
        """Selecting a non-existent device should raise an error."""
        mock_sd.query_devices.return_value = self._mock_devices()
        mock_sd.default.device = (0, 2)

        dm = AudioDeviceManager()
        dm.refresh_devices()

        with pytest.raises(Exception):
            dm.select_device(99)

    @patch("guitarscapes.audio.device_manager.sd")
    def test_empty_device_list(self, mock_sd):
        """Should handle no available devices."""
        mock_sd.query_devices.return_value = []
        mock_sd.default.device = (None, None)

        dm = AudioDeviceManager()
        dm.refresh_devices()
        devices = dm.get_input_devices()

        assert len(devices) == 0
        assert dm.get_default_device() is None
