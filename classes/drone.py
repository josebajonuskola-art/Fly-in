from __future__ import annotations
from .config import Hub, Connection
from enum import Enum


class DroneStatus(Enum):
    """Enumeration representing the current operational status of a drone."""

    WAITING = 1
    MOVING = 2
    DELIVERED = 3


class Drone():
    """Represents an autonomous drone agent within the simulation.

    Attributes:
        id (int): Unique identifier for the drone.
        status (DroneStatus): Current status of the drone (WAITING, MOVING, or
        DELIVERED).
        position (Hub | Connection): Current location, either resting at a Hub
        or traveling on a Connection.
        turns_remaining (int): Number of simulation turns remaining before
        completing current action/movement.
        path (list[Hub]): Ordered list of hubs representing the drone's
        assigned route.
    """

    def __init__(self, id: int, status: DroneStatus,
                 position: Hub | Connection, turns_remaining: int) -> None:
        """Initializes a new Drone instance.

        Args:
            id (int): Unique identifier for the drone.
            status (DroneStatus): Initial operational state of the drone.
            position (Hub | Connection): Starting hub or connection link
            where the drone resides.
            turns_remaining (int): Number of turns required to complete
            movement or transition.
        """

        self.id = id
        self.status = status
        self.position: Hub | Connection = position
        self.turns_remaining = turns_remaining
        self.path: list[Hub] = []
