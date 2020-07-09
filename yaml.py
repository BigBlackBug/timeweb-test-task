def _parse_line(line: str) -> tuple:
    key_start = line.find('-')
    key_end = line.rfind(":")
    if key_start == -1 or key_end == -1:
        raise ValueError(f"Line {line} does not contain "
                         f"a valid key-value string")
    key = line[key_start + 1:key_end].strip()
    if len(key) == 0:
        raise ValueError(f"Empty key detected")
    value = line[key_end + 1:].strip()
    if len(value) == 0:
        raise ValueError(f"Empty values for key: '{key}' "
                         f"are not allowed")
    return key, value


def from_file(config_file: str,
              keys=frozenset({'directory', 'database', 'log'})) -> dict:
    """
    Parses a yaml config file
    :param config_file:
    :param keys:
    :return: dict with parsed data
    """
    # since we're not allowed to use the yaml module
    # this simplistic approach will do
    # Also I'm not doing any extra validation
    # as it'd would take a lot more time and is out of the
    # scope of the task
    config = {}
    with open(config_file) as file:
        line = file.readline()
        if 'conf:' not in line:
            raise ValueError("Invalid configuration file")
        for line in file.readlines():
            line = line.strip()
            key, value = _parse_line(line)
            if key not in keys:
                raise ValueError(f"Unsupported config key '{key}'")
            config[key] = value
    if not keys.issubset(config.keys()):
        raise ValueError(f"All keys '{', '.join(keys)}' are required")
    return config
