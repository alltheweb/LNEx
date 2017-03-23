"""
Copyright 2017 Hussein S. Al-Olimat, hussein@knoesis.org

This software is released under the GNU Affero General Public License (AGPL)
v3.0 License.
"""


from collections import defaultdict

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections

import geo_calculations
import gaz_augmentation_and_filtering

connection_string = ""
index_name = ""


def set_elasticindex_conn(cs, inn):
    global connection_string
    global index_name

    connection_string = cs
    index_name = inn


def search_index(bb):
    Elasticsearch()

    if connection_string == '' or index_name == '':

        print "\n###########################################################"
        print "Global ERROR: Elastic host and port or index name not defined"
        print "#############################################################\n"
        exit()

    if not geo_calculations.is_bb_acceptable(
            bb) or bb[0] > bb[2] or bb[1] > bb[3]:

        print "\n##########################################################"
        print "Global ERROR: Bounding Box is too big, choose a smaller one!"
        print "############################################################\n"
        exit()

    connections.create_connection(hosts=[connection_string], timeout=20)

    phrase_search = [Q({"filtered": {
        "filter": {
            "geo_bounding_box": {
                        "coordinate": {
                            "bottom_left": {
                                "lat": bb[0],
                                "lon": bb[1]
                            },
                            "top_right": {
                                "lat": bb[2],
                                "lon": bb[3]
                            }
                        }
                        }
        },
        "query": {
            "match_all": {}
        }
    }
    })]

    # to search with a scroll
    e_search = Search(index=index_name).query(Q('bool', must=phrase_search))

    try:
        res = e_search.scan()
    except BaseException:
        raise

    return res


def get_text(obj):

    keys = dir(obj)

    if len(keys) == 1:
        return obj[keys[0]]

    else:
        if "en" in keys:
            return obj["en"]
        elif "default" in keys:
            return obj["default"]
        elif "reg" in keys:
            return obj["reg"]
        elif "old" in keys:
            return obj["old"]
        elif "alt" in keys:
            return obj["alt"]
        elif "loc" in keys:
            return obj["loc"]
        elif "int" in keys:
            return obj["int"]
        else:
            try:
                return obj[keys[0]]
            except BaseException:
                return obj


def build_bb_gazetteer(bb, augment):

    # accepted fields as location names
    location_fields = ["city", "country",
                       "name", "state", "street"]

    geo_info = defaultdict()
    geo_locations = defaultdict(list)

    id = 0

    for match in search_index(bb):

        id += 1

        keys = dir(match)

        geo_item = defaultdict()

        if "coordinate" in keys:
            geo_item["point"] = match["coordinate"]
        if "extent" in keys:
            geo_item["extent"] = match["extent"]["coordinates"]

        #######################################################################

        for key in dir(match):

            if key in location_fields:

                try:
                    text = get_text(match[key])

                    if key == "name":
                        # mapping a location name to its geo-info
                        geo_locations[text].append(id)

                        geo_info[id] = {"name": text,
                                        "geo_item": list(geo_item)}

                    else:
                        geo_locations[text]

                except BaseException:
                    print "exception at record # ", count
                    print get_text(match[key])
                    raise

    if augment:
        # 'pullapuram road': set([493])
        new_geo_locations, extended_words3 = \
            gaz_augmentation_and_filtering.augment(geo_locations)

    else:
        new_geo_locations = gaz_augmentation_and_filtering.filter(geo_locations)
        extended_words3 = \
            gaz_augmentation_and_filtering.get_extended_words3(
                new_geo_locations.keys())

    return new_geo_locations, geo_info, extended_words3

##########################################################################


if __name__ == "__main__":

    chennai_bb = [12.74, 80.066986084,
                  13.2823848224, 80.3464508057]

    connection_string = '130.108.85.186:9200'
    index_name = "photon_v1"

    set_elasticindex_conn(connection_string, index_name)

    geo_locations, geo_info, extended_words3 = build_bb_gazetteer(chennai_bb)
