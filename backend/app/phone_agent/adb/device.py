"""Device control utilities for Android automation."""

import subprocess
import time

from app.core.logging import get_logger
from app.phone_agent.config.apps import APP_PACKAGES
from app.phone_agent.config.timing import TIMING_CONFIG

logger = get_logger("adb.device")


def get_current_app(device_id: str | None = None) -> str:
    """Get the currently focused app name."""
    adb_prefix = _get_adb_prefix(device_id)

    result = subprocess.run(
        adb_prefix + ["shell", "dumpsys", "window"], capture_output=True, text=True
    )
    output = result.stdout

    for line in output.split("\n"):
        if "mCurrentFocus" in line or "mFocusedApp" in line:
            for app_name, package in APP_PACKAGES.items():
                if package in line:
                    return app_name

    return "System Home"


def tap(
    x: int, y: int, device_id: str | None = None, delay: float | None = None
) -> None:
    """Tap at the specified coordinates."""
    if delay is None:
        delay = TIMING_CONFIG.device.default_tap_delay

    adb_prefix = _get_adb_prefix(device_id)
    logger.info(f"[ADB] Tap at ({x}, {y}) device={device_id or 'default'}")

    start_time = time.time()
    result = subprocess.run(
        adb_prefix + ["shell", "input", "tap", str(x), str(y)], capture_output=True
    )
    duration = time.time() - start_time
    
    if result.returncode != 0:
        logger.warning(f"[ADB] Tap command failed: {result.stderr.decode() if result.stderr else 'unknown error'}")
    else:
        logger.debug(f"[ADB] Tap completed in {duration:.3f}s")
    
    time.sleep(delay)


def double_tap(
    x: int, y: int, device_id: str | None = None, delay: float | None = None
) -> None:
    """Double tap at the specified coordinates."""
    if delay is None:
        delay = TIMING_CONFIG.device.default_double_tap_delay

    adb_prefix = _get_adb_prefix(device_id)
    logger.info(f"[ADB] Double tap at ({x}, {y}) device={device_id or 'default'}")

    start_time = time.time()
    subprocess.run(
        adb_prefix + ["shell", "input", "tap", str(x), str(y)], capture_output=True
    )
    time.sleep(TIMING_CONFIG.device.double_tap_interval)
    subprocess.run(
        adb_prefix + ["shell", "input", "tap", str(x), str(y)], capture_output=True
    )
    duration = time.time() - start_time
    logger.debug(f"[ADB] Double tap completed in {duration:.3f}s")
    time.sleep(delay)


def long_press(
    x: int,
    y: int,
    duration_ms: int = 3000,
    device_id: str | None = None,
    delay: float | None = None,
) -> None:
    """Long press at the specified coordinates."""
    if delay is None:
        delay = TIMING_CONFIG.device.default_long_press_delay

    adb_prefix = _get_adb_prefix(device_id)
    logger.info(f"[ADB] Long press at ({x}, {y}) duration={duration_ms}ms device={device_id or 'default'}")

    start_time = time.time()
    subprocess.run(
        adb_prefix
        + ["shell", "input", "swipe", str(x), str(y), str(x), str(y), str(duration_ms)],
        capture_output=True,
    )
    duration = time.time() - start_time
    logger.debug(f"[ADB] Long press completed in {duration:.3f}s")
    time.sleep(delay)


def swipe(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration_ms: int | None = None,
    device_id: str | None = None,
    delay: float | None = None,
) -> None:
    """Swipe from start to end coordinates."""
    if delay is None:
        delay = TIMING_CONFIG.device.default_swipe_delay

    adb_prefix = _get_adb_prefix(device_id)

    if duration_ms is None:
        dist_sq = (start_x - end_x) ** 2 + (start_y - end_y) ** 2
        duration_ms = int(dist_sq / 1000)
        duration_ms = max(1000, min(duration_ms, 2000))

    logger.info(f"[ADB] Swipe from ({start_x}, {start_y}) to ({end_x}, {end_y}) duration={duration_ms}ms device={device_id or 'default'}")

    start_time = time.time()
    subprocess.run(
        adb_prefix
        + [
            "shell",
            "input",
            "swipe",
            str(start_x),
            str(start_y),
            str(end_x),
            str(end_y),
            str(duration_ms),
        ],
        capture_output=True,
    )
    duration = time.time() - start_time
    logger.debug(f"[ADB] Swipe completed in {duration:.3f}s")
    time.sleep(delay)


def back(device_id: str | None = None, delay: float | None = None) -> None:
    """Press the back button."""
    if delay is None:
        delay = TIMING_CONFIG.device.default_back_delay

    adb_prefix = _get_adb_prefix(device_id)
    logger.info(f"[ADB] Back button pressed device={device_id or 'default'}")

    start_time = time.time()
    subprocess.run(
        adb_prefix + ["shell", "input", "keyevent", "4"], capture_output=True
    )
    duration = time.time() - start_time
    logger.debug(f"[ADB] Back completed in {duration:.3f}s")
    time.sleep(delay)


def home(device_id: str | None = None, delay: float | None = None) -> None:
    """Press the home button."""
    if delay is None:
        delay = TIMING_CONFIG.device.default_home_delay

    adb_prefix = _get_adb_prefix(device_id)
    logger.info(f"[ADB] Home button pressed device={device_id or 'default'}")

    start_time = time.time()
    subprocess.run(
        adb_prefix + ["shell", "input", "keyevent", "KEYCODE_HOME"], capture_output=True
    )
    duration = time.time() - start_time
    logger.debug(f"[ADB] Home completed in {duration:.3f}s")
    time.sleep(delay)


def launch_app(
    app_name: str, device_id: str | None = None, delay: float | None = None
) -> bool:
    """Launch an app by name."""
    if delay is None:
        delay = TIMING_CONFIG.device.default_launch_delay

    if app_name not in APP_PACKAGES:
        logger.warning(f"[ADB] App not found in APP_PACKAGES: {app_name}")
        return False

    adb_prefix = _get_adb_prefix(device_id)
    package = APP_PACKAGES[app_name]
    logger.info(f"[ADB] Launching app: {app_name} (package={package}) device={device_id or 'default'}")

    start_time = time.time()
    result = subprocess.run(
        adb_prefix
        + [
            "shell",
            "monkey",
            "-p",
            package,
            "-c",
            "android.intent.category.LAUNCHER",
            "1",
        ],
        capture_output=True,
    )
    duration = time.time() - start_time
    
    if result.returncode != 0:
        logger.warning(f"[ADB] Launch app failed: {result.stderr.decode() if result.stderr else 'unknown error'}")
    else:
        logger.debug(f"[ADB] Launch app completed in {duration:.3f}s")
    
    time.sleep(delay)
    return True


def _get_adb_prefix(device_id: str | None) -> list:
    """Get ADB command prefix with optional device specifier."""
    if device_id:
        return ["adb", "-s", device_id]
    return ["adb"]

