"""Timing configuration for Phone Agent."""

import os
from dataclasses import dataclass


@dataclass
class ActionTimingConfig:
    """Configuration for action handler timing delays."""
    keyboard_switch_delay: float = 1.0
    text_clear_delay: float = 1.0
    text_input_delay: float = 1.0
    keyboard_restore_delay: float = 1.0

    def __post_init__(self):
        self.keyboard_switch_delay = float(
            os.getenv("PHONE_AGENT_KEYBOARD_SWITCH_DELAY", self.keyboard_switch_delay)
        )
        self.text_clear_delay = float(
            os.getenv("PHONE_AGENT_TEXT_CLEAR_DELAY", self.text_clear_delay)
        )
        self.text_input_delay = float(
            os.getenv("PHONE_AGENT_TEXT_INPUT_DELAY", self.text_input_delay)
        )
        self.keyboard_restore_delay = float(
            os.getenv("PHONE_AGENT_KEYBOARD_RESTORE_DELAY", self.keyboard_restore_delay)
        )


@dataclass
class DeviceTimingConfig:
    """Configuration for device operation timing delays."""
    default_tap_delay: float = 1.0
    default_double_tap_delay: float = 1.0
    double_tap_interval: float = 0.1
    default_long_press_delay: float = 1.0
    default_swipe_delay: float = 1.0
    default_back_delay: float = 1.0
    default_home_delay: float = 1.0
    default_launch_delay: float = 1.0

    def __post_init__(self):
        self.default_tap_delay = float(
            os.getenv("PHONE_AGENT_TAP_DELAY", self.default_tap_delay)
        )
        self.default_double_tap_delay = float(
            os.getenv("PHONE_AGENT_DOUBLE_TAP_DELAY", self.default_double_tap_delay)
        )
        self.double_tap_interval = float(
            os.getenv("PHONE_AGENT_DOUBLE_TAP_INTERVAL", self.double_tap_interval)
        )
        self.default_long_press_delay = float(
            os.getenv("PHONE_AGENT_LONG_PRESS_DELAY", self.default_long_press_delay)
        )
        self.default_swipe_delay = float(
            os.getenv("PHONE_AGENT_SWIPE_DELAY", self.default_swipe_delay)
        )
        self.default_back_delay = float(
            os.getenv("PHONE_AGENT_BACK_DELAY", self.default_back_delay)
        )
        self.default_home_delay = float(
            os.getenv("PHONE_AGENT_HOME_DELAY", self.default_home_delay)
        )
        self.default_launch_delay = float(
            os.getenv("PHONE_AGENT_LAUNCH_DELAY", self.default_launch_delay)
        )


@dataclass
class TimingConfig:
    """Master timing configuration."""
    action: ActionTimingConfig
    device: DeviceTimingConfig

    def __init__(self):
        self.action = ActionTimingConfig()
        self.device = DeviceTimingConfig()


TIMING_CONFIG = TimingConfig()

