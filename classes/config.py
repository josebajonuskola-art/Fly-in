from __future__ import annotations
from pydantic import BaseModel, Field, model_validator


class ConfigError(Exception):
    """Exception raised for errors encountered in the configuration setup."""
    pass


class Hub(BaseModel):
    """Represents a hub location in the drone simulation grid.

    Attributes:
        name (str): Unique identifier for the hub.
        x (int): X-coordinate location.
        y (int): Y-coordinate location.
        zone (str): Zone type (e.g., 'normal', 'restricted', 'blocked',
        'priority').
        color (str | None): Color representation for visual display.
        max_drones (int): Maximum capacity of drones the hub can hold
        simultaneously.
        distance_to_goal (int): Computed distance to the goal hub (-1 if
        uncalculated).
        drones_in (int): Current count of drones residing in the hub.
    """

    name: str
    x: int
    y: int
    zone: str = "normal"
    color: str | None = None
    max_drones: int = 1
    distance_to_goal: int = -1
    drones_in: int = 0

    @model_validator(mode="before")
    @classmethod
    def hub_values_checker(cls, data: str) -> dict[str, str | int | None]:
        """Parses and validates raw string data into hub attribute parameters.

        Args:
            data (str): Raw string input containing compulsory hub parameters
                and optional bracketed metadata.

        Returns:
            dict[str, str | int | None]: Dictionary with parsed hub field
            values.

        Raises:
            ConfigError: If coordinates are missing/invalid, metadata format
            is incorrect,
                an unknown zone type is specified, or `max_drones` is
                non-positive.
        """

        zone_value = "normal"
        color_value = None
        max_drones_value = 1

        splited_data = data.split('[', 1)

        compulsory_data = splited_data[0].split(' ')

        try:
            x = int(compulsory_data[1])
            y = int(compulsory_data[2])

        except ValueError:
            raise ConfigError("The hub's configuration must follow the "
                              "next structure: 'obstacleX 5 5'."
                              "<name_of_the_hub> <coordenate_x: int> "
                              "<coordenate_y: int>.")

        if len(splited_data) > 1:

            if not splited_data[1].endswith(']'):
                raise ConfigError("Metadata must follow the next structure "
                                  "'[zone=priority color=green "
                                  "max_drones=2]'.")

            splited_data[1] = splited_data[1][:-1]

            metadata = splited_data[1].split(' ')

            zone_types = ["normal", "restricted", "blocked", "priority"]

            for metadata_fragment in metadata:

                if "zone=" in metadata_fragment:

                    pre_zone = metadata_fragment.split('=', 1)
                    if pre_zone[1] not in zone_types:
                        raise ConfigError('Metadata zone must be one of'
                                          ' the next ones: "normal", '
                                          '"restricted", "blocked", '
                                          '"priority".')

                    zone_value = pre_zone[1]

                elif "color=" in metadata_fragment:

                    pre_color = metadata_fragment.split('=', 1)
                    if not pre_color[1]:
                        raise ConfigError("The color must be a single word"
                                          ". Example 'color=green'.")

                    color_value = pre_color[1]

                elif "max_drones=" in metadata_fragment:

                    pre_max_drones = metadata_fragment.split('=', 1)

                    try:
                        int_pre_max_drones = int(pre_max_drones[1])
                        if int_pre_max_drones <= 0:
                            raise ConfigError("max_drones' value must"
                                              " be a positive integer.")

                    except ValueError:
                        raise ConfigError("max_drones' value must be a "
                                          "positive integer.")

                    max_drones_value = int_pre_max_drones

                else:
                    raise ConfigError("Metadata cannot include nothing "
                                      "apart from those fields '"
                                      "[zone=priority color=green "
                                      "max_drones=2]'.")

        return {
            "name": compulsory_data[0],
            "x": x,
            "y": y,
            "zone": zone_value,
            "color": color_value,
            "max_drones": max_drones_value
        }


class Connection(BaseModel):
    """Represents a connection link between two hubs in the simulation network.

    Attributes:
        zone_a (str): Name of the first connected hub.
        zone_b (str): Name of the second connected hub.
        max_link_capacity (int): Maximum drone capacity allowed on this link.
        is_in_graph (bool): Flag indicating if the link is added to the graph.
        drones_in (int): Current number of drones traveling on this connection.
    """

    zone_a: str
    zone_b: str
    max_link_capacity: int
    is_in_graph: bool = False
    drones_in: int = 0

    @model_validator(mode="before")
    @classmethod
    def connection_values_checker(cls, data: str) -> dict[str, str | int]:
        """Parses and validates raw string data into connection attribute
        parameters.

        Args:
            data (str): Raw string input defining the connected hubs and
            optional metadata.

        Returns:
            dict[str, str | int]: Dictionary containing parsed connection
            parameters.

        Raises:
            ConfigError: If syntax is invalid, zone names contain spaces,
            metadata
                brackets are malformed, or capacity values are non-positive.
        """

        max_link_capacity = 1

        splited_data = data.split('[', 1)

        compulsory_data = splited_data[0].split('-')

        compulsory_data[1] = compulsory_data[1].rstrip()

        if (len(compulsory_data) != 2 or ' ' in
                compulsory_data[0] or ' ' in compulsory_data[1]):
            raise ConfigError("Only two zones are allowed between connections."
                              " The name's of the zones cannot include dashes."
                              "Example of use: 'hub-roof1'.")

        if len(splited_data) > 1:

            if not splited_data[1].endswith(']'):
                raise ConfigError("Metadata must follow the next structure"
                                  " '[max_drones=2]'.")

            splited_data[1] = splited_data[1][:-1]

            metadata = splited_data[1].split(' ')

            for metadata_fragment in metadata:

                if "max_link_capacity" in metadata_fragment:

                    pre_max_drones = metadata_fragment.split('=', 1)
                    try:
                        int_pre_max_drones = int(pre_max_drones[1])
                        if int_pre_max_drones <= 0:
                            raise ConfigError("max_drones' value must be"
                                              " a positive integer.")
                    except ValueError:
                        raise ConfigError("max_drones' value must be a "
                                          "positive integer.")

                    max_link_capacity = int_pre_max_drones

                else:
                    raise ConfigError("Metadata cannot include nothing "
                                      "apart from the field '[max_drones=2]'.")

        return {
            "zone_a": compulsory_data[0],
            "zone_b": compulsory_data[1],
            "max_link_capacity": max_link_capacity
        }


class Config(BaseModel):
    """Main configuration model validating overall simulation environment
    settings.

    Attributes:
        nb_drones (int): Total number of drones participating in the
        simulation.
        start_hub (Hub): Starting hub for all drones.
        end_hub (Hub): Destination hub for all drones.
        hubs (list[Hub]): List of intermediate hub objects.
        connections (list[Connection]): List of connection links between hubs.
    """

    nb_drones: int = Field(alias='NB_DRONES', ge=1)
    start_hub: Hub = Field(alias='START_HUB')
    end_hub: Hub = Field(alias='END_HUB')
    hubs: list[Hub] = Field(alias='HUB')
    connections: list[Connection] = Field(alias='CONNECTION')

    @model_validator(mode="after")
    def config_validator(self) -> 'Config':
        """Validates consistency, uniqueness, and connectivity of hubs and
        connections.

        Ensures hub names and coordinates are unique, connection references
        exist,
        no duplicated connections are present, and initializes capacity
        settings.

        Returns:
            Config: The validated Config model instance.

        Raises:
            ConfigError: If duplicate hub names, duplicate coordinates,
            unregistered
                connection hubs, or duplicate connections are detected.
        """

        hub_names = [h.name for h in self.hubs]
        hub_names.append(self.start_hub.name)
        hub_names.append(self.end_hub.name)

        for i in range(len(hub_names)):
            for j in range(i + 1, len(hub_names)):

                if hub_names[i] == hub_names[j]:
                    raise ConfigError("There are one or more repited "
                                      "hub's names.")

        hub_values = [(h.x, h.y) for h in self.hubs]

        if len(hub_values) != len(set(hub_values)):
            raise ConfigError("There are one or more repited hub's values.")

        connection_names = [(c.zone_a, c.zone_b) for c in self.connections]

        for connection in connection_names:

            if (connection[0] not in hub_names or
                    connection[1] not in hub_names):
                raise ConfigError("At least one of the connection zone's "
                                  "name is not registered in the hubs' names.")

        for i in range(len(connection_names)):
            for j in range(i + 1, len(connection_names)):

                a1, b1 = connection_names[i]
                a2, b2 = connection_names[j]

                if a1 == a2 and b1 == b2:
                    raise ConfigError("At least one connection point is "
                                      "repeated.")

                if a1 == b2 and b1 == a2:
                    raise ConfigError("At least one connection point is "
                                      "repeated(e.g., a-b and b-a are "
                                      "considered duplicates).")

        self.start_hub.max_drones = self.nb_drones + 1
        self.start_hub.drones_in = self.nb_drones
        self.end_hub.max_drones = self.nb_drones + 1

        return self
