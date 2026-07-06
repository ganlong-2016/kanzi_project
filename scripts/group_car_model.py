#!/usr/bin/env python3
"""Group car prefab meshes into Wheels / Doors / Body hierarchy."""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

CAR_KZPROJ = Path("/workspace/IVI/car/Car.kzproj")

# Wheel mesh assignment (from scania4.glb spatial analysis)
WHEEL_GROUPS: dict[str, list[str]] = {
    "Wheel_FL": [
        "Circle.028",
        "Circle.032",
        "Circle.033",
        "Circle.037",
        "Cube.014",
        "Plane.007",
    ],
    "Wheel_FR": [
        "Circle.011",
        "Circle.016",
        "Circle.020",
        "Cube.012",
        "Plane.008",
    ],
    "Wheel_RL": [
        "Circle.001",
        "Circle.004",
        "Circle.006",
        "Circle.010",
        "Cube.005",
        "Cube.008",
    ],
    "Wheel_RR": [
        "Cube.006",
        "Cube.007",
        "Cube.010",
        "Cube.016",
        "Cube.020",
        "Cube.021",
    ],
}

DOOR_GROUPS = ["Door_FL", "Door_FR", "Door_RL", "Door_RR"]

# Pivot positions for door empty nodes (hinge approximations, meters)
DOOR_PIVOTS = {
    "Door_FL": (-1.15, 1.2, 1.2),
    "Door_FR": (1.15, 1.2, 1.2),
    "Door_RL": (-1.15, 1.2, 0.2),
    "Door_RR": (1.15, 1.2, 0.2),
}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def parse_project_items(lines: list[str], children_start: int) -> list[dict]:
    items: list[dict] = []
    i = children_start + 1
    while i < len(lines):
        if lines[i].strip() == "</children>":
            break
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
                                "start": start,
                                "end": j,
                                "block": block,
                                "name": sn.group(1) if sn else "?",
                                "type": typ.group(1) if typ else "?",
                            }
                        )
                        i = j
                        break
                j += 1
        i += 1
    return items


def make_empty_node(name: str, children_xml: str, with_xmlns: bool = False) -> str:
    xmlns = (
        ' xmlns:d7p1="http://schemas.datacontract.org/2004/07/Rightware.Kanzi.Tool.Logic.Project.SceneGraphItems"'
        if with_xmlns
        else ""
    )
    ts = now_iso()
    pivot = DOOR_PIVOTS.get(name)
    transform_xml = ""
    if pivot:
        tx, ty, tz = pivot
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

    return f"""                <ProjectItem{xmlns}
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
                  <children>
{children_xml}                  </children>
                  <dataSource
                    i:nil="true" />
                  <isHidden>false</isHidden>
                  <isReadOnly>false</isReadOnly>
                </ProjectItem>
"""


def main() -> None:
    lines = CAR_KZPROJ.read_text(encoding="utf-8").splitlines(keepends=True)

    found = 0
    inner_car_line = None
    for i, line in enumerate(lines):
        if "<SerializedName>car</SerializedName>" in line and i > 90170:
            found += 1
            if found == 2:
                inner_car_line = i
                break
    if inner_car_line is None:
        raise RuntimeError("Inner car EmptyNode not found")

    children_start = None
    for j in range(inner_car_line, inner_car_line + 10):
        if "<children>" in lines[j]:
            children_start = j
            break
    if children_start is None:
        raise RuntimeError("car children block not found")

    children_end = None
    for j in range(children_start + 1, len(lines)):
        if lines[j].strip() == "</children>":
            children_end = j
            break
    if children_end is None:
        raise RuntimeError("car children end not found")

    items = parse_project_items(lines, children_start)
    mesh_by_name = {c["name"]: c["block"] for c in items if c["type"] == "MeshNode"}
    static_items = [c["block"] for c in items if c["type"] != "MeshNode"]

    assigned: set[str] = set()
    wheel_blocks: list[str] = []
    for group_name, members in WHEEL_GROUPS.items():
        group_children = ""
        for member in members:
            if member not in mesh_by_name:
                print(f"WARNING: wheel mesh {member} not found in car prefab")
                continue
            group_children += mesh_by_name[member]
            assigned.add(member)
        wheel_blocks.append(make_empty_node(group_name, group_children))

    wheels_xml = "".join(wheel_blocks)
    wheels_group = make_empty_node("Wheels", wheels_xml, with_xmlns=True)

    door_blocks: list[str] = []
    for door_name in DOOR_GROUPS:
        door_blocks.append(make_empty_node(door_name, "", with_xmlns=False))
    doors_xml = "".join(door_blocks)
    doors_group = make_empty_node("Doors", doors_xml, with_xmlns=True)

    body_children = ""
    for name, block in sorted(mesh_by_name.items()):
        if name not in assigned:
            body_children += block
    body_group = make_empty_node("Body", body_children, with_xmlns=True)

    new_children = "".join(static_items) + body_group + wheels_group + doors_group

    new_lines = (
        lines[: children_start + 1]
        + [new_children]
        + lines[children_end:]
    )
    CAR_KZPROJ.write_text("".join(new_lines), encoding="utf-8")

    print("Car prefab regrouped:")
    print(f"  Wheels: {sum(len(v) for v in WHEEL_GROUPS.values())} meshes in 4 groups")
    print(f"  Body: {len(mesh_by_name) - len(assigned)} meshes")
    print(f"  Doors: 4 empty pivot groups (no separate door meshes in GLB)")
    missing = [m for group in WHEEL_GROUPS.values() for m in group if m not in mesh_by_name]
    if missing:
        print(f"  Missing meshes: {missing}")


if __name__ == "__main__":
    main()
