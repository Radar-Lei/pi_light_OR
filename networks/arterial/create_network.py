#!/usr/bin/env python3
"""Create a 5-intersection arterial corridor in SUMO format.

Generates:
  - arterial.nod.xml  (nodes)
  - arterial.edg.xml  (edges)
  - arterial.net.xml  (compiled network)
  - arterial.rou.xml  (routes + vehicle demand)
  - arterial.add.xml  (TLS programs for all intersections)
  - arterial.sumocfg  (SUMO configuration)

Network layout:
                N1    N2    N3    N4    N5
                |     |     |     |     |
  W_in --- C1 --- C2 --- C3 --- C4 --- C5 --- E_out
                |     |     |     |     |
                S1    S2    S3    S4    S5

  - 5 signalized intersections in a line (east-west arterial)
  - Spacing: 300m between intersections
  - Each intersection: 4-arm, 3 lanes per approach, 13.89 m/s (50 km/h)
  - Side streets: 300m long (north-south)
  - Demand: 800 veh/hr on arterial (E-W), 300 veh/hr on side streets (N-S)
  - Turn ratios: 70/15/15 (arterial), 60/20/20 (side streets)
  - 4-phase TLS with protected left turns at each intersection
"""
import subprocess
import os

NETWORK_DIR = os.path.dirname(os.path.abspath(__file__))

NUM_INTERSECTIONS = 5
SPACING = 300.0       # meters between intersections
SIDE_LENGTH = 300.0   # length of side street stubs
SPEED = 13.89         # m/s (50 km/h)
NUM_LANES = 3


def write_nodes():
    """Generate node definitions for the arterial corridor."""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<nodes>"]

    # Intersection nodes (C1..C5) along x-axis
    for i in range(1, NUM_INTERSECTIONS + 1):
        x = (i - 1) * SPACING
        lines.append(f'    <node id="C{i}" x="{x:.1f}" y="0" type="traffic_light"/>')

    # Boundary nodes: west and east endpoints of the arterial
    lines.append(f'    <node id="W_in" x="{-SIDE_LENGTH:.1f}" y="0"/>')
    lines.append(
        f'    <node id="E_out" x="{(NUM_INTERSECTIONS - 1) * SPACING + SIDE_LENGTH:.1f}" y="0"/>'
    )

    # Side-street boundary nodes (north and south for each intersection)
    for i in range(1, NUM_INTERSECTIONS + 1):
        x = (i - 1) * SPACING
        lines.append(f'    <node id="N{i}" x="{x:.1f}" y="{SIDE_LENGTH:.1f}"/>')
        lines.append(f'    <node id="S{i}" x="{x:.1f}" y="{-SIDE_LENGTH:.1f}"/>')

    lines.append("</nodes>")

    path = os.path.join(NETWORK_DIR, "arterial.nod.xml")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


def write_edges():
    """Generate edge definitions for the arterial corridor."""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<edges>"]

    attrs = f'numLanes="{NUM_LANES}" speed="{SPEED}"'

    # --- Arterial links (east-west) ---
    lines.append("    <!-- Arterial: westbound boundary to C1 -->")
    lines.append(f'    <edge id="W_in2C1" from="W_in" to="C1" {attrs}/>')
    lines.append(f'    <edge id="C12W_in" from="C1" to="W_in" {attrs}/>')

    # Inter-intersection links
    for i in range(1, NUM_INTERSECTIONS):
        j = i + 1
        lines.append(f"    <!-- Arterial segment C{i} <-> C{j} -->")
        lines.append(f'    <edge id="C{i}2C{j}" from="C{i}" to="C{j}" {attrs}/>')
        lines.append(f'    <edge id="C{j}2C{i}" from="C{j}" to="C{i}" {attrs}/>')

    lines.append("    <!-- Arterial: C5 to eastbound boundary -->")
    lines.append(f'    <edge id="C52E_out" from="C5" to="E_out" {attrs}/>')
    lines.append(f'    <edge id="E_out2C5" from="E_out" to="C5" {attrs}/>')

    # --- Side streets (north-south) ---
    for i in range(1, NUM_INTERSECTIONS + 1):
        lines.append(f"    <!-- Side streets at C{i} -->")
        lines.append(f'    <edge id="N{i}2C{i}" from="N{i}" to="C{i}" {attrs}/>')
        lines.append(f'    <edge id="C{i}2N{i}" from="C{i}" to="N{i}" {attrs}/>')
        lines.append(f'    <edge id="S{i}2C{i}" from="S{i}" to="C{i}" {attrs}/>')
        lines.append(f'    <edge id="C{i}2S{i}" from="C{i}" to="S{i}" {attrs}/>')

    lines.append("</edges>")

    path = os.path.join(NETWORK_DIR, "arterial.edg.xml")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


def _get_outgoing_edges(intersection_idx):
    """Return list of outgoing edge IDs from intersection C{intersection_idx}."""
    i = intersection_idx
    edges = []
    # West
    if i == 1:
        edges.append("C12W_in")
    else:
        edges.append(f"C{i}2C{i-1}")
    # East
    if i == NUM_INTERSECTIONS:
        edges.append(f"C{i}2E_out")
    else:
        edges.append(f"C{i}2C{i+1}")
    # North
    edges.append(f"C{i}2N{i}")
    # South
    edges.append(f"C{i}2S{i}")
    return edges


def _get_incoming_edges(intersection_idx):
    """Return dict of incoming edge IDs grouped by approach direction."""
    i = intersection_idx
    incoming = {}
    # From west
    if i == 1:
        incoming["W"] = "W_in2C1"
    else:
        incoming["W"] = f"C{i-1}2C{i}"
    # From east
    if i == NUM_INTERSECTIONS:
        incoming["E"] = f"E_out2C{i}"
    else:
        incoming["E"] = f"C{i+1}2C{i}"
    # From north
    incoming["N"] = f"N{i}2C{i}"
    # From south
    incoming["S"] = f"S{i}2C{i}"
    return incoming


def _turn_targets(approach_dir, intersection_idx):
    """Return (through_edge, left_edge, right_edge) for a given approach direction.

    Convention (SUMO right-hand traffic):
      Approach from W: through=E, left=S, right=N
      Approach from E: through=W, left=N, right=S
      Approach from N: through=S, left=W, right=E
      Approach from S: through=N, left=E, right=W
    """
    i = intersection_idx
    out = _get_outgoing_edges(i)  # [W, E, N, S] order

    # Map direction to outgoing edge
    dir_to_edge = {}
    if i == 1:
        dir_to_edge["W"] = "C12W_in"
    else:
        dir_to_edge["W"] = f"C{i}2C{i-1}"
    if i == NUM_INTERSECTIONS:
        dir_to_edge["E"] = f"C{i}2E_out"
    else:
        dir_to_edge["E"] = f"C{i}2C{i+1}"
    dir_to_edge["N"] = f"C{i}2N{i}"
    dir_to_edge["S"] = f"C{i}2S{i}"

    turn_map = {
        "W": ("E", "S", "N"),  # from west: through=east, left=south, right=north
        "E": ("W", "N", "S"),
        "N": ("S", "W", "E"),  # from north: through=south, left=west, right=east
        "S": ("N", "E", "W"),
    }

    through_dir, left_dir, right_dir = turn_map[approach_dir]
    return dir_to_edge[through_dir], dir_to_edge[left_dir], dir_to_edge[right_dir]


def write_routes(arterial_demand=800, side_demand=300):
    """Generate demand with differentiated turn ratios.

    Args:
        arterial_demand: veh/hr per arterial approach (E-W directions)
        side_demand: veh/hr per side-street approach (N-S directions)
    """
    # Turn ratios
    arterial_ratios = {"through": 0.70, "left": 0.15, "right": 0.15}
    side_ratios = {"through": 0.60, "left": 0.20, "right": 0.20}

    routes = []
    flows = []
    flow_id = 0

    for i in range(1, NUM_INTERSECTIONS + 1):
        incoming = _get_incoming_edges(i)

        for approach_dir, in_edge in incoming.items():
            # Determine if arterial or side street
            is_arterial = approach_dir in ("W", "E")
            demand = arterial_demand if is_arterial else side_demand
            ratios = arterial_ratios if is_arterial else side_ratios
            period_base = 3600.0 / demand

            through_edge, left_edge, right_edge = _turn_targets(approach_dir, i)

            for turn_type, out_edge in [
                ("through", through_edge),
                ("left", left_edge),
                ("right", right_edge),
            ]:
                route_name = f"r_{in_edge}__{out_edge}"
                # Avoid duplicate routes (same edge pair from different intersections
                # won't happen because edge IDs are unique)
                route_edges = f"{in_edge} {out_edge}"
                routes.append(f'    <route id="{route_name}" edges="{route_edges}"/>')

                flow_period = period_base / ratios[turn_type]
                flows.append(
                    f'    <flow id="f_{flow_id}" route="{route_name}" '
                    f'begin="0" end="3600" period="{flow_period:.2f}" '
                    f'departSpeed="max" departLane="best"/>'
                )
                flow_id += 1

    content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<routes>\n"
        '    <vType id="car" length="5" minGap="2.5" maxSpeed="13.89" '
        'accel="2.6" decel="4.5"/>\n\n'
        + "\n".join(routes)
        + "\n\n"
        + "\n".join(flows)
        + "\n</routes>\n"
    )

    path = os.path.join(NETWORK_DIR, "arterial.rou.xml")
    with open(path, "w") as f:
        f.write(content)
    return path


def write_tls_additional():
    """Define 4-phase TLS programs for all 5 intersections.

    Phase structure (same for each intersection):
      Phase 0: EW through + right (green)
      Phase 1: EW yellow
      Phase 2: EW left (protected green)
      Phase 3: EW left yellow
      Phase 4: NS through + right (green)
      Phase 5: NS yellow
      Phase 6: NS left (protected green)
      Phase 7: NS left yellow

    Phase state encoding per intersection depends on SUMO's connection
    ordering. We use netconvert's --tls.guess to auto-generate TLS, then
    override with our program via the additional file. The state string
    length depends on the number of connections at each intersection.

    Since netconvert with --tls.guess will create its own phase encoding,
    we let it handle the state strings and just define timing via the
    additional file. The actual state strings will be set by TraCI at
    runtime. Here we provide a reasonable default for standalone runs.
    """
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<additional>"]

    for i in range(1, NUM_INTERSECTIONS + 1):
        # With 4 approaches x 3 lanes = 12 incoming lanes, each can connect
        # to ~3 outgoing edges. netconvert determines exact connection count.
        # We use a generic program that TraCI will override at runtime.
        # For standalone fixed-time operation, netconvert's auto-generated
        # program is sufficient. We define offset for green wave coordination.
        offset = (i - 1) * 8  # simple offset for arterial progression
        lines.append(f"    <!-- TLS program for intersection C{i} -->")
        lines.append(
            f'    <tlLogic id="C{i}" type="static" programID="coordinated" offset="{offset}">'
        )
        # We cannot predict the exact state string length until netconvert
        # runs, so we rely on netconvert's auto-generated program for the
        # default. This additional file provides coordinated timing.
        # The state strings below assume the standard connection ordering
        # that netconvert produces for a 4-arm 3-lane intersection.
        # netconvert typically creates ~12 connections per approach pair.
        # We'll generate proper states after inspecting netconvert output.
        lines.append(
            '        <!-- EW through+right green (arterial priority) -->'
        )
        lines.append(
            '        <phase duration="35" state="GGGgrrrrGGGgrrrr" minDur="15" maxDur="50"/>'
        )
        lines.append('        <!-- EW yellow -->')
        lines.append(
            '        <phase duration="3"  state="yyyyrrrryyyyrrrr"/>'
        )
        lines.append('        <!-- EW left protected green -->')
        lines.append(
            '        <phase duration="15" state="rrrrGGggrrrrGGgg" minDur="8" maxDur="25"/>'
        )
        lines.append('        <!-- EW left yellow -->')
        lines.append(
            '        <phase duration="3"  state="rrrryyyyrrrryyyy"/>'
        )
        lines.append('        <!-- NS through+right green -->')
        lines.append(
            '        <phase duration="25" state="GGGgrrrrGGGgrrrr" minDur="10" maxDur="40"/>'
        )
        lines.append('        <!-- NS yellow -->')
        lines.append(
            '        <phase duration="3"  state="yyyyrrrryyyyrrrr"/>'
        )
        lines.append('        <!-- NS left protected green -->')
        lines.append(
            '        <phase duration="12" state="rrrrGGggrrrrGGgg" minDur="8" maxDur="20"/>'
        )
        lines.append('        <!-- NS left yellow -->')
        lines.append(
            '        <phase duration="3"  state="yyyyrrrryyyyrrrr"/>'
        )
        lines.append("    </tlLogic>")

    lines.append("</additional>")

    path = os.path.join(NETWORK_DIR, "arterial.add.xml")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
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
    path = os.path.join(NETWORK_DIR, "arterial.sumocfg")
    with open(path, "w") as f:
        f.write(content)
    return path


def build_network(nod_file, edg_file):
    """Run netconvert to compile the network."""
    net_file = os.path.join(NETWORK_DIR, "arterial.net.xml")
    cmd = [
        "netconvert",
        "--node-files", nod_file,
        "--edge-files", edg_file,
        "--output-file", net_file,
        "--no-turnarounds", "true",
        "--tls.guess", "true",
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    if result.stderr:
        print(f"netconvert warnings:\n{result.stderr}")
    return net_file


def fix_tls_additional(net_file):
    """Read the compiled network to determine correct TLS state string lengths,
    then rewrite the additional file with properly sized state strings.

    This two-pass approach ensures the phase states match netconvert's
    actual connection layout.
    """
    import xml.etree.ElementTree as ET

    tree = ET.parse(net_file)
    root = tree.getroot()

    # Extract connection count per TLS (= state string length)
    tls_state_len = {}
    for tl in root.findall(".//tlLogic"):
        tl_id = tl.get("id")
        phases = tl.findall("phase")
        if phases:
            tls_state_len[tl_id] = len(phases[0].get("state", ""))

    # Also extract netconvert's auto-generated phases as reference
    tls_phases = {}
    for tl in root.findall(".//tlLogic"):
        tl_id = tl.get("id")
        phases = []
        for p in tl.findall("phase"):
            phases.append({
                "duration": p.get("duration"),
                "state": p.get("state"),
            })
        tls_phases[tl_id] = phases

    # Rewrite additional file using netconvert's state strings but our timing
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<additional>"]

    for i in range(1, NUM_INTERSECTIONS + 1):
        tl_id = f"C{i}"
        if tl_id not in tls_phases:
            print(f"Warning: TLS {tl_id} not found in network, skipping")
            continue

        ref_phases = tls_phases[tl_id]
        n_phases = len(ref_phases)
        offset = (i - 1) * 8  # green wave offset

        lines.append(f"    <!-- TLS program for intersection C{i} "
                     f"({n_phases} phases, state length {tls_state_len.get(tl_id, '?')}) -->")
        lines.append(
            f'    <tlLogic id="{tl_id}" type="static" '
            f'programID="coordinated" offset="{offset}">'
        )

        # Use netconvert's phase structure with adjusted durations
        # Give arterial (EW) phases more green time
        for j, phase in enumerate(ref_phases):
            state = phase["state"]
            # Count green signals to determine if this is a major or minor phase
            green_count = state.count("G") + state.count("g")
            yellow_count = state.count("y")

            if yellow_count > 0:
                dur = 3
                min_dur = max_dur = None
            elif green_count > len(state) * 0.3:
                # Major green phase - longer duration
                dur = 30
                min_dur, max_dur = 10, 45
            else:
                # Minor green phase (left turns)
                dur = 15
                min_dur, max_dur = 8, 25

            phase_str = f'        <phase duration="{dur}" state="{state}"'
            if min_dur is not None:
                phase_str += f' minDur="{min_dur}" maxDur="{max_dur}"'
            phase_str += "/>"
            lines.append(phase_str)

        lines.append("    </tlLogic>")

    lines.append("</additional>")

    path = os.path.join(NETWORK_DIR, "arterial.add.xml")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


if __name__ == "__main__":
    print("=" * 60)
    print("Creating 5-intersection arterial network")
    print("=" * 60)

    # Step 1: Write node and edge definitions
    nod = write_nodes()
    edg = write_edges()
    print(f"  Nodes: {nod}")
    print(f"  Edges: {edg}")

    # Step 2: Compile network with netconvert
    net = build_network(nod, edg)
    print(f"  Network: {net}")

    # Step 3: Fix TLS additional file using actual network connection layout
    add = fix_tls_additional(net)
    print(f"  TLS additional: {add}")

    # Step 4: Write route demand
    rou = write_routes(arterial_demand=800, side_demand=300)
    print(f"  Routes: {rou}")

    # Step 5: Write SUMO configuration
    cfg = write_sumo_config(net, rou)
    print(f"  Config: {cfg}")

    print("=" * 60)
    print(f"Arterial network created at: {NETWORK_DIR}")
    print(f"  5 intersections (C1-C5), 300m spacing")
    print(f"  Arterial demand: 800 veh/hr, Side-street demand: 300 veh/hr")
    print(f"  Run with: sumo -c {cfg}")
    print("=" * 60)
