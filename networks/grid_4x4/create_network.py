#!/usr/bin/env python3
"""Create a 4x4 grid signalized network in SUMO format.

Generates:
  - grid_4x4.nod.xml  (nodes)
  - grid_4x4.edg.xml  (edges)
  - grid_4x4.net.xml  (compiled network via netconvert)
  - grid_4x4.rou.xml  (routes + vehicle demand)
  - grid_4x4.add.xml  (TLS programs for all 16 intersections)
  - grid_4x4.sumocfg  (SUMO configuration)

Network layout (4x4 grid with boundary nodes):

    b_N0  b_N1  b_N2  b_N3
      |     |     |     |
  b_W0--n_0_0--n_0_1--n_0_2--n_0_3--b_E0
      |     |     |     |
  b_W1--n_1_0--n_1_1--n_1_2--n_1_3--b_E1
      |     |     |     |
  b_W2--n_2_0--n_2_1--n_2_2--n_2_3--b_E2
      |     |     |     |
  b_W3--n_3_0--n_3_1--n_3_2--n_3_3--b_E3
      |     |     |     |
    b_S0  b_S1  b_S2  b_S3

Internal links: 100m (SHORT -- critical for spillback in Claim 4).
Boundary links: 200m (buffer for vehicle generation).
Each approach: 2 lanes, speed limit 13.89 m/s (50 km/h).
TLS: Simple 2-phase (NS green / EW green) at each of the 16 intersections.
"""
import subprocess
import os

NETWORK_DIR = os.path.dirname(os.path.abspath(__file__))
GRID_SIZE = 4
INTERNAL_LENGTH = 100  # meters between intersections (short for spillback)
BOUNDARY_LENGTH = 200  # meters for boundary approach links
NUM_LANES = 2
SPEED = 13.89  # m/s = 50 km/h


def intersection_id(r, c):
    """Internal intersection node ID."""
    return f"n_{r}_{c}"


def boundary_id(side, idx):
    """Boundary node ID. side in {N, S, E, W}."""
    return f"b_{side}{idx}"


def write_nodes():
    """Generate node definitions for the 4x4 grid + boundary nodes."""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<nodes>"]

    # Internal intersection nodes (traffic lights)
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            x = c * INTERNAL_LENGTH
            y = (GRID_SIZE - 1 - r) * INTERNAL_LENGTH  # row 0 at top
            nid = intersection_id(r, c)
            lines.append(
                f'    <node id="{nid}" x="{x}" y="{y}" type="traffic_light"/>'
            )

    # Boundary nodes (North)
    for c in range(GRID_SIZE):
        x = c * INTERNAL_LENGTH
        y = (GRID_SIZE - 1) * INTERNAL_LENGTH + BOUNDARY_LENGTH
        lines.append(f'    <node id="{boundary_id("N", c)}" x="{x}" y="{y}"/>')

    # Boundary nodes (South)
    for c in range(GRID_SIZE):
        x = c * INTERNAL_LENGTH
        y = -BOUNDARY_LENGTH
        lines.append(f'    <node id="{boundary_id("S", c)}" x="{x}" y="{y}"/>')

    # Boundary nodes (West)
    for r in range(GRID_SIZE):
        x = -BOUNDARY_LENGTH
        y = (GRID_SIZE - 1 - r) * INTERNAL_LENGTH
        lines.append(f'    <node id="{boundary_id("W", r)}" x="{x}" y="{y}"/>')

    # Boundary nodes (East)
    for r in range(GRID_SIZE):
        x = (GRID_SIZE - 1) * INTERNAL_LENGTH + BOUNDARY_LENGTH
        y = (GRID_SIZE - 1 - r) * INTERNAL_LENGTH
        lines.append(f'    <node id="{boundary_id("E", r)}" x="{x}" y="{y}"/>')

    lines.append("</nodes>")
    content = "\n".join(lines)
    path = os.path.join(NETWORK_DIR, "grid_4x4.nod.xml")
    with open(path, "w") as f:
        f.write(content)
    return path


def write_edges():
    """Generate edge definitions: internal grid + boundary connections."""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<edges>"]
    attrs = f'numLanes="{NUM_LANES}" speed="{SPEED}"'

    lines.append("    <!-- Internal horizontal edges (East-West) -->")
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE - 1):
            n1 = intersection_id(r, c)
            n2 = intersection_id(r, c + 1)
            # Eastbound
            lines.append(f'    <edge id="{n1}_to_{n2}" from="{n1}" to="{n2}" {attrs}/>')
            # Westbound
            lines.append(f'    <edge id="{n2}_to_{n1}" from="{n2}" to="{n1}" {attrs}/>')

    lines.append("    <!-- Internal vertical edges (North-South) -->")
    for r in range(GRID_SIZE - 1):
        for c in range(GRID_SIZE):
            n1 = intersection_id(r, c)
            n2 = intersection_id(r + 1, c)
            # Southbound (r increases = south in our layout)
            lines.append(f'    <edge id="{n1}_to_{n2}" from="{n1}" to="{n2}" {attrs}/>')
            # Northbound
            lines.append(f'    <edge id="{n2}_to_{n1}" from="{n2}" to="{n1}" {attrs}/>')

    lines.append("    <!-- Boundary edges (North) -->")
    for c in range(GRID_SIZE):
        bn = boundary_id("N", c)
        ni = intersection_id(0, c)
        lines.append(f'    <edge id="{bn}_to_{ni}" from="{bn}" to="{ni}" {attrs}/>')
        lines.append(f'    <edge id="{ni}_to_{bn}" from="{ni}" to="{bn}" {attrs}/>')

    lines.append("    <!-- Boundary edges (South) -->")
    for c in range(GRID_SIZE):
        bs = boundary_id("S", c)
        ni = intersection_id(GRID_SIZE - 1, c)
        lines.append(f'    <edge id="{bs}_to_{ni}" from="{bs}" to="{ni}" {attrs}/>')
        lines.append(f'    <edge id="{ni}_to_{bs}" from="{ni}" to="{bs}" {attrs}/>')

    lines.append("    <!-- Boundary edges (West) -->")
    for r in range(GRID_SIZE):
        bw = boundary_id("W", r)
        ni = intersection_id(r, 0)
        lines.append(f'    <edge id="{bw}_to_{ni}" from="{bw}" to="{ni}" {attrs}/>')
        lines.append(f'    <edge id="{ni}_to_{bw}" from="{ni}" to="{bw}" {attrs}/>')

    lines.append("    <!-- Boundary edges (East) -->")
    for r in range(GRID_SIZE):
        be = boundary_id("E", r)
        ni = intersection_id(r, GRID_SIZE - 1)
        lines.append(f'    <edge id="{be}_to_{ni}" from="{be}" to="{ni}" {attrs}/>')
        lines.append(f'    <edge id="{ni}_to_{be}" from="{ni}" to="{be}" {attrs}/>')

    lines.append("</edges>")
    content = "\n".join(lines)
    path = os.path.join(NETWORK_DIR, "grid_4x4.edg.xml")
    with open(path, "w") as f:
        f.write(content)
    return path


def _get_neighbor_edges(r, c):
    """Return (incoming_edges, outgoing_edges) for intersection (r, c).

    Each entry is (edge_id, direction) where direction is N/S/E/W
    indicating which side the edge connects to.
    """
    nid = intersection_id(r, c)
    incoming = []
    outgoing = []

    # North neighbor (row r-1) or boundary
    if r > 0:
        nb = intersection_id(r - 1, c)
    else:
        nb = boundary_id("N", c)
    incoming.append((f"{nb}_to_{nid}", "N"))
    outgoing.append((f"{nid}_to_{nb}", "N"))

    # South neighbor (row r+1) or boundary
    if r < GRID_SIZE - 1:
        nb = intersection_id(r + 1, c)
    else:
        nb = boundary_id("S", c)
    incoming.append((f"{nb}_to_{nid}", "S"))
    outgoing.append((f"{nid}_to_{nb}", "S"))

    # West neighbor (col c-1) or boundary
    if c > 0:
        nb = intersection_id(r, c - 1)
    else:
        nb = boundary_id("W", r)
    incoming.append((f"{nb}_to_{nid}", "W"))
    outgoing.append((f"{nid}_to_{nb}", "W"))

    # East neighbor (col c+1) or boundary
    if c < GRID_SIZE - 1:
        nb = intersection_id(r, c + 1)
    else:
        nb = boundary_id("E", r)
    incoming.append((f"{nb}_to_{nid}", "E"))
    outgoing.append((f"{nid}_to_{nb}", "E"))

    return incoming, outgoing


# Maps (from_dir, to_dir) -> turn type
# "from_dir" = which side the vehicle comes FROM
# Through = continues straight, left/right relative to travel direction
_TURN_MAP = {
    # From North (traveling south): through=S, left=E, right=W
    ("N", "S"): "through", ("N", "E"): "left", ("N", "W"): "right",
    # From South (traveling north): through=N, left=W, right=E
    ("S", "N"): "through", ("S", "W"): "left", ("S", "E"): "right",
    # From West (traveling east): through=E, left=N, right=S
    ("W", "E"): "through", ("W", "N"): "left", ("W", "S"): "right",
    # From East (traveling west): through=W, left=S, right=N
    ("E", "W"): "through", ("E", "S"): "left", ("E", "N"): "right",
}


def write_routes(total_demand_per_edge=500):
    """Generate demand entering from each boundary edge.

    Args:
        total_demand_per_edge: total veh/hr entering from each boundary
            edge (N/S/E/W), distributed evenly across 4 entry points per edge.

    Turn ratios: 60% through, 20% left, 20% right at each intersection.
    Vehicles travel across the grid following shortest paths with
    probabilistic turning at each intersection. For simplicity, we define
    full routes from each boundary entry to each boundary exit.
    """
    turn_ratios = {"through": 0.6, "left": 0.2, "right": 0.2}

    # Demand per entry point per edge
    vph_per_entry = total_demand_per_edge / GRID_SIZE

    routes_xml = []
    flows_xml = []
    route_id = 0
    flow_id = 0

    # Generate routes: from each boundary entry, travel through the grid
    # For each boundary entry point, generate routes that go through/left/right
    # We use multi-hop routes through the grid

    # Strategy: For each entry point, create routes to all possible exit
    # boundary nodes. Weight by compound turn probabilities.
    # For simplicity and to keep routes manageable, generate straight-through
    # routes (dominant 60% each turn) and some turning routes.

    # Simpler approach: define entry->exit routes as straight lines through grid
    # plus some turning variants. This is standard for grid network experiments.

    # === North boundary entries (traveling southbound) ===
    for c in range(GRID_SIZE):
        entry_edge = f"{boundary_id('N', c)}_to_{intersection_id(0, c)}"

        # Through route: N -> S (straight south through entire grid)
        edges = [entry_edge]
        for r in range(GRID_SIZE - 1):
            edges.append(f"{intersection_id(r, c)}_to_{intersection_id(r + 1, c)}")
        edges.append(f"{intersection_id(GRID_SIZE - 1, c)}_to_{boundary_id('S', c)}")
        rname = f"route_{route_id}"
        routes_xml.append(f'    <route id="{rname}" edges="{" ".join(edges)}"/>')
        period = 3600.0 / (vph_per_entry * turn_ratios["through"])
        flows_xml.append(
            f'    <flow id="f_{flow_id}" route="{rname}" '
            f'begin="0" end="3600" period="{period:.2f}" '
            f'departSpeed="max" departLane="best"/>'
        )
        route_id += 1
        flow_id += 1

        # Left turn route: enter from N, turn left (east) at row 1, exit east
        if GRID_SIZE > 1:
            turn_row = 1
            edges_l = [entry_edge]
            for r in range(turn_row):
                edges_l.append(f"{intersection_id(r, c)}_to_{intersection_id(r + 1, c)}")
            # Turn east
            for cc in range(c, GRID_SIZE - 1):
                edges_l.append(
                    f"{intersection_id(turn_row, cc)}_to_{intersection_id(turn_row, cc + 1)}"
                )
            edges_l.append(
                f"{intersection_id(turn_row, GRID_SIZE - 1)}_to_{boundary_id('E', turn_row)}"
            )
            rname = f"route_{route_id}"
            routes_xml.append(f'    <route id="{rname}" edges="{" ".join(edges_l)}"/>')
            period = 3600.0 / (vph_per_entry * turn_ratios["left"])
            flows_xml.append(
                f'    <flow id="f_{flow_id}" route="{rname}" '
                f'begin="0" end="3600" period="{period:.2f}" '
                f'departSpeed="max" departLane="best"/>'
            )
            route_id += 1
            flow_id += 1

        # Right turn route: enter from N, turn right (west) at row 1, exit west
        if GRID_SIZE > 1:
            turn_row = 1
            edges_r = [entry_edge]
            for r in range(turn_row):
                edges_r.append(f"{intersection_id(r, c)}_to_{intersection_id(r + 1, c)}")
            # Turn west
            for cc in range(c, 0, -1):
                edges_r.append(
                    f"{intersection_id(turn_row, cc)}_to_{intersection_id(turn_row, cc - 1)}"
                )
            edges_r.append(
                f"{intersection_id(turn_row, 0)}_to_{boundary_id('W', turn_row)}"
            )
            rname = f"route_{route_id}"
            routes_xml.append(f'    <route id="{rname}" edges="{" ".join(edges_r)}"/>')
            period = 3600.0 / (vph_per_entry * turn_ratios["right"])
            flows_xml.append(
                f'    <flow id="f_{flow_id}" route="{rname}" '
                f'begin="0" end="3600" period="{period:.2f}" '
                f'departSpeed="max" departLane="best"/>'
            )
            route_id += 1
            flow_id += 1

    # === South boundary entries (traveling northbound) ===
    for c in range(GRID_SIZE):
        entry_edge = f"{boundary_id('S', c)}_to_{intersection_id(GRID_SIZE - 1, c)}"

        # Through: S -> N
        edges = [entry_edge]
        for r in range(GRID_SIZE - 1, 0, -1):
            edges.append(f"{intersection_id(r, c)}_to_{intersection_id(r - 1, c)}")
        edges.append(f"{intersection_id(0, c)}_to_{boundary_id('N', c)}")
        rname = f"route_{route_id}"
        routes_xml.append(f'    <route id="{rname}" edges="{" ".join(edges)}"/>')
        period = 3600.0 / (vph_per_entry * turn_ratios["through"])
        flows_xml.append(
            f'    <flow id="f_{flow_id}" route="{rname}" '
            f'begin="0" end="3600" period="{period:.2f}" '
            f'departSpeed="max" departLane="best"/>'
        )
        route_id += 1
        flow_id += 1

        # Left: S entry, turn left (west) at row 2
        turn_row = GRID_SIZE - 2
        edges_l = [entry_edge]
        for r in range(GRID_SIZE - 1, turn_row, -1):
            edges_l.append(f"{intersection_id(r, c)}_to_{intersection_id(r - 1, c)}")
        for cc in range(c, 0, -1):
            edges_l.append(
                f"{intersection_id(turn_row, cc)}_to_{intersection_id(turn_row, cc - 1)}"
            )
        edges_l.append(f"{intersection_id(turn_row, 0)}_to_{boundary_id('W', turn_row)}")
        rname = f"route_{route_id}"
        routes_xml.append(f'    <route id="{rname}" edges="{" ".join(edges_l)}"/>')
        period = 3600.0 / (vph_per_entry * turn_ratios["left"])
        flows_xml.append(
            f'    <flow id="f_{flow_id}" route="{rname}" '
            f'begin="0" end="3600" period="{period:.2f}" '
            f'departSpeed="max" departLane="best"/>'
        )
        route_id += 1
        flow_id += 1

        # Right: S entry, turn right (east) at row 2
        edges_r = [entry_edge]
        for r in range(GRID_SIZE - 1, turn_row, -1):
            edges_r.append(f"{intersection_id(r, c)}_to_{intersection_id(r - 1, c)}")
        for cc in range(c, GRID_SIZE - 1):
            edges_r.append(
                f"{intersection_id(turn_row, cc)}_to_{intersection_id(turn_row, cc + 1)}"
            )
        edges_r.append(
            f"{intersection_id(turn_row, GRID_SIZE - 1)}_to_{boundary_id('E', turn_row)}"
        )
        rname = f"route_{route_id}"
        routes_xml.append(f'    <route id="{rname}" edges="{" ".join(edges_r)}"/>')
        period = 3600.0 / (vph_per_entry * turn_ratios["right"])
        flows_xml.append(
            f'    <flow id="f_{flow_id}" route="{rname}" '
            f'begin="0" end="3600" period="{period:.2f}" '
            f'departSpeed="max" departLane="best"/>'
        )
        route_id += 1
        flow_id += 1

    # === West boundary entries (traveling eastbound) ===
    for r in range(GRID_SIZE):
        entry_edge = f"{boundary_id('W', r)}_to_{intersection_id(r, 0)}"

        # Through: W -> E
        edges = [entry_edge]
        for cc in range(GRID_SIZE - 1):
            edges.append(f"{intersection_id(r, cc)}_to_{intersection_id(r, cc + 1)}")
        edges.append(f"{intersection_id(r, GRID_SIZE - 1)}_to_{boundary_id('E', r)}")
        rname = f"route_{route_id}"
        routes_xml.append(f'    <route id="{rname}" edges="{" ".join(edges)}"/>')
        period = 3600.0 / (vph_per_entry * turn_ratios["through"])
        flows_xml.append(
            f'    <flow id="f_{flow_id}" route="{rname}" '
            f'begin="0" end="3600" period="{period:.2f}" '
            f'departSpeed="max" departLane="best"/>'
        )
        route_id += 1
        flow_id += 1

        # Left: W entry, turn left (north) at col 1
        turn_col = 1
        edges_l = [entry_edge]
        for cc in range(turn_col):
            edges_l.append(f"{intersection_id(r, cc)}_to_{intersection_id(r, cc + 1)}")
        for rr in range(r, 0, -1):
            edges_l.append(
                f"{intersection_id(rr, turn_col)}_to_{intersection_id(rr - 1, turn_col)}"
            )
        edges_l.append(f"{intersection_id(0, turn_col)}_to_{boundary_id('N', turn_col)}")
        rname = f"route_{route_id}"
        routes_xml.append(f'    <route id="{rname}" edges="{" ".join(edges_l)}"/>')
        period = 3600.0 / (vph_per_entry * turn_ratios["left"])
        flows_xml.append(
            f'    <flow id="f_{flow_id}" route="{rname}" '
            f'begin="0" end="3600" period="{period:.2f}" '
            f'departSpeed="max" departLane="best"/>'
        )
        route_id += 1
        flow_id += 1

        # Right: W entry, turn right (south) at col 1
        edges_r = [entry_edge]
        for cc in range(turn_col):
            edges_r.append(f"{intersection_id(r, cc)}_to_{intersection_id(r, cc + 1)}")
        for rr in range(r, GRID_SIZE - 1):
            edges_r.append(
                f"{intersection_id(rr, turn_col)}_to_{intersection_id(rr + 1, turn_col)}"
            )
        edges_r.append(
            f"{intersection_id(GRID_SIZE - 1, turn_col)}_to_{boundary_id('S', turn_col)}"
        )
        rname = f"route_{route_id}"
        routes_xml.append(f'    <route id="{rname}" edges="{" ".join(edges_r)}"/>')
        period = 3600.0 / (vph_per_entry * turn_ratios["right"])
        flows_xml.append(
            f'    <flow id="f_{flow_id}" route="{rname}" '
            f'begin="0" end="3600" period="{period:.2f}" '
            f'departSpeed="max" departLane="best"/>'
        )
        route_id += 1
        flow_id += 1

    # === East boundary entries (traveling westbound) ===
    for r in range(GRID_SIZE):
        entry_edge = f"{boundary_id('E', r)}_to_{intersection_id(r, GRID_SIZE - 1)}"

        # Through: E -> W
        edges = [entry_edge]
        for cc in range(GRID_SIZE - 1, 0, -1):
            edges.append(f"{intersection_id(r, cc)}_to_{intersection_id(r, cc - 1)}")
        edges.append(f"{intersection_id(r, 0)}_to_{boundary_id('W', r)}")
        rname = f"route_{route_id}"
        routes_xml.append(f'    <route id="{rname}" edges="{" ".join(edges)}"/>')
        period = 3600.0 / (vph_per_entry * turn_ratios["through"])
        flows_xml.append(
            f'    <flow id="f_{flow_id}" route="{rname}" '
            f'begin="0" end="3600" period="{period:.2f}" '
            f'departSpeed="max" departLane="best"/>'
        )
        route_id += 1
        flow_id += 1

        # Left: E entry, turn left (south) at col 2
        turn_col = GRID_SIZE - 2
        edges_l = [entry_edge]
        for cc in range(GRID_SIZE - 1, turn_col, -1):
            edges_l.append(f"{intersection_id(r, cc)}_to_{intersection_id(r, cc - 1)}")
        for rr in range(r, GRID_SIZE - 1):
            edges_l.append(
                f"{intersection_id(rr, turn_col)}_to_{intersection_id(rr + 1, turn_col)}"
            )
        edges_l.append(
            f"{intersection_id(GRID_SIZE - 1, turn_col)}_to_{boundary_id('S', turn_col)}"
        )
        rname = f"route_{route_id}"
        routes_xml.append(f'    <route id="{rname}" edges="{" ".join(edges_l)}"/>')
        period = 3600.0 / (vph_per_entry * turn_ratios["left"])
        flows_xml.append(
            f'    <flow id="f_{flow_id}" route="{rname}" '
            f'begin="0" end="3600" period="{period:.2f}" '
            f'departSpeed="max" departLane="best"/>'
        )
        route_id += 1
        flow_id += 1

        # Right: E entry, turn right (north) at col 2
        edges_r = [entry_edge]
        for cc in range(GRID_SIZE - 1, turn_col, -1):
            edges_r.append(f"{intersection_id(r, cc)}_to_{intersection_id(r, cc - 1)}")
        for rr in range(r, 0, -1):
            edges_r.append(
                f"{intersection_id(rr, turn_col)}_to_{intersection_id(rr - 1, turn_col)}"
            )
        edges_r.append(f"{intersection_id(0, turn_col)}_to_{boundary_id('N', turn_col)}")
        rname = f"route_{route_id}"
        routes_xml.append(f'    <route id="{rname}" edges="{" ".join(edges_r)}"/>')
        period = 3600.0 / (vph_per_entry * turn_ratios["right"])
        flows_xml.append(
            f'    <flow id="f_{flow_id}" route="{rname}" '
            f'begin="0" end="3600" period="{period:.2f}" '
            f'departSpeed="max" departLane="best"/>'
        )
        route_id += 1
        flow_id += 1

    content = '<?xml version="1.0" encoding="UTF-8"?>\n<routes>\n'
    content += '    <vType id="car" length="5" minGap="2.5" maxSpeed="13.89" '
    content += 'accel="2.6" decel="4.5"/>\n\n'
    content += "\n".join(routes_xml) + "\n\n"
    content += "\n".join(flows_xml) + "\n"
    content += "</routes>"

    path = os.path.join(NETWORK_DIR, "grid_4x4.rou.xml")
    with open(path, "w") as f:
        f.write(content)
    print(f"  Routes: {len(routes_xml)} routes, {len(flows_xml)} flows")
    return path


def write_tls_additional():
    """Define 2-phase TLS programs for all 16 intersections.

    Phase structure (simple 2-phase):
      Phase 0: NS green (+ yellow transition)
      Phase 1: EW green (+ yellow transition)

    For a 4-arm intersection with 2 lanes per approach, the connection
    state string depends on the actual connections generated by netconvert.
    We use a generic approach: let netconvert generate TLS via --tls.guess,
    then override with our additional file.

    Since we use --tls.guess in netconvert, SUMO will auto-generate TLS
    programs. We write an additional file that overrides them with our
    simple 2-phase scheme.

    Connection state encoding for 2-lane, 4-arm intersection:
    Each approach has 2 lanes -> left/through movements.
    With 4 approaches (N,S,E,W) x 2 lanes x ~2 movements = variable length.
    We let netconvert decide connection count and override via TraCI at
    runtime. The additional file provides a reasonable default.
    """
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<additional>"]

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            nid = intersection_id(r, c)
            # Count connections: each approach has 2 lanes, and for internal
            # intersections there are 4 approaches with turns to 3 other dirs.
            # Exact state string length depends on netconvert output.
            # We use a placeholder that will be overridden by netconvert's
            # default TLS or by TraCI control.
            #
            # For a standard 4-arm, 2-lane intersection with no U-turns:
            # 4 approaches x 2 lanes x 3 possible turns = 24 connections
            # But corner/edge intersections have fewer approaches.
            # We'll generate a generic 2-phase state string.

            num_approaches = 4  # all internal nodes are 4-arm in a grid
            # Each approach: 2 lanes, each lane can go to 3 directions = 6 connections per approach
            # Total = 24 connections for a fully connected 4-arm
            # NS phase: N and S approaches green (12 connections green, 12 red)
            # EW phase: E and W approaches green

            # We'll use a generic approach - the state string will be adjusted
            # by netconvert. Write a reasonable default for 4-arm intersections.
            # Standard order: connections are listed by incoming edge
            # (alphabetical), then by lane index.

            # For simplicity, use allGreen/allRed with netconvert determining
            # actual connection mapping. The TLS program from netconvert's
            # --tls.guess will be the actual default; this file overrides if loaded.

            # Generic 2-phase for ~16 connections (conservative estimate):
            n_conn = 24  # will be adjusted by netconvert
            half = n_conn // 2
            ns_green = "G" * half + "r" * half
            ns_yellow = "y" * half + "r" * half
            ew_green = "r" * half + "G" * half
            ew_yellow = "r" * half + "y" * half

            lines.append(f'    <tlLogic id="{nid}" type="static" programID="default" offset="0">')
            lines.append(f'        <!-- NS green -->')
            lines.append(f'        <phase duration="30" state="{ns_green}" minDur="10" maxDur="45"/>')
            lines.append(f'        <!-- NS yellow -->')
            lines.append(f'        <phase duration="3"  state="{ns_yellow}"/>')
            lines.append(f'        <!-- EW green -->')
            lines.append(f'        <phase duration="30" state="{ew_green}" minDur="10" maxDur="45"/>')
            lines.append(f'        <!-- EW yellow -->')
            lines.append(f'        <phase duration="3"  state="{ew_yellow}"/>')
            lines.append(f'    </tlLogic>')

    lines.append("</additional>")
    content = "\n".join(lines)
    path = os.path.join(NETWORK_DIR, "grid_4x4.add.xml")
    with open(path, "w") as f:
        f.write(content)
    return path


def write_sumo_config(net_file, route_file):
    """Write SUMO configuration file."""
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
    path = os.path.join(NETWORK_DIR, "grid_4x4.sumocfg")
    with open(path, "w") as f:
        f.write(content)
    return path


def build_network(nod_file, edg_file):
    """Run netconvert to compile the network."""
    net_file = os.path.join(NETWORK_DIR, "grid_4x4.net.xml")
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
        print(f"  netconvert warnings:\n{result.stderr[:500]}")
    return net_file


def regenerate_tls_from_net(net_file):
    """Read the compiled net file to determine actual connection counts
    per TLS and regenerate the additional file with correct state string lengths.
    """
    import xml.etree.ElementTree as ET

    tree = ET.parse(net_file)
    root = tree.getroot()

    # Collect TLS connection counts from the net file
    tls_connections = {}
    for conn in root.findall(".//connection"):
        tl = conn.get("tl")
        if tl:
            link_idx = int(conn.get("linkIndex", 0))
            if tl not in tls_connections:
                tls_connections[tl] = 0
            tls_connections[tl] = max(tls_connections[tl], link_idx + 1)

    # Also read the auto-generated TLS programs to understand phase structure
    tls_programs = {}
    for tl_logic in root.findall(".//tlLogic"):
        tl_id = tl_logic.get("id")
        phases = []
        for phase in tl_logic.findall("phase"):
            phases.append(phase.get("state"))
        tls_programs[tl_id] = phases

    # Regenerate additional file with correct state string lengths
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<additional>"]

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            nid = intersection_id(r, c)
            n_conn = tls_connections.get(nid, 24)

            # Read auto-generated program to understand the connection ordering
            auto_phases = tls_programs.get(nid, [])
            if auto_phases:
                # Use the auto-generated program as basis but simplify to 2-phase
                # The auto-generated program already has correct state string lengths
                state_len = len(auto_phases[0])

                # Build 2-phase program: NS directions vs EW directions
                # Parse auto-generated phases to identify NS vs EW connections
                # For simplicity, construct from auto-program: merge phases that
                # serve NS (phases 0,1 typically) and EW (phases 2,3 typically)
                # into just 2 green phases.

                # Strategy: take the first auto-phase as "group A green",
                # create complement as "group B green"
                ns_green_chars = list(auto_phases[0])
                ew_green_chars = []
                for i, ch in enumerate(ns_green_chars):
                    if ch in ('G', 'g'):
                        ew_green_chars.append('r')
                    else:
                        ew_green_chars.append('G')

                ns_green = "".join(ns_green_chars)
                ns_yellow = ns_green.replace('G', 'y').replace('g', 'y')
                ew_green = "".join(ew_green_chars)
                ew_yellow = ew_green.replace('G', 'y').replace('g', 'y')
            else:
                # Fallback: generate generic states
                half = n_conn // 2
                ns_green = "G" * half + "r" * (n_conn - half)
                ns_yellow = "y" * half + "r" * (n_conn - half)
                ew_green = "r" * half + "G" * (n_conn - half)
                ew_yellow = "r" * half + "y" * (n_conn - half)

            lines.append(
                f'    <tlLogic id="{nid}" type="static" '
                f'programID="default" offset="0">'
            )
            lines.append(f'        <!-- NS green -->')
            lines.append(
                f'        <phase duration="30" state="{ns_green}" '
                f'minDur="10" maxDur="45"/>'
            )
            lines.append(f'        <!-- NS yellow -->')
            lines.append(f'        <phase duration="3"  state="{ns_yellow}"/>')
            lines.append(f'        <!-- EW green -->')
            lines.append(
                f'        <phase duration="30" state="{ew_green}" '
                f'minDur="10" maxDur="45"/>'
            )
            lines.append(f'        <!-- EW yellow -->')
            lines.append(f'        <phase duration="3"  state="{ew_yellow}"/>')
            lines.append(f'    </tlLogic>')

    lines.append("</additional>")
    content = "\n".join(lines)
    path = os.path.join(NETWORK_DIR, "grid_4x4.add.xml")
    with open(path, "w") as f:
        f.write(content)
    print(f"  TLS additional regenerated with correct state lengths for {len(tls_connections)} intersections")
    return path


if __name__ == "__main__":
    print("Creating 4x4 grid network...")
    print(f"  Internal link length: {INTERNAL_LENGTH}m (short for spillback)")
    print(f"  Lanes per direction: {NUM_LANES}")

    nod = write_nodes()
    print(f"  Nodes: {nod}")

    edg = write_edges()
    print(f"  Edges: {edg}")

    net = build_network(nod, edg)
    print(f"  Net: {net}")

    rou = write_routes(total_demand_per_edge=500)
    print(f"  Routes: {rou}")

    # First write a placeholder TLS, then regenerate with correct state lengths
    tls = regenerate_tls_from_net(net)
    print(f"  TLS: {tls}")

    cfg = write_sumo_config(net, rou)
    print(f"  Config: {cfg}")

    print(f"\nNetwork created at: {NETWORK_DIR}")
    print(f"  Grid: {GRID_SIZE}x{GRID_SIZE} = {GRID_SIZE**2} signalized intersections")
    print(f"  Boundary nodes: {4 * GRID_SIZE}")
    print(f"  Total nodes: {GRID_SIZE**2 + 4 * GRID_SIZE}")
