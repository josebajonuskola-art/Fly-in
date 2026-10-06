*This project has been created as part of the 42 curriculum by juskola-*

## Description

**Fly-in** is a Python project focused on designing, implementing, and visualizing an efficient multi-drone routing and scheduling simulation. The main goal of the project is to navigate a fleet of autonomous drones from a designated starting hub (`start_hub`) to a target destination (`end_hub`) through a network of interconnected zones in the minimum number of discrete simulation turns. The system must coordinate simultaneous movements, optimize path throughput, avoid spatial conflicts, and account for turn-based movement costs across diverse map topologies.

The program parses map configuration files containing graph structures, zone metadata, and movement constraints. It handles diverse zone types—such as standard `normal` zones, 2-turn `restricted` zones, high-priority routes, and impassable `blocked` areas—alongside capacity restrictions on both zones (`max_drones`) and bidirectional links (`max_link_capacity`). In compliance with strict project constraints, the underlying graph representations and pathfinding algorithms are built entirely from scratch in object-oriented, type-safe Python 3.10+ without relying on third-party graph libraries (such as `networkx`).

Beyond calculating optimal routes, the application provides a step-by-step simulation output tracking each drone's trajectory turn by turn. To make complex routing dynamics intuitive, the project includes visual feedback—delivered either through a colored terminal interface or a graphical display—showing active drone positions, zone occupancy, and link traversals in real time.

Overall, **Fly-in** combines advanced algorithmic optimization, strict object-oriented architecture, static type safety (`mypy` and `flake8`), and real-time visualization to deliver a robust, modular, and high-performance drone traffic management system.

## Instructions

Clone the repository and move into the project folder:
```bash
git clone <repository_url>
cd fly-in
```

All project automation commands can be executed using `make`. Below are all available commands for installation, execution, debugging, linting, and cleanup:


- Create the virtual environment and install dependencies:
```
  make install
```

- Activate the virtual environment:

```
  source .env/bin/activate
```

- Run the simulation using the default configuration file:
```
  make run
```

- Run with a custom map file:
```
  make run CFG=maps/medium_1.txt
```

- Directly with Python:
```
  python3 fly_in.py config.txt
```

- Run the project using Python's built-in debugger:
```
  make debug
```

- Run debug mode on a custom map file:
```
  make debug CFG=maps/hard_1.txt
```

- Run flake8 and mypy checks:
```
  make lint
```

- Run stricter static analysis:
```
  make lint-strict
```

- Remove cache files, temporary files, and the virtual environment:
```
  make clean
```

## Resources

- [Python Official Documentation](https://docs.python.org/3/)
- [flake8 Documentation](https://flake8.pycqa.org/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [tkinter Documentation](https://docs.python.org/3/library/tkinter.html)

### AI usage

Artificial Intelligence tools were used during the project for:

- Improving and organizing documentation.
- Brainstorming project architecture.
- Clarifying path solving concepts.
- Reviewing README structure.
- Improving docstrings.
- Improving code readability and explanations.

## Algorithm explanation and Implementation Strategy

The primary goal of **Fly-in** is to route a fleet of drones from `start_hub` to `end_hub` in the minimal number of simulation turns while strictly observing graph constraints, zone capacities (`max_drones`), and link limits (`max_link_capacity`). 

Our solution is divided into two main phases: **Graph Exploration & Path Discovery** and **Turn-Based Multi-Drone Scheduling**.

---

### 1. Pathfinding & Graph Exploration (Floodfill / Custom BFS)

To navigate the zone network efficiently without relying on third-party graph libraries, we implemented a custom pathfinding algorithm based on the **Floodfill algorithm** (a modified Breadth-First Search):

- **Distance & Cost Mapping:** Starting from the target destination (`end_hub`) back toward the starting hub (`start_hub`), the Floodfill algorithm traverses the graph to map the shortest turn-distance from every accessible zone to the end goal.
- **Handling Zone Movement Costs:**
  - **`normal` zones (1 turn):** Standard movement cost of 1 turn.
  - **`priority` zones (1 turn):** Evaluated with equal turn cost to normal zones but given higher weight precedence during path selection to prioritize high-efficiency corridors.
  - **`restricted` zones (2 turns):** Accounted as a multi-turn step during distance calculations.
  - **`blocked` zones:** Filtered out during graph discovery and treated as non-traversable walls.
- **Shortest Path Set Construction:** Using the distance map generated by Floodfill, the pathfinder extracts a primary set of shortest paths from `start_hub` to `end_hub`. It also identifies alternative/disjoint routes to allow simultaneous drone flow.

---

### 2. Multi-Drone Scheduling & Flow Management

Once candidate paths are identified, a dynamic turn-by-turn scheduler manages drone dispatching and movement:

- **Path Allocation & Distribution:** Drones are distributed across available shortest paths based on route capacities and remaining turns. If sending a drone down an alternative slightly longer path yields an earlier total arrival time than bottlenecking a shorter path, the algorithm dynamically balances the traffic.
- **Capacity Constraint Resolution:**
  - **Zone Capacity (`max_drones`):** Tracked dynamically at each turn. Drones exiting a zone free up space in that same turn, allowing following drones to enter immediately.
  - **Link Capacity (`max_link_capacity`):** Enforces limits on how many drones can traverse a specific connection simultaneously.
- **Multi-Turn Transit (`restricted` zones):** Drones traveling into a restricted zone occupy the incoming connection during the intermediate turn and must land on the target zone on the next turn.
- **Strategic Waiting & Deadlock Avoidance:** If all optimal paths are temporarily at capacity, drones wait at their current zone until capacity frees up, avoiding path collisions or invalid overlaps.

## Visual Representation

To enhance user experience and provide clear insight into the algorithm's decision-making process, **Fly-in** includes a real-time Graphical User Interface (GUI) built with Python’s native **`tkinter`** library, alongside optional colored terminal logging.

---

### Key GUI Features

- **Dynamic Graph Rendering:** Automatically layout and displays zones (`start_hub`, `end_hub`, `hub`) as interactive nodes, positioning them based on parsed integer coordinates and connecting them with bidirectional links.
- **Zone & Link Color-Coding:** Visually reflects metadata properties:
  - **Zone Types:** Color-coded highlights for `normal`, `priority` (preferred routes), `restricted` (2-turn delay), and `blocked` (impassable walls).
  - **Custom Colors:** Renders specific custom color attributes defined in map metadata (`[color=red]`, `[color=blue]`, etc.).
- **Animated Drone Movements:** Drones are rendered as animated icons/tokens smoothly transitioning between zones frame by frame for each simulation turn.
- **Capacity & Occupancy Indicators:** Displays live numeric overlays on zones (`max_drones`) and links (`max_link_capacity`) to visualize real-time congestion and traffic bottlenecks.
- **Interactive Playback Controls:** Includes a control panel with **Play / Pause**, **Next Turn / Step**, **Reset**, and a **Simulation Speed Slider** to adjust execution tempo.

---

### How It Enhances User Experience (UX)

1. **Instant Topology Verification:** Allows users and evaluators to instantly inspect complex map layouts, verify connected components, and spot isolated or blocked zones without manually analyzing raw text files.
2. **Pathfinding & Scheduling Transparency:** Step-by-step playback makes complex multi-drone scheduling choices clear—demonstrating why certain drones wait, split across alternative paths, or prioritize specific corridors.
3. **Debugging & Bottleneck Analysis:** Live capacity overlays make it easy to identify spatial conflicts, link saturation, or queue formation during test case evaluations.
4. **Seamless Dual Output:** Works in tandem with standard terminal logging (`D1-roof1 D2-corridorA`), making peer evaluations interactive, engaging, and easy to validate.

## Example Input and Expected Output

Below is an example of a map configuration file and the corresponding turn-by-turn simulation output generated by **Fly-in**.

### Sample Input Map (`maps/example.map`)

```txt
nb_drones: 2
start_hub: start 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=normal]
hub: roof2 6 2 [zone=normal]
hub: corridorA 4 3 [zone=priority max_drones=1]
hub: tunnelB 7 4 [zone=normal]
connection: start-roof1
connection: start-corridorA
connection: roof1-roof2
connection: roof2-goal
connection: corridorA-tunnelB [max_link_capacity=1]
connection: tunnelB-goal
```

### Sample Output

```txt
D1-roof1 D2-corridorA
D1-roof2 D2-tunnelB
D1-goal D2-goal
```