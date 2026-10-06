import tkinter as tk
from .config import Hub, Connection
from .drone import Drone
from .simulation import Simulation


class VisualEnv():
    """Provides a graphical user interface (GUI) using Tkinter to visualize
    the drone simulation.

    Attributes:
        simulation (Simulation): The active simulation instance containing
        graph and drone state.
        scale (float): Scale factor used to convert simulation coordinates to
        screen pixels.
        offset_x (int): Horizontal offset for centering the environment on
        canvas.
        offset_y (int): Vertical offset for centering the environment on
        canvas.
        font_size (int): Calculated dynamic font size for canvas text elements.
        max_x (int): Maximum X coordinate across all hubs.
        max_y (int): Maximum Y coordinate across all hubs.
        min_x (int): Minimum X coordinate across all hubs.
        min_y (int): Minimum Y coordinate across all hubs.
    """

    def __init__(self, simulation: Simulation) -> None:
        """Initializes the VisualEnv instance with the simulation context and
        default view metrics.

        Args:
            simulation (Simulation): The simulation instance containing graph
            and drone states.
        """
        self.simulation = simulation
        self.scale: float = 0
        self.offset_x: float = 0
        self.offset_y: float = 0
        self.font_size: int = 0
        self.max_x: int = 0
        self.max_y: int = 0
        self.min_x: int = 0
        self.min_y: int = 0

    def _all_hubs(self) -> list[Hub]:
        """Retrieves a consolidated list of all hubs in the simulation.

        Returns:
            list[Hub]: Complete list containing the start hub, end hub, and
            intermediate hubs.
        """
        return (
            [self.simulation.graph.cfg.start_hub,
             self.simulation.graph.cfg.end_hub]
            + self.simulation.graph.cfg.hubs
        )

    def _find_bounds(self, hubs: list[Hub]) -> tuple[int, int, int, int]:
        """Calculates boundary coordinate values (min/max X and Y) across all
        provided hubs.

        Args:
            hubs (list[Hub]): List of hubs to extract bounding coordinates
            from.

        Returns:
            tuple[int, int, int, int]: Bounding values as (min_x, min_y
            , max_x, max_y).
        """
        self.min_x = min(h.x for h in hubs)
        self.min_y = min(h.y for h in hubs)
        self.max_x = max(h.x for h in hubs)
        self.max_y = max(h.y for h in hubs)
        return self.min_x, self.min_y, self.max_x, self.max_y

    def _to_pixel(self, x: int, y: int) -> tuple[int, int]:
        """Converts simulation space grid coordinates into canvas screen pixel
        positions.

        Args:
            x (int): X-coordinate in simulation space.
            y (int): Y-coordinate in simulation space.

        Returns:
            tuple[int, int]: Transformed (pixel_x, pixel_y) screen coordinates.
        """
        return int(
            (x - self.min_x) * self.scale + self.offset_x), int(
            (y - self.min_y) * self.scale + self.offset_y)

    def _compute_scale_and_offset(
        self, canvas_width: float, canvas_height: float, margin: float
    ) -> tuple[float, int, int]:
        """Calculates display scaling factor and canvas offset to fit all hubs
        on screen.

        Args:
            canvas_width (float): Total width of the canvas in pixels.
            canvas_height (float): Total height of the canvas in pixels.
            margin (float): Margin padding around canvas borders.

        Returns:
            tuple[float, int, int]: Calculated scale factor, x offset, and y
            offset.
        """

        usable_width: float = canvas_width - 2 * margin
        usable_height: float = canvas_height - 2 * margin

        range_x = max(self.max_x - self.min_x, 1)
        range_y = max(self.max_y - self.min_y, 1)

        scale_x = usable_width / range_x
        scale_y = usable_height / range_y
        self.scale = min(scale_x, scale_y)

        drawn_width = range_x * self.scale
        drawn_height = range_y * self.scale

        self.offset_x = margin + (usable_width - drawn_width) / 2
        self.offset_y = margin + (usable_height - drawn_height) / 2

        return self.scale, int(self.offset_x), int(self.offset_y)

    def _compute_font_size(self) -> int:
        """Determines an appropriate font size bounded within min and max
        constraints based on scale.

        Returns:
            int: Calculated font size.
        """
        base_size = int(self.scale)
        return max(2, min(base_size, 7))

    def _create_connection(
            self, connection: Connection
    ) -> None:
        """Renders a connection line and capacity information label on the
        canvas.

        Args:
            connection (Connection): Connection link object to be drawn.
        """

        hub_a = self.find_hub(connection.zone_a)
        hub_b = self.find_hub(connection.zone_b)

        px_a, py_a = self._to_pixel(hub_a.x, hub_a.y)
        px_b, py_b = self._to_pixel(hub_b.x, hub_b.y)

        self.canvas.create_line(px_a, py_a, px_b, py_b,
                                fill="black", width=2)

        mid_x = (px_a + px_b) / 2 + 15
        mid_y = (py_a + py_b) / 2 + 15
        conn_info = f"{connection.drones_in}/{connection.max_link_capacity}"

        self.canvas.create_text(
            mid_x, mid_y, text=conn_info, font=("Arial", self.font_size))

    def _create_hub(
            self, hub: Hub
    ) -> None:
        """Renders a hub circle indicator and associated info text on the
        canvas.

        Args:
            hub (Hub): Hub object to be drawn.
        """

        p_x, p_y = self._to_pixel(
            hub.x, hub.y
        )

        if hub.color is None:
            color = self._color_for_zone(hub.zone)
        else:
            color = self._safe_color(hub.color)

        self.canvas.create_oval(
            p_x - 5, p_y - 5, p_x + 5, p_y + 5, fill=color
        )

        hub_info = (f"{hub.name}\n Max drones: {hub.max_drones}\n"
                    f"Drones in: {hub.drones_in}\nDistance: {hub.distance_to_goal}")

        self.canvas.create_text(
            p_x, p_y + 40, text=hub_info, font=("Arial", self.font_size))

    def _create_drone(self, drone: Drone) -> None:
        """Renders a drone marker on the canvas based on its current position
        (Hub or Connection).

        Args:
            drone (Drone): Drone object to be drawn.
        """

        if isinstance(drone.position, Hub):

            p_x, p_y = self._to_pixel(drone.position.x, drone.position.y)
            self.canvas.create_rectangle(p_x - 5, p_y - 5, p_x + 5, p_y + 5)

        elif isinstance(drone.position, Connection):

            hub_a = self.find_hub(drone.position.zone_a)
            hub_b = self.find_hub(drone.position.zone_b)

            px_a, py_a = self._to_pixel(hub_a.x, hub_a.y)
            px_b, py_b = self._to_pixel(hub_b.x, hub_b.y)

            mid_x = (px_a + px_b) / 2
            mid_y = (py_a + py_b) / 2

            self.canvas.create_rectangle(
                mid_x - 5, mid_y - 5, mid_x + 5, mid_y + 5,
                fill="black", width=2
            )

    def _safe_color(self, color: str) -> str:
        """Validates a color string against Tkinter's recognized color names.

        Args:
            color (str): Candidate color name, typically provided by the
            user's config file.

        Returns:
            str: The original color if valid for Tkinter, otherwise a fallback
            color.
        """
        try:
            self.canvas.winfo_rgb(color)
            return color
        except Exception:
            return "gray"

    def _color_for_zone(self, zone: str) -> str:
        """Maps a zone type to a predefined, always-valid Tkinter color.

        Args:
            zone (str): Zone type (normal, priority, restricted, blocked).

        Returns:
            str: Color name associated with the given zone type.
        """
        colors = {
            "normal": "gray",
            "priority": "gold",
            "restricted": "orange",
            "blocked": "black",
        }
        return colors.get(zone, "gray")

    def find_hub(self, hub_name: str) -> Hub:
        """Finds a Hub object by its name among all hubs in the simulation.

        Args:
            hub_name (str): Name of the hub to search for.

        Returns:
            Hub: The matching Hub object.

        Raises:
            ValueError: If no hub with the given name exists.
        """
        hubs = self._all_hubs()

        for hub in hubs:
            if hub.name == hub_name:
                return hub

        raise ValueError(f"No hub found with name '{hub_name}'.")

    def _create_turn_indicator(self) -> None:
        """Renders a text label on the canvas showing the current simulation
        turn."""

        canvas_width = 1200
        self.canvas.create_text(
            canvas_width - 15, 15,
            text=f"Turn: {self.simulation.turn}",
            anchor="ne",
            font=("Arial", 16, "bold"),
        )

    def start(self) -> None:
        """Creates the Tkinter window, computes the fixed layout metrics once,
        binds the space key to advance turns, draws the initial state, and
        starts the Tkinter event loop.
        """

        root = tk.Tk()
        canvas_width = 1920
        canvas_height = 1080
        margin = 100
        self.canvas = tk.Canvas(
            root, width=canvas_width, height=canvas_height, bg="lightblue"
        )
        self.canvas.pack()

        hubs = self._all_hubs()
        self.min_x, self.min_y, self.max_x, self.max_y = (
            self._find_bounds(hubs))
        self.scale, self.offset_x, self.offset_y = (
            self._compute_scale_and_offset(
                canvas_width, canvas_height, margin
            ))

        self.font_size = self._compute_font_size()

        root.bind("<space>", self._on_space)
        root.focus_set()

        self.render()

        root.mainloop()

    def _on_space(self, event: tk.Event) -> None:
        """Callback executed when the space key is pressed: advances one
        simulation turn and redraws the canvas, unless the simulation has
        already finished.

        Args:
            event (tk.Event): The key-press event supplied by Tkinter.
        """
        if not self.simulation.is_finished():
            self.simulation.actual_turn()
            self.render()

    def render(self) -> None:
        """Clears the canvas and redraws the full current state: turn
        indicator, connections, hubs, and drones.
        """

        self.canvas.delete("all")

        self._create_turn_indicator()

        for connection in self.simulation.graph.cfg.connections:
            self._create_connection(connection)

        for hub in self._all_hubs():
            self._create_hub(hub)

        for drone in self.simulation.drones:
            self._create_drone(drone)
