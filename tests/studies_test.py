# coding=utf-8

import unittest

from graphene.test import Client
import sqlalchemy.orm
from fform.dal_base import DalBase

from ffgraphql.config import import_config
from ffgraphql.schema import schema


class DemoTest(unittest.TestCase):

    def setUp(self):
        cfg = import_config(
            fname_config_file="/etc/fightfor-graphql/fightfor-graphql.json",
        )

        dal = DalBase(
            sql_username=cfg.sql_username,
            sql_password=cfg.sql_password,
            sql_host=cfg.sql_host,
            sql_port=cfg.sql_port,
            sql_db=cfg.sql_db,
            sql_engine_echo=cfg.logger_level == "DEBUG",
        )

        # Prepare a DB session.
        session_maker = sqlalchemy.orm.sessionmaker(bind=dal.engine)
        self.session = session_maker()

        # Prepare a Graphene client.
        self.client = Client(schema)

    def tearDown(self):
        self.session.close()

    #
    # def test_query_studies_search(self):
    #
    #     query = """
    #         query {
    #           studies{
    #             search(meshDescriptorIds: [3372]) {
    #               studyId
    #             }
    #           }
    #         }
    #     """
    #
    #     result_eval = self.client.execute(
    #         query, context_value={"session": self.session}
    #     )
    #
    #     # self.assertDictEqual(result_refr, result_eval)
    #

    # def test_sth(self):
    #
    #     query = """
    #         query getStats($studyIds: [Int]!){
    #           studiesStats {
    #             countStudiesByFacility(studyIds: $studyIds) {
    #               facility {
    #                 name,
    #                 city,
    #                 state,
    #                 country
    #               },
    #               countStudies
    #             }
    #           }
    #         }
    #     """
    #
    #     result_eval = self.client.execute(
    #         query,
    #         context_value={"session": self.session},
    #         variable_values={
    #             "studyIds": [115251, 115525, 115791, 115847]
    #         }
    #     )
    #
    # def test_sth(self):
    #
    #     query = """
    #         query filterStudies($studyIds: [Int]!){
    #           studies {
    #             filter(
    #               studyIds: $studyIds,
    #               filters: [
    #                 {
    #                   field: "org_study_id",
    #                   operator: EQ,
    #                   value: "CUC10-BNE01"
    #                 }
    #               ]
    #             ) {
    #               studyId
    #             }
    #           }
    #         }
    #     """
    #
    #     result_eval = self.client.execute(
    #         query,
    #         context_value={"session": self.session},
    #         variable_values={
    #             "studyIds": [115251, 115525, 115791, 115847]
    #         }
    #     )

    def test_sth(self):
        query = """
            query filterStudies(
                $studyIds: [Int]!,
                $cities: [String]
            ) {
                studies {
                    filter(
                        studyIds: $studyIds,
                        cities: $cities
                    ) {
                        studyId,
                        briefTitle,
                        locations {
                            locationId,
                            facility {
                                name,
                                city,
                                state,
                                country
                            }
                        },
                        interventions {
                            interventionType,
                            name
                        }
                    }
                }
            }
        """

        result_eval = self.client.execute(
            query,
            context_value={"session": self.session},
            variable_values={
                "studyIds": [
                    1,
                    8,
                    10,
                    11,
                    12,
                    13
                ],
                "cities": [
                    "Minneapolis",
                    "Burlington"
                ]
            }
        )

        # from IPython import embed
        # embed()
