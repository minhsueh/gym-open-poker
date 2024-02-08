import yaml

config_path = './config.yaml'
with open(config_path, "r") as stream:
    try:
        default_config_dict = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
