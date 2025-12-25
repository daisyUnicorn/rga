"""
GELab Parser - Ported from gelab-zero/copilot_tools/parser_0920_summary.py.

Handles parsing of GELab model output format:
<THINK> thinking content </THINK>
explain:explanation\taction:ACTION_TYPE\tparam:value\tsummary:step summary
"""

import re
from collections import OrderedDict
from typing import Any

from app.core.logging import get_logger

logger = get_logger("gelab_parser")


class GELabParser:
    """
    Parser for GELab model output.

    Handles:
    - <THINK>...</THINK> tags with typo tolerance (TINK, think, THIN)
    - Tab-separated key:value pairs
    - Point coordinate parsing (supports "x,y" and "x y" formats)
    """

    def str2action(self, command_str: str) -> OrderedDict:
        """
        Parse model output string to action dictionary.

        Args:
            command_str: Raw model output string

        Returns:
            OrderedDict with parsed action fields

        Expected format:
            <THINK> cot </THINK>
            explain:xxx\taction:xx\tvalue:xxx\tsummary:xxx
        """
        command_str = command_str.strip()

        # Normalize THINK tags: fix typos, case, and spacing
        command_str = (
            command_str
            .replace("<TINK>", "<THINK>").replace("</TINK>", "</THINK>")
            .replace("<think>", "<THINK>").replace("</think>", "</THINK>")
            .replace("<THIN>", "<THINK>").replace("</THIN>", "</THINK>")
        )
        command_str = re.sub(
            r"<\s*/?THINK\s*>",
            lambda m: "<THINK>" if "/" not in m.group() else "</THINK>",
            command_str,
            flags=re.IGNORECASE
        )

        # Extract CoT and key-value parts
        try:
            cot_part = command_str.split("<THINK>")[1].split("</THINK>")[0].strip()
            kv_part = command_str.split("</THINK>")[1].strip()
        except IndexError:
            logger.warning("Missing <THINK> tags, treating entire response as kv")
            kv_part = command_str
            cot_part = ""

        action = OrderedDict()
        action['cot'] = cot_part

        # Split by tab separator
        kvs = [kv.strip() for kv in kv_part.split("\t") if kv.strip()]

        for kv in kvs:
            if ":" not in kv:
                continue

            key = kv.split(":", 1)[0].strip()
            value = kv.split(":", 1)[1].strip()

            if key == "action":
                action['action'] = value
            elif key == "summary":
                action['summary'] = value
            elif "point" in key:
                # Parse point format: "x,y" or "x y"
                try:
                    coords = value.replace(",", " ").split()
                    if len(coords) < 2:
                        raise ValueError(f"Expected 2 coordinates, got {len(coords)}")

                    x, y = int(coords[0]), int(coords[1])
                    action[key] = [x, y]

                except (ValueError, IndexError) as e:
                    raise ValueError(
                        f"[GELabParser Error] Failed to parse point '{value}' for key '{key}': {str(e)}. "
                        f"Expected format: 'x,y' or 'x y' with integer values"
                    ) from e
            else:
                action[key] = value

        return action

    def action2action(self, action: dict) -> OrderedDict:
        """
        Validate and standardize action format.

        Args:
            action: Raw parsed action dictionary

        Returns:
            Standardized OrderedDict with required fields
        """
        assert "action" in action or "action_type" in action, \
            f"action {action} should have action or action_type field"

        explain = action.get('explain', '')
        cot = action.get('cot', '')
        summary = action.get('summary', '')
        action_type = action.get('action_type', action.get('action', None))

        return_action = OrderedDict({
            "cot": cot,
            "explain": explain,
            "action": action_type,
            "summary": summary
        })

        # Add type-specific fields
        if action_type == "TYPE":
            assert "value" in action, f"TYPE action should have value field"
            return_action["value"] = action['value']
            if "point" in action:
                return_action["point"] = action['point']

        elif action_type == "CLICK":
            assert "point" in action, f"CLICK action should have point field"
            return_action["point"] = action['point']

        elif action_type == "AWAKE":
            assert "value" in action, f"AWAKE action should have value field"
            return_action["value"] = action['value']

        elif action_type == "INFO":
            assert "value" in action, f"INFO action should have value field"
            return_action["value"] = action['value']

        elif action_type == "WAIT":
            assert "value" in action, f"WAIT action should have value field"
            return_action["value"] = action['value']

        elif action_type == "COMPLETE":
            assert "return" in action, f"COMPLETE action should have return field"
            return_action["return"] = action['return']

        elif action_type == "ABORT":
            if "value" in action:
                return_action["value"] = action['value']

        elif action_type == "SLIDE":
            assert "point1" in action, f"SLIDE action should have point1 field"
            assert "point2" in action, f"SLIDE action should have point2 field"
            return_action["point1"] = action['point1']
            return_action["point2"] = action['point2']

        elif action_type == "LONGPRESS":
            assert "point" in action, f"LONGPRESS action should have point field"
            return_action["point"] = action['point']

        else:
            logger.warning(f"Unknown action type: {action_type}")

        return return_action


def denormalize_point(point: list[int], width: int, height: int) -> list[int]:
    """
    Convert GELab normalized coordinates (0-1000) to pixel coordinates.

    Args:
        point: [x, y] in 0-1000 coordinate system
        width: Screen width in pixels
        height: Screen height in pixels

    Returns:
        [x, y] in pixel coordinates
    """
    x_normalized, y_normalized = point
    x_pixel = int(x_normalized * width / 1000)
    y_pixel = int(y_normalized * height / 1000)
    return [x_pixel, y_pixel]


def normalize_point(point: list[int], width: int, height: int) -> list[int]:
    """
    Convert pixel coordinates to GELab normalized coordinates (0-1000).

    Args:
        point: [x, y] in pixel coordinates
        width: Screen width in pixels
        height: Screen height in pixels

    Returns:
        [x, y] in 0-1000 coordinate system
    """
    x_pixel, y_pixel = point
    x_normalized = int(x_pixel * 1000 / width)
    y_normalized = int(y_pixel * 1000 / height)
    return [x_normalized, y_normalized]
