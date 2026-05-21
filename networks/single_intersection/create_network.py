#!/usr/bin/env python3
"""Create a standard 4-arm signalized intersection in SUMO format.

Generates:
  - single_intersection.nod.xml  (nodes)
  - single_intersection.edg.xml  (edges)
  - single_intersection.con.xml  (connections - optional)
  - single_intersection.net.xml  (compiled network)
  - single_intersection.rou.xml  (routes + vehicle demand)
  - single_intersection.sumocfg  (SUMO configuration)
  - single_intersection.add.xml  (additional file for TLS program)

Network layout:
    N
    |
  W-C-E    (C = center intersection with traffic light)
    |
    S

Each approach: 3 lanes, 300m long, speed limit 13.89 m/s (50 km/h).
Phases: 4-phase with protected left turns.
"""
import subprocess
import os

NETWORK_DIR = os.path.dirname(os.path.abspath(__file__))


def write_nodes():
    content = """<?xml version="1.0" encoding="UTF-8"?>
<nodes>
    <node id="C" x="0" y="0" type="traffic_light"/>
    <node id="N" x="0" y="300"/>
    <node id="S" x="0" y="-300"/>
    <node id="E" x="300" y="0"/>
    <node id="W" x="-300" y="0"/>
</nodes>"""
    path = os.path.join(NETWORK_DIR, "single_intersection.nod.xml")
    with open(path, "w") as f:
        f.write(content)
    return path


def write_edges():
    content = """<?xml version="1.0" encoding="UTF-8"?>
<edges>
    <!-- Incoming edges (toward center) -->
    <edge id="N2C" from="N" to="C" numLanes="3" speed="13.89"/>
    <edge id="S2C" from="S" to="C" numLanes="3" speed="13.89"/>
    <edge id="E2C" from="E" to="C" numLanes="3" speed="13.89"/>
    <edge id="W2C" from="W" to="C" numLanes="3" speed="13.89"/>
    <!-- Outgoing edges (from center) -->
    <edge id="C2N" from="C" to="N" numLanes="3" speed="13.89"/>
    <edge id="C2S" from="C" to="S" numLanes="3" speed="13.89"/>
    <edge id="C2E" from="C" to="E" numLanes="3" speed="13.89"/>
    <edge id="C2W" from="C" to="W" numLanes="3" speed="13.89"/>
</edges>"""
    path = os.path.join(NETWORK_DIR, "single_intersection.edg.xml")
    with open(path, "w") as f:
        f.write(content)
    return path


def write_routes(demand_level=600):
    """Generate balanced demand: `demand_level` veh/hr per approach."""
    vph = demand_level  # vehicles per hour per approach
    period = 3600.0 / vph  # seconds between departures

    routes = []
    flows = []
    route_id = 0
    flow_id = 0

    directions = [
        ("N2C", "C2S", "through"),
        ("N2C", "C2E", "left"),
        ("N2C", "C2W", "right"),
        ("S2C", "C2N", "through"),
        ("S2C", "C2W", "left"),
        ("S2C", "C2E", "right"),
        ("E2C", "C2W", "through"),
        ("E2C", "C2S", "left"),
        ("E2C", "C2N", "right"),
        ("W2C", "C2E", "through"),
        ("W2C", "C2N", "left"),
        ("W2C", "C2S", "right"),
    ]

    # Turn ratios: 60% through, 20% left, 20% right
    turn_ratios = {"through": 0.6, "left": 0.2, "right": 0.2}

    for from_edge, to_edge, turn_type in directions:
        route_name = f"route_{from_edge}_{to_edge}"
        routes.append(f'    <route id="{route_name}" edges="{from_edge} {to_edge}"/>')

        flow_period = period / turn_ratios[turn_type]
        flows.append(
            f'    <flow id="f_{flow_id}" route="{route_name}" '
            f'begin="0" end="3600" period="{flow_period:.2f}" '
            f'departSpeed="max" departLane="best"/>'
        )
        flow_id += 1

    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="car" length="5" minGap="2.5" maxSpeed="13.89" accel="2.6" decel="4.5"/>

{chr(10).join(routes)}

{chr(10).join(flows)}
</routes>"""
    path = os.path.join(NETWORK_DIR, "single_intersection.rou.xml")
    with open(path, "w") as f:
        f.write(content)
    return path


def write_tls_additional():
    """Define a 4-phase TLS program with min-green and yellow."""
    # Phase encoding for 4-arm, 3-lane intersection:
    # SUMO auto-generates connections; we define a simple program
    content = """<?xml version="1.0" encoding="UTF-8"?>
<additional>
    <!-- Default fixed-time program (will be overridden by TraCI) -->
    <tlLogic id="C" type="static" programID="default" offset="0">
        <!-- NS through+right green -->
        <phase duration="30" state="GGgrrrGGgrrr" minDur="10" maxDur="45"/>
        <!-- NS yellow -->
        <phase duration="3"  state="yyyrrryyyrrr"/>
        <!-- NS left green -->
        <phase duration="15" state="rrrGGgrrrGGg" minDur="8" maxDur="25"/>
        <!-- NS left yellow -->
        <phase duration="3"  state="rrryyyrrryyy"/>
        <!-- EW through+right green -->
        <phase duration="30" state="rrrGGgrrrGGg" minDur="10" maxDur="45"/>
        <!-- EW yellow -->
        <phase duration="3"  state="rrryyyrrryyy"/>
        <!-- EW left green -->
        <phase duration="15" state="GGgrrrGGgrrr" minDur="8" maxDur="25"/>
        <!-- EW left yellow -->
        <phase duration="3"  state="yyyrrryyyrrr"/>
    </tlLogic>
</additional>"""
    path = os.path.join(NETWORK_DIR, "single_intersection.add.xml")
    with open(path, "w") as f:
        f.write(content)
    return path


def write_sumo_config(net_file, route_file):
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <input>
        <net-file value="{os.path.basename(net_file)}"/>
        <route-files value="{os.path.basename(route_file)}"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="3600"/>
        <step-length value="1.0"/>
    </time>
    <processing>
        <time-to-teleport value="-1"/>
    </processing>
    <report>
        <no-step-log value="true"/>
    </report>
</configuration>"""
    path = os.path.join(NETWORK_DIR, "single_intersection.sumocfg")
    with open(path, "w") as f:
        f.write(content)
    return path


def build_network(nod_file, edg_file):
    net_file = os.path.join(NETWORK_DIR, "single_intersection.net.xml")
    cmd = [
        "netconvert",
        "--node-files", nod_file,
        "--edge-files", edg_file,
        "--output-file", net_file,
        "--no-turnarounds", "true",
        "--tls.guess", "true",
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return net_file


if __name__ == "__main__":
    nod = write_nodes()
    edg = write_edges()
    net = build_network(nod, edg)
    rou = write_routes(demand_level=600)
    write_tls_additional()
    cfg = write_sumo_config(net, rou)
    print(f"Network created at: {NETWORK_DIR}")
    print(f"  Net file: {net}")
    print(f"  Route file: {rou}")
    print(f"  Config: {cfg}")
