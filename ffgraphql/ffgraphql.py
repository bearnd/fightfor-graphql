# coding: utf-8

"""Main module."""

import os
import argparse

import sqlalchemy.orm
from fform.dal_base import DalBase

from ffgraphql.config import import_config
from ffgraphql.api import create_api
from ffgraphql.schema import schema


_cfg = None


def load_config(filename_config_file=None):
    if filename_config_file:
        cfg = import_config(fname_config_file=filename_config_file)
    elif "FFGRAPHQL_CONFIG" in os.environ:
        fname_config_file = os.environ["FFGRAPHQL_CONFIG"]
        cfg = import_config(fname_config_file=fname_config_file)
    else:
        msg_fmt = "Configuration file path not defined."
        raise ValueError(msg_fmt)

    return cfg


def get_cfg(filename_config_file=None):
    global _cfg
    if _cfg is None:
        _cfg = load_config(filename_config_file=filename_config_file)

    return _cfg


def main(filename_config_file=None):
    cfg = load_config(filename_config_file=filename_config_file)

    dal = DalBase(
        sql_username=cfg.sql_username,
        sql_password=cfg.sql_password,
        sql_host=cfg.sql_host,
        sql_port=cfg.sql_port,
        sql_db=cfg.sql_db,
        sql_engine_echo=cfg.logger_level == "DEBUG",
    )

    scoped_session = sqlalchemy.orm.scoped_session(dal.session_factory)

    api = create_api(
        cfg=cfg,
        schema=schema,
        scoped_session=scoped_session,
        logger_level=cfg.logger_level,
    )

    return api


# main sentinel
if __name__ == "__main__":

    argument_parser = argparse.ArgumentParser(
        description=("fightfor-graphql: GraphQL API over the SQLAlchemy ORM "
                     "serving the project data via Falcon.")
    )
    argument_parser.add_argument(
        "--config-file",
        dest="config_file",
        help="configuration file",
        required=False
    )
    arguments = argument_parser.parse_args()

    if arguments.config_file:
        _filename_config_file = arguments.config_file
    else:
        _filename_config_file = None

    main(filename_config_file=_filename_config_file)
