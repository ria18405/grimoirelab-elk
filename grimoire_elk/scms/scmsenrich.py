# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2020 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#   Ria Gupta <ria18405@iiitd.ac.in>
#

from grimoire_elk.enriched.enrich import Enrich
from grimoire_elk.elastic_mapping import Mapping as BaseMapping


class ScmsMapping(BaseMapping):

    @staticmethod
    def get_elastic_mappings(es_major):
        """Get Elasticsearch mapping.

        :param es_major: major version of Elasticsearch, as string
        :returns:        dictionary with a key, 'items', with the mapping
        """

        mapping = """
        {
            "properties": {
                 "context": {
                   "type": "text",
                   "fielddata": true,
                   "index": true
                 },
                 "body": {
                   "type": "text",
                   "index": true
                 },
                 "id": {
                    "type": "keyword"
                },
                "channel": {
                    "type": "keyword"
                }
           }
        } """

        return {"items": mapping}


class ScmsEnrich(Enrich):
    mapping = ScmsMapping

    def __init__(self, db_sortinghat='', db_projects_map=None, json_projects_map=None,
                 db_user='', db_password='', db_host=''):
        super().__init__(db_sortinghat, db_projects_map, json_projects_map,
                         db_user, db_password, db_host)
        self.studies = []
        self.studies.append(self.enrich_extra_data)