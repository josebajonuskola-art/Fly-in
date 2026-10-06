import sys
from pathlib import Path
from classes.config import ConfigError, Config
from classes.graph import Graph
from classes.simulation import Simulation
from classes.visual_enviroment import VisualEnv


def read_config_file(config_file: str) -> dict[str, str | list[str]]:
    """Reads and validates a configuration file for the drone simulation.

    Parses a plain text configuration file line-by-line, enforcing syntax
    rules,
    checking for required key-value pairs, and aggregating repetitive sections
    (such as 'CONNECTION' and 'HUB') into lists.

    Args:
        config_file (str): Path to the configuration text file.

    Returns:
        dict[str, str | list[str]]: A dictionary containing configuration keys
            mapped to single string values or lists of string values.

    Raises:
        ConfigError: If the file format is invalid, keys/values are missing,
            non-list keys are duplicated, or mandatory expected keys are
            missing.
    """
    dict_cfg: dict[str, str | list[str]] = dict()

    with open(config_file, "r") as file:

        value_line = False

        for nb_line, line in enumerate(file, start=1):
            line = line.strip()

            if not line or line.startswith('#'):
                continue

            if (value_line is False and 'nb_drones:' not in line):
                raise ConfigError(
                    "The first line must define the number of drones "
                    "using 'nb_drones: <positive_integer>'."
                )

            if ':' not in line:
                raise ConfigError(f"Line {nb_line}: missing ':'.")

            k, v = line.split(':', 1)
            k = k.strip()
            k = k.upper()
            v = v.strip()

            if not k:
                raise ConfigError(f"Line {nb_line}: missing key.")

            if not v:
                raise ConfigError(f"Line {nb_line}: missing value.")

            if k in dict_cfg and (k != "CONNECTION" and k != "HUB"):
                raise ConfigError(f"Line {nb_line}: duplicated key.")

            if k not in dict_cfg and (k == "CONNECTION" or k == "HUB"):
                dict_cfg[k] = [v]

            elif k == "CONNECTION" or k == "HUB":
                is_list = dict_cfg[k]
                if isinstance(is_list, list):
                    is_list.append(v)

            else:
                value_line = True
                dict_cfg[k] = v

        expected_keys = ["NB_DRONES", "START_HUB", "END_HUB", "HUB",
                         "CONNECTION"]

        keys = list(dict_cfg.keys())

        for key in expected_keys:
            if key not in keys:
                raise ConfigError(
                    "One or more compulsory expected keys haven't been found "
                    "in the 'config.txt'. Expected keys: 'NB_DRONES', "
                    "'START_HUB', 'END_HUB', 'HUB' and 'CONNECTION'"
                )

        return dict_cfg


def main() -> None:
    """Parses CLI arguments, initializes simulation components, and runs the
    application.

    Validates that a configuration file argument is provided, parses and
    validates
    its content, instantiates the graph and simulation components, and
    launches
    the visual environment interface.
    """
    if (len(sys.argv) != 2 or sys.argv[0] != "fly_in.py"):

        print("No requiered arguments provided. Usage: <python3 ", end='')
        print("fly_in.py config.txt>")
        sys.exit(1)

    if not Path(sys.argv[1]).is_file():
        print("The config file is not present in the root of the project")
        sys.exit(1)

    try:

        config_raw = read_config_file(sys.argv[1])
        config = Config.model_validate(config_raw)

        graph = Graph(config)
        sim = Simulation(graph)
        vis_env = VisualEnv(sim)
        vis_env.start()

    except ConfigError as e:
        print(f"Config error: {e}")
        sys.exit(1)

    except ValueError as e:
        print(f"Value error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
