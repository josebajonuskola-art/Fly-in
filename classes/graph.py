from .config import Config, Hub


class Graph():
    """Represents the graph structure of hubs and their connections in the
    simulation.

    Attributes:
        cfg (Config): Configuration object containing hubs and connection
        details.
        neighbours (dict[str, list[Hub]]): Mapping of hub names to lists of
        adjacent Hub objects.
    """

    def __init__(self, cfg: Config) -> None:
        """Initializes the Graph instance with configuration settings and
        builds the adjacency list.

        Args:
            cfg (Config): Simulation configuration containing hubs and
            connections.
        """
        self.cfg = cfg
        self.neighbours: dict[str, list[Hub]] = self.get_all_neighbours()

    def print_graph_hub(self) -> None:
        """Prints the graph's adjacency dictionary containing all hubs and
        their neighbors."""

        print(self.neighbours)

    def get_all_neighbours(self) -> dict[str, list[Hub]]:
        """Constructs an adjacency dictionary mapping every hub name to its
        list of neighboring hubs.

        Returns:
            dict[str, list[Hub]]: Dictionary where keys are hub names and
            values are lists
                of neighboring Hub objects.
        """

        ngbs = {}
        ngbs[self.cfg.start_hub.name] = self.get_neighbours(self.cfg.start_hub)
        ngbs[self.cfg.end_hub.name] = self.get_neighbours(self.cfg.end_hub)

        for hub in self.cfg.hubs:
            ngbs[hub.name] = self.get_neighbours(hub)

        return ngbs

    def get_neighbours(self, hub: Hub) -> list[Hub]:
        """Finds all neighboring hubs connected to a given hub.

        Args:
            hub (Hub): The hub for which to find adjacent neighbors.

        Returns:
            list[Hub]: A list of Hub objects connected to the specified hub.
        """

        neighbours: list[Hub] = []
        hub_ngbs_id: list[str] = []
        all_hubs: list[Hub] = (self.cfg.hubs +
                               [self.cfg.start_hub, self.cfg.end_hub])

        for cnn in self.cfg.connections:

            if cnn.zone_a == hub.name and cnn.zone_b not in hub_ngbs_id:
                hub_ngbs_id.append(cnn.zone_b)

            elif cnn.zone_b == hub.name and cnn.zone_a not in hub_ngbs_id:
                hub_ngbs_id.append(cnn.zone_a)

        for hubs in all_hubs:

            if hubs.name in hub_ngbs_id:
                neighbours.append(hubs)

        return neighbours
