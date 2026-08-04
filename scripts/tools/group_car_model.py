#!/usr/bin/env python3
"""Regroup the `car` prefab (IVI/KanziProject/car/Car.kzproj, truck.glb) to the standard
truck grouping in docs/truck-model-grouping-spec.md.

Target tree (groups without meshes are created as empty placeholders):

    Car
    ├── Body
    │   ├── Cab_Shell / Chassis_Frame / Interior (a11 + SW) / Glass_Static (a17)
    │   └── Fifth_Wheel (empty) ▸ Trailer_Anchor (empty)
    ├── Doors
    │   ├── Door_FL ▸ DoorShell_FL / Window_FL / Mirror_L
    │   └── Door_FR ▸ DoorShell_FR / Window_FR / Mirror_R
    ├── Wheels
    │   ├── Steer_FL ▸ Wheel_FL, Steer_FR ▸ Wheel_FR (front, kingpin + axle pivots)
    │   └── Wheel_RL / Wheel_RR (rear, axle pivots)
    ├── Lights   ← Headlights (a05, combined lens) + empty per-lamp placeholders
    └── Movables ← empty placeholders (Wiper_* / Grille_Front / ...)

Group pivots are placed on physical hinge/axle positions (spec §5); the mesh
vertices are baked in model space, so every group pivot is compensated by an
inverse translation on the child group / mesh nodes (net transform identity).

Mesh-to-group assignment derives from truck.glb spatial + material analysis
(axes: +Z front, +X left, Y up):
  a17 uses the window glass material at the windshield position -> Glass_Static;
  a05 uses HL_Glass across the front -> headlight lens; a11 + SW sit inside the
  cab -> Interior; low chassis/bumper/step meshes -> Chassis_Frame; the rest of
  the shell -> Cab_Shell. Door children split into shell / window / mirror.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

CAR_KZPROJ = Path(__file__).resolve().parents[2] / "IVI" / "KanziProject" / "car" / "Car.kzproj"

Vec = tuple[float, float, float]

# ---------------------------------------------------------------------------
# Mesh assignment tables (node names inside the current car prefab)
# ---------------------------------------------------------------------------

CHASSIS_MESHES = ["a01", "a02", "a03", "a04", "a06", "a07", "a09", "a10", "a45", "a46"]
CAB_MESHES = [
    "a08", "a18", "a19", "a19.3", "a20", "a21", "a21.1", "a21.2", "a22", "a23",
    "a24", "a25", "a26", "a28", "a29", "a30", "a31", "a32",
]
GLASS_MESHES = ["a17"]          # windshield (same glass material as windows)
INTERIOR_MESHES = ["a11"]       # seat/dashboard block; SW (steering wheel) group joins it
HEADLIGHT_MESHES = ["a05"]      # HL_Glass lens strip spanning both sides (not yet split L/R)

DOORSHELL_FL = ["a18.002", "a19.1", "a21.3", "a27.1"]
WINDOW_FL = ["window_L"]
MIRROR_L = ["a26.002", "a31.002"]
DOORSHELL_FR = ["a18.1", "a19.2", "a21.4", "a27"]
WINDOW_FR = ["window_R"]
MIRROR_R = ["a26.1", "a31.1"]

WHEEL_FL = ["a40", "a41", "a42", "a43", "a44"]
WHEEL_FR = ["a53", "a54", "a55", "a56", "a57"]
WHEEL_RL = ["a47", "a48", "a49", "a50", "a51", "a52"]
WHEEL_RR = ["a58", "a59", "a60", "a61", "a62", "a63"]

# ---------------------------------------------------------------------------
# Pivots in model space (meters), from truck.glb bounding-box analysis
# ---------------------------------------------------------------------------

DOOR_PIVOT_L: Vec = (1.59, 3.0, 3.79)      # front-edge hinge, vertical axis
DOOR_PIVOT_R: Vec = (-1.59, 3.0, 3.79)
WINDOW_PIVOT_L: Vec = (1.59, 3.18, 3.03)   # glass bottom-center
WINDOW_PIVOT_R: Vec = (-1.59, 3.18, 3.03)
MIRROR_PIVOT_L: Vec = (1.76, 3.54, 3.40)   # fold axis at arm mount
MIRROR_PIVOT_R: Vec = (-1.76, 3.54, 3.40)
WHEEL_PIVOT_FL: Vec = (1.49, 0.76, 2.20)   # wheel center / kingpin axis
WHEEL_PIVOT_FR: Vec = (-1.49, 0.76, 2.20)
WHEEL_PIVOT_RL: Vec = (1.30, 0.76, -3.14)
WHEEL_PIVOT_RR: Vec = (-1.30, 0.76, -3.14)
FIFTH_WHEEL_PIVOT: Vec = (0.0, 1.3, -3.14)  # above rear axle (placeholder)

EMPTY_LIGHT_GROUPS = [
    "Headlight_L", "Headlight_R", "DRL_L", "DRL_R", "FogLight_L", "FogLight_R",
    "TurnSignal_FL", "TurnSignal_FR", "TurnSignal_RL", "TurnSignal_RR",
    "Taillight_L", "Taillight_R", "ReverseLight_L", "ReverseLight_R",
    "MarkerLights", "Worklight",
]
EMPTY_MOVABLE_GROUPS = [
    "Wiper_L", "Wiper_R", "Grille_Front", "ChargePort_Door", "FuelCap", "SunVisor",
]


def neg(v: Vec) -> Vec:
    return (-v[0], -v[1], -v[2])


def sub(a: Vec, b: Vec) -> Vec:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def fmt(v: float) -> str:
    return f"{v:g}"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


# ---------------------------------------------------------------------------
# kzproj XML block parsing (line-based, same approach as the original script)
# ---------------------------------------------------------------------------

def parse_project_items(lines: list[str], children_start: int) -> tuple[list[dict], int]:
    """Parse direct-child <ProjectItem> blocks; return (items, children_end_line)."""
    items: list[dict] = []
    i = children_start + 1
    while i < len(lines):
        if lines[i].strip() == "</children>":
            return items, i
        if lines[i].strip().startswith("<ProjectItem"):
            depth = 0
            start = i
            j = i
            while j < len(lines):
                if re.search(r"<ProjectItem[\s>]", lines[j]):
                    depth += 1
                if "</ProjectItem>" in lines[j]:
                    depth -= 1
                    if depth == 0:
                        block = "".join(lines[start : j + 1])
                        sn = re.search(r"<SerializedName>([^<]+)</SerializedName>", block)
                        typ = re.search(r'i:type="d\d+p\d+:([^"]+)"', block)
                        items.append(
                            {
                                "block": block,
                                "name": sn.group(1) if sn else "?",
                                "type": typ.group(1) if typ else "?",
                            }
                        )
                        i = j
                        break
                j += 1
        i += 1
    raise RuntimeError("</children> terminator not found")


def parse_block_children(block: str) -> list[dict]:
    lines = block.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.strip() == "<children>":
            items, _ = parse_project_items(lines, i)
            return items
        if line.strip() == "<children />":
            return []
    return []


def set_mesh_translation(block: str, t: Vec) -> str:
    """Set the translation of a mesh node's Node3D.RenderTransformation."""
    pattern = re.compile(
        r"(<d(\d+)p1:translation[^>]*>\s*"
        r"<d(\d+)p1:_x>)[^<]*(</d\3p1:_x>\s*"
        r"<d\3p1:_y>)[^<]*(</d\3p1:_y>\s*"
        r"<d\3p1:_z>)[^<]*(</d\3p1:_z>)",
        re.DOTALL,
    )
    new_block, count = pattern.subn(
        lambda m: m.group(1) + fmt(t[0]) + m.group(4) + fmt(t[1]) + m.group(5) + fmt(t[2]) + m.group(6),
        block,
    )
    if count != 1:
        raise RuntimeError(f"expected exactly 1 translation in mesh block, found {count}")
    return new_block


# ---------------------------------------------------------------------------
# Node XML generation
# ---------------------------------------------------------------------------

def make_empty_node(name: str, children_xml: str, translation: Vec | None = None) -> str:
    ts = now_iso()
    transform_xml = ""
    if translation is not None:
        tx, ty, tz = (fmt(v) for v in translation)
        transform_xml = f"""
                <d8p1:KeyValueOfstringDynamicPropertyeuDbPpRS>
                  <d8p1:Key>Node3D.RenderTransformation</d8p1:Key>
                  <d8p1:Value>
                    <categoryOverride
                      i:nil="true" />
                    <isHidden
                      i:nil="true" />
                    <isReadOnly
                      i:nil="true" />
                    <propertyTypeReference>Node3D.RenderTransformation</propertyTypeReference>
                    <value xmlns:d11p1="http://schemas.datacontract.org/2004/07/Rightware.Kanzi.Tool.Logic.Base.DataTypes"
                      i:type="d11p1:SRTTransformation">
                      <d11p1:isScaleUniform>true</d11p1:isScaleUniform>
                      <d11p1:rotation xmlns:d12p1="http://schemas.datacontract.org/2004/07/System.Windows.Media.Media3D">
                        <d12p1:_x>0</d12p1:_x>
                        <d12p1:_y>0</d12p1:_y>
                        <d12p1:_z>0</d12p1:_z>
                      </d11p1:rotation>
                      <d11p1:scale xmlns:d12p1="http://schemas.datacontract.org/2004/07/System.Windows.Media.Media3D">
                        <d12p1:_x>1</d12p1:_x>
                        <d12p1:_y>1</d12p1:_y>
                        <d12p1:_z>1</d12p1:_z>
                      </d11p1:scale>
                      <d11p1:translation xmlns:d12p1="http://schemas.datacontract.org/2004/07/System.Windows.Media.Media3D">
                        <d12p1:_x>{tx}</d12p1:_x>
                        <d12p1:_y>{ty}</d12p1:_y>
                        <d12p1:_z>{tz}</d12p1:_z>
                      </d11p1:translation>
                    </value>
                  </d8p1:Value>
                </d8p1:KeyValueOfstringDynamicPropertyeuDbPpRS>"""

    children_block = (
        f"<children>\n{children_xml}                  </children>"
        if children_xml
        else "<children />"
    )
    return f"""                <ProjectItem
                  i:type="d7p1:EmptyNode">
                  <properties xmlns:d8p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays" xmlns="http://schemas.datacontract.org/2004/07/Rightware.Kanzi.Tool.Logic.Properties">
                    <d8p1:KeyValueOfstringDynamicPropertyeuDbPpRS>
                      <d8p1:Key>Tags</d8p1:Key>
                      <d8p1:Value>
                        <categoryOverride
                          i:nil="true" />
                        <isHidden
                          i:nil="true" />
                        <isReadOnly
                          i:nil="true" />
                        <propertyTypeReference>Tags</propertyTypeReference>
                        <value xmlns:d11p1="http://schemas.datacontract.org/2004/07/Rightware.Kanzi.Tool.Logic.Project"
                          i:type="d11p1:ArrayOfProjectItemReference" />
                      </d8p1:Value>
                    </d8p1:KeyValueOfstringDynamicPropertyeuDbPpRS>{transform_xml}
                    <d8p1:KeyValueOfstringDynamicPropertyeuDbPpRS>
                      <d8p1:Key>Name</d8p1:Key>
                      <d8p1:Value>
                        <categoryOverride
                          i:nil="true" />
                        <isHidden
                          i:nil="true" />
                        <isReadOnly
                          i:nil="true" />
                        <propertyTypeReference>Name</propertyTypeReference>
                        <value xmlns:d11p1="http://www.w3.org/2001/XMLSchema"
                          i:type="d11p1:string">{name}</value>
                      </d8p1:Value>
                    </d8p1:KeyValueOfstringDynamicPropertyeuDbPpRS>
                    <d8p1:KeyValueOfstringDynamicPropertyeuDbPpRS>
                      <d8p1:Key>CreationTime</d8p1:Key>
                      <d8p1:Value>
                        <categoryOverride
                          i:nil="true" />
                        <isHidden
                          i:nil="true" />
                        <isReadOnly
                          i:nil="true" />
                        <propertyTypeReference>CreationTime</propertyTypeReference>
                        <value xmlns:d11p1="http://www.w3.org/2001/XMLSchema"
                          i:type="d11p1:dateTime">{ts}</value>
                      </d8p1:Value>
                    </d8p1:KeyValueOfstringDynamicPropertyeuDbPpRS>
                  </properties>
                  <SerializedName>{name}</SerializedName>
                  {children_block}
                  <dataSource
                    i:nil="true" />
                  <isHidden>false</isHidden>
                  <isReadOnly>false</isReadOnly>
                </ProjectItem>
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    text = CAR_KZPROJ.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    # Locate the car root node: Prefabs folder -> prefab item "Car" -> node "Car".
    prefabs_line = next(
        i for i, l in enumerate(lines) if "<SerializedName>Prefabs</SerializedName>" in l
    )
    car_names = [
        i for i, l in enumerate(lines[prefabs_line:], start=prefabs_line)
        if "<SerializedName>Car</SerializedName>" in l
    ]
    if len(car_names) < 2:
        raise RuntimeError("Car prefab root node not found under Prefabs")
    car_root_line = car_names[1]

    children_start = next(
        j for j in range(car_root_line, car_root_line + 10) if lines[j].strip() == "<children>"
    )
    items, children_end = parse_project_items(lines, children_start)

    # Collect mesh blocks (recursively) and keep special blocks intact.
    mesh_by_name: dict[str, str] = {}
    sw_block: str | None = None
    static_blocks: list[str] = []

    def collect(item: dict) -> None:
        nonlocal sw_block
        if item["type"] == "MeshNode":
            if item["name"] in mesh_by_name:
                raise RuntimeError(f"duplicate mesh node name {item['name']}")
            mesh_by_name[item["name"]] = item["block"]
        elif item["type"] == "EmptyNode":
            if item["name"] == "SW":
                sw_block = item["block"]
            else:
                for child in parse_block_children(item["block"]):
                    collect(child)
        else:
            static_blocks.append(item["block"])

    for item in items:
        collect(item)

    if sw_block is None:
        raise RuntimeError("SW (steering wheel) group not found")

    assigned: set[str] = set()

    def meshes(names: list[str], compensation: Vec | None = None) -> str:
        xml = ""
        for name in names:
            if name not in mesh_by_name:
                raise RuntimeError(f"mesh node {name} not found in car prefab")
            block = mesh_by_name[name]
            if compensation is not None:
                block = set_mesh_translation(block, compensation)
            xml += block
            assigned.add(name)
        return xml

    # --- Body -------------------------------------------------------------
    body_xml = (
        make_empty_node("Cab_Shell", meshes(CAB_MESHES))
        + make_empty_node("Chassis_Frame", meshes(CHASSIS_MESHES))
        + make_empty_node(
            "Fifth_Wheel", make_empty_node("Trailer_Anchor", ""), FIFTH_WHEEL_PIVOT
        )
        + make_empty_node("Interior", meshes(INTERIOR_MESHES) + sw_block)
        + make_empty_node("Glass_Static", meshes(GLASS_MESHES))
    )
    body = make_empty_node("Body", body_xml)

    # --- Doors (pivot on hinge, children compensated) -----------------------
    def door(name: str, pivot: Vec, shell: list[str], window: list[str],
             window_pivot: Vec, mirror: list[str], mirror_pivot: Vec,
             side: str, mirror_name: str) -> str:
        inner = (
            make_empty_node(f"DoorShell_{side}", meshes(shell), neg(pivot))
            + make_empty_node(
                f"Window_{side}", meshes(window, neg(window_pivot)), sub(window_pivot, pivot)
            )
            + make_empty_node(
                mirror_name, meshes(mirror, neg(mirror_pivot)), sub(mirror_pivot, pivot)
            )
        )
        return make_empty_node(name, inner, pivot)

    doors_xml = (
        door("Door_FL", DOOR_PIVOT_L, DOORSHELL_FL, WINDOW_FL, WINDOW_PIVOT_L,
             MIRROR_L, MIRROR_PIVOT_L, "FL", "Mirror_L")
        + door("Door_FR", DOOR_PIVOT_R, DOORSHELL_FR, WINDOW_FR, WINDOW_PIVOT_R,
               MIRROR_R, MIRROR_PIVOT_R, "FR", "Mirror_R")
    )
    doors = make_empty_node("Doors", doors_xml)

    # --- Wheels (Steer_* yaw pivot ▸ Wheel_* roll pivot) --------------------
    wheels_xml = (
        make_empty_node(
            "Steer_FL",
            make_empty_node("Wheel_FL", meshes(WHEEL_FL, neg(WHEEL_PIVOT_FL))),
            WHEEL_PIVOT_FL,
        )
        + make_empty_node(
            "Steer_FR",
            make_empty_node("Wheel_FR", meshes(WHEEL_FR, neg(WHEEL_PIVOT_FR))),
            WHEEL_PIVOT_FR,
        )
        + make_empty_node("Wheel_RL", meshes(WHEEL_RL, neg(WHEEL_PIVOT_RL)), WHEEL_PIVOT_RL)
        + make_empty_node("Wheel_RR", meshes(WHEEL_RR, neg(WHEEL_PIVOT_RR)), WHEEL_PIVOT_RR)
    )
    wheels = make_empty_node("Wheels", wheels_xml)

    # --- Lights / Movables (mostly empty placeholders) ----------------------
    lights_xml = make_empty_node("Headlights", meshes(HEADLIGHT_MESHES))
    for name in EMPTY_LIGHT_GROUPS:
        lights_xml += make_empty_node(name, "")
    lights = make_empty_node("Lights", lights_xml)

    movables_xml = ""
    for name in EMPTY_MOVABLE_GROUPS:
        movables_xml += make_empty_node(name, "")
    movables = make_empty_node("Movables", movables_xml)

    unassigned = sorted(set(mesh_by_name) - assigned)
    if unassigned:
        raise RuntimeError(f"unassigned meshes left over: {unassigned}")

    new_children = body + doors + wheels + lights + movables + "".join(static_blocks)
    new_lines = lines[: children_start + 1] + [new_children] + lines[children_end:]
    CAR_KZPROJ.write_text("".join(new_lines), encoding="utf-8")

    print("Car prefab regrouped to truck-model-grouping-spec layout:")
    print(f"  Body:   Cab_Shell {len(CAB_MESHES)} / Chassis_Frame {len(CHASSIS_MESHES)} "
          f"/ Glass_Static {len(GLASS_MESHES)} / Interior {len(INTERIOR_MESHES)}+SW / Fifth_Wheel (empty)")
    print(f"  Doors:  Door_FL / Door_FR with DoorShell + Window + Mirror subgroups")
    print(f"  Wheels: Steer_FL/FR ▸ Wheel_FL/FR, Wheel_RL/RR (axle pivots)")
    print(f"  Lights: Headlights ({HEADLIGHT_MESHES}) + {len(EMPTY_LIGHT_GROUPS)} empty placeholders")
    print(f"  Movables: {len(EMPTY_MOVABLE_GROUPS)} empty placeholders")
    print(f"  Meshes assigned: {len(assigned)} + SW group (5)")


if __name__ == "__main__":
    main()
