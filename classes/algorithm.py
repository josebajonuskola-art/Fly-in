from .config import Connection, Config, Hub, ConfigError
from .simulation import Simulation


class Algorithm():
    """Provides pathfinding and graph analysis algorithms for drone
        simulation."""

    def __init__(self, simulation: Simulation, configuration: Config):
        """Initializes the Algorithm instance with simulation and
            configuration context.

        Args:
            simulation (Simulation): The simulation instance containing
            the graph.
            configuration (Config): Configuration data containing
            hubs and connections.
        """
        self.simulation = simulation
        self.configuration = configuration

    def distances_printer(self) -> None:
        """Prints the calculated distance to goal for all hubs in
        the configuration."""

        print(f"Hubs name: {self.configuration.start_hub.name} | "
              "Distance to goal: "
              f"{self.configuration.start_hub.distance_to_goal}")

        for hub in self.configuration.hubs:
            print(f"Hubs name: {hub.name} | Distance to goal:"
                  f" {hub.distance_to_goal}")

        print(f"Hubs name: {self.configuration.end_hub.name} "
              "| Distance to goal: "
              f"{self.configuration.end_hub.distance_to_goal}")

    def get_hub_neighbours(self, hub: Hub) -> list[Hub]:
        """Retrieves the list of neighboring hubs for a specified hub.

        Args:
            hub (Hub): The hub whose neighbors are to be found.

        Returns:
            list[Hub]: A list of neighboring Hub instances.

        Raises:
            ValueError: If no neighbors are registered for the given hub.
        """

        for hubs, neighbours in self.simulation.graph.neighbours.items():

            if hub.name == hubs:
                return neighbours

        raise ValueError(f"No neighbours found for '{hub.name}'.")

    def evo_flood_filler(self) -> None:
        """Calculates distance from each hub to goal hub using
        flood fill algorithm.

        Traverses graph backwards from end hub, updating distance_to_goal
        on each hub
        based on zone cost (normal, priority, or restricted).
        """

        goal_hub = self.configuration.end_hub
        goal_hub.distance_to_goal = 0
        hubs_to_fill: list[Hub] = [goal_hub]

        while hubs_to_fill:
            actual_hub = hubs_to_fill.pop(0)
            for hub in self.get_hub_neighbours(actual_hub):
                if hub.distance_to_goal == -1:

                    if hub.zone == "normal":
                        hub.distance_to_goal = actual_hub.distance_to_goal + 1
                        hubs_to_fill.append(hub)

                    elif hub.zone == "priority":
                        hub.distance_to_goal = actual_hub.distance_to_goal + 1
                        hubs_to_fill.append(hub)

                    elif hub.zone == "restricted":
                        hub.distance_to_goal = actual_hub.distance_to_goal + 2
                        hubs_to_fill.append(hub)

    def search_connection(self, hub_from: Hub, hub_to: Hub) -> Connection:
        """Finds the Connection object bridging two specific hubs.

        Args:
            hub_from (Hub): The originating hub.
            hub_to (Hub): The destination hub.

        Returns:
            Connection: The matching connection object between the two hubs.

        Raises:
            ValueError: If no connection is found between the specified hubs.
        """

        for connection in self.configuration.connections:

            if (connection.zone_a == hub_from.name and
                    connection.zone_b == hub_to.name) or \
                    (connection.zone_a == hub_to.name and
                     connection.zone_b == hub_from.name):
                return connection

        raise ValueError(f"No connection found between '{hub_from.name}'"
                         f" and '{hub_to.name}'")

    def candidate_cleaner(self, candidates: list[Hub]) -> list[Hub]:
        """Filters candidates to keep only hubs reachable from the goal.
        Args: candidates: Hubs connected to the current hub.
        Returns: A list containing only candidates with a valid
        distance to the goal. """

        new_candidates: list[Hub] = []

        for candidate in candidates:
            if candidate.distance_to_goal >= 0:
                new_candidates.append(candidate)

        return new_candidates

    def path_solver(self) -> list[Hub | Connection]:
        """Calculates and constructs the optimal route from start hub to
        end hub.

        Runs flood fill distance computation and steps through best
        neighboring hubs,
        incorporating specific connection instances when passing through
        restricted zones.

        Returns:
            list[Hub | Connection]: An ordered sequence of Hubs (and
            Connections
                for restricted zones) representing the computed path.
        """

        path: list[Hub | Connection] = []
        actual_hub: Hub = self.configuration.start_hub
        path.append(actual_hub)

        self.evo_flood_filler()

        while actual_hub.name != self.configuration.end_hub.name:
            candidates = self.get_hub_neighbours(actual_hub)
            candidates = self.candidate_cleaner(candidates)

            if len(candidates) == 0:
                raise ConfigError("There is no possible path resolution.")

            next_hub = candidates[0]

            for candidate in candidates:

                if candidate.distance_to_goal < next_hub.distance_to_goal:
                    next_hub = candidate

                elif candidate.distance_to_goal == next_hub.distance_to_goal:
                    if candidate.zone == "priority":
                        next_hub = candidate

            if next_hub.zone == "restricted":
                path.append(self.search_connection(actual_hub, next_hub))
                path.append(next_hub)

            else:
                path.append(next_hub)

            actual_hub = next_hub

        return path
