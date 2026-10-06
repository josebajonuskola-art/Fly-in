from .config import Hub, Connection
from .drone import Drone, DroneStatus
from .graph import Graph


class Simulation():
    """Manages the simulation execution, drone navigation, turn updates, and
    state tracking.

    Attributes:
        graph (Graph): The graph structure representing the simulation
        topology.
        drones (list[Drone]): List of active drone instances in the simulation.
        turn (int): Current simulation turn counter.
        delivered_drones (int): Total count of drones that have reached the
        end hub.
        path (list[Hub | Connection]): Computed optimal path sequence for
        drone movement.
    """

    def __init__(self, graph: Graph) -> None:
        """Initializes the Simulation instance with a graph and prepares the
        setup.

        Args:
            graph (Graph): The graph structure containing hubs and connections.
        """

        self.graph = graph
        self.drones: list[Drone] = []
        self.turn = 0
        self.delivered_drones = 0
        self.path: list[Hub | Connection] = []

        self.setup()

    def setup(self) -> None:
        """Computes the path solution using the algorithm solver and
        initializes drones."""
        from .algorithm import Algorithm

        algo = Algorithm(self, self.graph.cfg)
        self.path = algo.path_solver()
        self.drone_initializer()

    def drone_initializer(self) -> None:
        """Instantiates all drone instances based on the configured drone
        count."""

        for drone_id in range(self.graph.cfg.nb_drones):
            self.drones.append(Drone(
                drone_id, DroneStatus.WAITING,
                self.graph.cfg.start_hub, 0
            ))

    def move_drone(self, drone: Drone, point_1: Hub | Connection,
                   point_2: Hub | Connection) -> None:
        """Updates a drone's position to the target location and prints the
        move trace.

        Args:
            drone (Drone): The drone instance being moved.
            point_1 (Hub | Connection): The current position before the move.
            point_2 (Hub | Connection): The target destination
            (Hub or Connection).
        """

        drone.position = point_2

        print(f"D{drone.id}-", end='')

        if hasattr(point_2, "name"):
            print(f"{point_2.name}", end=' ')
            if point_2.name == self.graph.cfg.end_hub.name:
                drone.status = DroneStatus.DELIVERED

        else:
            print(f"{point_2.zone_a}-{point_2.zone_b}", end=' ')

    def get_next_position(
        self, position: Hub | Connection,
        path: list[Hub | Connection]
    ) -> Hub | Connection:
        """Determines the immediate next point along a specified path from a
        current position.

        Args:
            position (Hub | Connection): Current location in the route.
            path (list[Hub | Connection]): Sequence of hubs and connections
            forming the route.

        Returns:
            Hub | Connection: The subsequent point in the path sequence.

        Raises:
            ValueError: If the current position is not found in the path or
            has no successor.
        """

        i = 0
        actual_position: Hub | Connection = position

        for position in path:

            if isinstance(actual_position, Hub):
                if isinstance(position, Hub):
                    if position.name == actual_position.name:
                        return path[i + 1]

            if isinstance(actual_position, Connection):
                if isinstance(position, Connection):
                    if (position.zone_a == actual_position.zone_a and
                            position.zone_b == actual_position.zone_b):
                        return path[i + 1]

            i += 1

        if isinstance(position, Connection):
            raise ValueError("No next position found for '"
                             f"{position.zone_a}-{position.zone_b}'.")

        raise ValueError(f"No next position found for '{position.name}'.")

    def get_moving_drones_and_positions(
        self, path: list[Hub | Connection]
    ) -> list[tuple[Drone, Hub | Connection]]:
        """Identifies drones eligible to advance during the turn based on
        capacity limits.

        Args:
            path (list[Hub | Connection]): The path sequence guiding drone
            movements.

        Returns:
            list[tuple[Drone, Hub | Connection]]: Pairs of drones and their
            approved next positions.
        """

        moving_drones_and_positions: list[
            tuple[Drone, Hub | Connection]
        ] = []

        for drone in self.drones:

            if drone.status == DroneStatus.DELIVERED:
                continue

            next_position: Hub | Connection = self.get_next_position(
                drone.position, path
            )
            if isinstance(next_position, Hub):

                if (next_position.zone != "restricted"
                        and next_position.drones_in
                        < next_position.max_drones):
                    drone.position.drones_in -= 1
                    next_position.drones_in += 1
                    moving_drones_and_positions.append(
                        (drone, next_position)
                    )

                elif (next_position.zone == "restricted"
                        and next_position.drones_in
                        < next_position.max_drones + 1):
                    drone.position.drones_in -= 1
                    moving_drones_and_positions.append(
                        (drone, next_position)
                    )

            if isinstance(next_position, Connection):
                next_restr_hub = self.get_next_position(
                    next_position, path
                )
                if isinstance(next_restr_hub, Hub):
                    if (next_restr_hub.drones_in
                            < next_restr_hub.max_drones):
                        if (next_position.drones_in
                                < next_position.max_link_capacity):
                            drone.position.drones_in -= 1
                            next_position.drones_in += 1
                            next_restr_hub.drones_in += 1
                            moving_drones_and_positions.append(
                                (drone, next_position)
                            )

        return moving_drones_and_positions

    def actual_turn(self) -> list[tuple[Drone, Hub | Connection]]:
        """Executes a single simulation turn by moving eligible drones and
        updating state.

        Returns:
            list[tuple[Drone, Hub | Connection]]: A list of drone movements
            executed in this turn.
        """
        drones_moving_this_turn = (
                self.get_moving_drones_and_positions(self.path)
            )
        for drone, next_position in drones_moving_this_turn:

            self.move_drone(drone, drone.position, next_position)

            if next_position == self.graph.cfg.end_hub:
                drone.status = DroneStatus.DELIVERED
                self.delivered_drones += 1

        print('')

        self.turn += 1

        return drones_moving_this_turn

    def is_finished(self) -> bool:
        """Checks if all drones have successfully reached the destination hub.

        Returns:
            bool: True if all drones have delivered, False otherwise.
        """
        return self.delivered_drones >= self.graph.cfg.nb_drones
