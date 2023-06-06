import yaml
from utils.logger import (
    logger,
    log_obj,
)
from typing import (
    List,
    Dict,
    Literal,
)


class Config:
    @log_obj
    def __init__(self, config_file_path="updater.yaml"):
        self.config = self.__read_conf(config_file_path)
        self.task = self.__parse_section("task")
        self.__parse_section("schedule")
        self.__parse_section("remove")
        self.__parse_section("other")
        self.__parse_section("drw_local")
        self.__parse_section("drw")
        self.__parse_section("drw_linux")
        self.__parse_section("ksc")
        self.__parse_section("weekly_pack")
        self.__parse_section("rename")
        self.__parse_section("pre_total_script")
        self.__parse_section("total_archive")
        self.__parse_section("post_total_script")

    def __read_conf(self, file_path):
        with open(file_path, "r") as file:
            return yaml.safe_load(file)

    def __parse_section(self, section_name):
        for key, value in zip(
            self.config[section_name], self.config[section_name].values()
        ):
            setattr(self, key, value)
            logger.debug(f"{key}:{value}")
        return self.config[section_name]
