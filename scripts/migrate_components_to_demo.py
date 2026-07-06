#!/usr/bin/env python3
"""Move UI component prefabs from common.kzproj to demo.kzproj."""

from __future__ import annotations

import re
from pathlib import Path

COMMON = Path("/workspace/IVI/common/common.kzproj")
DEMO = Path("/workspace/IVI/demo/demo.kzproj")

# 1-based inclusive line ranges in common.kzproj
PREFAB_RANGE = (9972, 14691)
STATE_MANAGER_RANGE = (54682, 55572)
TOGGLE_STATE_PROP_RANGE = (56944, 56990)
LABEL_TEXT_PROP_RANGE = (56991, 57045)
SLIDER_VALUE_PROP_RANGE = (57046, 57095)  # Slider.Value also moves with Slider prefab

DEMO_PREFAB_INSERT_BEFORE = 8194  # before DemoPage
DEMO_STATE_MANAGERS_CHILDREN_LINE = 43323  # <children /> under State Managers


def transform_paths(text: str) -> str:
    text = text.replace("kzb://common/Prefabs/", "kzb://demo/Prefabs/")
    text = text.replace("common/Prefabs/", "demo/Prefabs/")
    text = text.replace("kzb://common/State Managers/", "kzb://demo/State Managers/")
    text = text.replace("common/State Managers/", "demo/State Managers/")
    return text


def slice_lines(lines: list[str], start: int, end: int) -> list[str]:
    return lines[start - 1 : end]


def remove_range(lines: list[str], start: int, end: int) -> list[str]:
    return lines[: start - 1] + lines[end:]


def remove_property_editor_entries(content: str) -> str:
  patterns = [
      r'\s*<d2p1:KeyValueOfstringPropertyEditorViewModeData1Qk_SHUva>\s*'
      r'<d2p1:Key>kzb://common/Prefabs/[^<]+</d2p1:Key>.*?</d2p1:KeyValueOfstringPropertyEditorViewModeData1Qk_SHUva>',
      r'\s*<d2p1:KeyValueOfstringPropertyEditorViewModeData1Qk_SHUva>\s*'
      r'<d2p1:Key>kzb://common/State Managers/ToggleSwitchState[^<]*</d2p1:Key>.*?</d2p1:KeyValueOfstringPropertyEditorViewModeData1Qk_SHUva>',
      r'\s*<d2p1:KeyValueOfstringPropertyEditorViewModeData1Qk_SHUva>\s*'
      r'<d2p1:Key>kzb://common/Property Types/ToggleSwitch[^<]*</d2p1:Key>.*?</d2p1:KeyValueOfstringPropertyEditorViewModeData1Qk_SHUva>',
  ]
  for pattern in patterns:
      content = re.sub(pattern, "", content, flags=re.DOTALL)
  return content


def remove_composition_slider_entry(content: str) -> str:
    pattern = (
        r'\s*<CompositionViewModel>\s*<currentlyActive>false</currentlyActive>\s*'
        r'<projectItemReference>.*?common/Prefabs/Slider/Slider/.*?</CompositionViewModel>'
    )
    return re.sub(pattern, "", content, flags=re.DOTALL)


def main() -> None:
    common_lines = COMMON.read_text(encoding="utf-8").splitlines(keepends=True)
    demo_lines = DEMO.read_text(encoding="utf-8").splitlines(keepends=True)

    prefab_block = transform_paths("".join(slice_lines(common_lines, *PREFAB_RANGE)))
    state_manager_block = transform_paths("".join(slice_lines(common_lines, *STATE_MANAGER_RANGE)))
    toggle_state_prop = slice_lines(common_lines, *TOGGLE_STATE_PROP_RANGE)

    # --- demo: insert prefabs before DemoPage ---
    insert_at = DEMO_PREFAB_INSERT_BEFORE - 1
    demo_lines = demo_lines[:insert_at] + [prefab_block] + demo_lines[insert_at:]

    # --- demo: replace empty State Managers children ---
    sm_children_line = None
    for i, line in enumerate(demo_lines):
        if line.strip() == "<SerializedName>State Managers</SerializedName>":
            for j in range(i + 1, min(i + 6, len(demo_lines))):
                if demo_lines[j].strip() == "<children />":
                    sm_children_line = j
                    break
            break
    if sm_children_line is None:
        raise RuntimeError("Could not find empty State Managers <children /> in demo.kzproj")
    demo_lines[sm_children_line] = "      <children>\n" + state_manager_block + "      </children>\n"

    # --- demo: add ToggleSwitch.State property type if missing ---
    demo_text = "".join(demo_lines)
    if "<d3p1:Key>ToggleSwitch.State</d3p1:Key>" not in demo_text:
        marker = "    </d2p1:propertyTypes>\n  </projectsPropertyTypeLibrary>"
        if marker not in demo_text:
            raise RuntimeError("Could not find demo propertyTypes closing marker")
        demo_text = demo_text.replace(marker, "".join(toggle_state_prop) + marker, 1)

    # --- demo: update prefab references ---
    demo_text = demo_text.replace("kzb://common/Prefabs/", "kzb://demo/Prefabs/")
    DEMO.write_text(demo_text, encoding="utf-8")

    # --- common: remove moved blocks (bottom-up) ---
    common_lines = COMMON.read_text(encoding="utf-8").splitlines(keepends=True)
    for start, end in sorted(
        [PREFAB_RANGE, STATE_MANAGER_RANGE, SLIDER_VALUE_PROP_RANGE, LABEL_TEXT_PROP_RANGE, TOGGLE_STATE_PROP_RANGE],
        reverse=True,
    ):
        common_lines = remove_range(common_lines, start, end)

    common_text = "".join(common_lines)
    common_text = remove_property_editor_entries(common_text)
    common_text = remove_composition_slider_entry(common_text)

    # Remove LabelText preview reference from common Screen (component no longer in common)
    common_text = common_text.replace(
        "<d15p1:pathString>common/Prefabs/LabelText/</d15p1:pathString>",
        "<d15p1:pathString></d15p1:pathString>",
    )

    COMMON.write_text(common_text, encoding="utf-8")

    print("Migration complete.")
    print(f"  Inserted prefabs into demo before line {DEMO_PREFAB_INSERT_BEFORE}")
    print(f"  Moved ToggleSwitchState into demo State Managers")
    print(f"  Updated kzb://common/Prefabs/* -> kzb://demo/Prefabs/* in demo")


if __name__ == "__main__":
    main()
