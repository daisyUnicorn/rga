"""Screenshot utilities for capturing Android device screen."""

import base64
import os
import subprocess
import tempfile
import uuid
from dataclasses import dataclass
from io import BytesIO

from PIL import Image

from app.core.logging import get_logger

logger = get_logger("screenshot")


@dataclass
class Screenshot:
    """Represents a captured screenshot."""
    base64_data: str
    width: int
    height: int
    is_sensitive: bool = False


def get_screenshot(device_id: str | None = None, timeout: int = 10) -> Screenshot:
    """Capture a screenshot from the connected Android device."""
    import time
    start_time = time.time()
    
    # Generate unique filename using UUID to avoid concurrent conflicts
    screenshot_uuid = str(uuid.uuid4())
    device_temp_file = f"/sdcard/tmp_{screenshot_uuid}.png"
    local_temp_path = os.path.join(tempfile.gettempdir(), f"screenshot_{screenshot_uuid}.png")
    adb_prefix = _get_adb_prefix(device_id)
    
    logger.info(f"[SCREENSHOT] Capturing screenshot device={device_id or 'default'} uuid={screenshot_uuid[:8]}")

    try:
        # Execute screenshot command with unique filename
        capture_start = time.time()
        result = subprocess.run(
            adb_prefix + ["shell", "screencap", "-p", device_temp_file],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        capture_duration = time.time() - capture_start
        logger.debug(f"[SCREENSHOT] Capture on device completed in {capture_duration:.3f}s, returncode={result.returncode}")

        # Check for ADB connection issues or command failure
        output = result.stdout + result.stderr
        if result.returncode != 0:
            logger.error(f"[SCREENSHOT] screencap command failed: returncode={result.returncode}, output={output}")
            return _create_fallback_screenshot(is_sensitive=False)
        
        # Check for empty/error output that indicates connection issues
        if "error:" in output.lower() or "device" in output.lower() and "not found" in output.lower():
            logger.error(f"[SCREENSHOT] ADB connection error: {output}")
            return _create_fallback_screenshot(is_sensitive=False)
        
        # Check for screenshot failure (sensitive screen)
        if "Status: -1" in output or "Failed" in output:
            logger.warning("[SCREENSHOT] Sensitive screen detected, using fallback")
            return _create_fallback_screenshot(is_sensitive=True)

        # Pull screenshot to local temp path
        pull_start = time.time()
        pull_result = subprocess.run(
            adb_prefix + ["pull", device_temp_file, local_temp_path],
            capture_output=True,
            text=True,
            timeout=10,  # Increased timeout for network transfer
        )
        pull_duration = time.time() - pull_start
        logger.debug(f"[SCREENSHOT] Pull to local completed in {pull_duration:.3f}s, returncode={pull_result.returncode}")
        
        # Check pull result
        if pull_result.returncode != 0:
            pull_output = pull_result.stdout + pull_result.stderr
            logger.error(f"[SCREENSHOT] Pull command failed: returncode={pull_result.returncode}, output={pull_output}")
            return _create_fallback_screenshot(is_sensitive=False)

        if not os.path.exists(local_temp_path):
            pull_output = pull_result.stdout + pull_result.stderr
            logger.warning(f"[SCREENSHOT] Pull failed, file not found locally. Pull output: {pull_output}")
            return _create_fallback_screenshot(is_sensitive=False)

        # Read and encode image
        img = Image.open(local_temp_path)
        width, height = img.size

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")
        file_size = len(buffered.getvalue()) / 1024  # KB

        # Cleanup local temp file
        os.remove(local_temp_path)

        # Cleanup device temp file (best effort, ignore errors)
        try:
            subprocess.run(
                adb_prefix + ["shell", "rm", device_temp_file],
                capture_output=True,
                text=True,
                timeout=5,
            )
        except Exception:
            # Ignore cleanup errors on device
            pass

        total_duration = time.time() - start_time
        logger.info(f"[SCREENSHOT] Success: {width}x{height}, {file_size:.1f}KB, total {total_duration:.2f}s")

        return Screenshot(
            base64_data=base64_data, width=width, height=height, is_sensitive=False
        )

    except subprocess.TimeoutExpired:
        total_duration = time.time() - start_time
        logger.error(f"[SCREENSHOT] Timeout after {total_duration:.2f}s (limit={timeout}s)")
        # Cleanup device temp file on error (best effort)
        try:
            subprocess.run(
                adb_prefix + ["shell", "rm", device_temp_file],
                capture_output=True,
                text=True,
                timeout=5,
            )
        except Exception:
            pass
        return _create_fallback_screenshot(is_sensitive=False)
    except Exception as e:
        total_duration = time.time() - start_time
        logger.error(f"[SCREENSHOT] Error after {total_duration:.2f}s: {e}")
        # Cleanup device temp file on error (best effort)
        try:
            subprocess.run(
                adb_prefix + ["shell", "rm", device_temp_file],
                capture_output=True,
                text=True,
                timeout=5,
            )
        except Exception:
            pass
        return _create_fallback_screenshot(is_sensitive=False)


def _get_adb_prefix(device_id: str | None) -> list:
    """Get ADB command prefix with optional device specifier."""
    if device_id:
        return ["adb", "-s", device_id]
    return ["adb"]


def _create_fallback_screenshot(is_sensitive: bool) -> Screenshot:
    """Create a black fallback image when screenshot fails."""
    default_width, default_height = 1080, 2400

    black_img = Image.new("RGB", (default_width, default_height), color="black")
    buffered = BytesIO()
    black_img.save(buffered, format="PNG")
    base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return Screenshot(
        base64_data=base64_data,
        width=default_width,
        height=default_height,
        is_sensitive=is_sensitive,
    )

