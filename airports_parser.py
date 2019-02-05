#!/usr/bin/env python

import osmium
import shapely.wkb as wkblib
import argparse
from shapely.geometry import Point, Polygon

class AerowayNodesHandler(osmium.SimpleHandler):
    BUFFER_DISTANCE = 0.00005
    
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.num_nodes = 0
        self.line = 0
        self.coordinates = []
        self.geoms = []
        self.envelope = False
        self.minimum_rotated_rectangle = False
        self.wkbfab = osmium.geom.WKBFactory()
        
    def get_nodes_in_area(self, buffer_const):
        intersected_node_ids = []
        for m in self.geoms:
            buffered_rectangle = m.minimum_rotated_rectangle.buffer(buffer_const)
            for n_id in range(0, len(self.coordinates)):
                n = self.coordinates[n_id]
                if buffered_rectangle.contains(Point(n[1], n[0])):
                    intersected_node_ids.append(n_id)
        return intersected_node_ids
    
    def export(self, filename):
        with open ("{}_nodes.txt".format(filename), "wb") as fp:
            intersected_node_ids = self.get_nodes_in_area(
                                        self.BUFFER_DISTANCE
                                    )
            for node_id in range(0, len(self.coordinates)):
                if node_id not in intersected_node_ids:
                    node = self.coordinates[node_id]
                    fp.write("{},{}\n".format(node[0],node[1])\
                             .encode('utf-8'))
        with open ("{}_areas.txt".format(filename), "wb") as fp:
            for area in self.geoms:
                for geom in area.geoms:
                    exported_geom = geom
                    if self.envelope:
                        exported_geom = geom.envelope
                    elif self.minimum_rotated_rectangle:
                        exported_geom = geom.minimum_rotated_rectangle
                    line = b''
                    for coord in list(exported_geom.exterior.coords):
                        line += "{},{}".format(coord[1],coord[0])\
                             .encode('utf-8')
                    line += b'\n'
                    fp.write(line)

    # https://wiki.openstreetmap.org/wiki/Aeroways
    def is_aeroway_airport(self, tags):
        if 'aeroway' in tags:
            if tags['aeroway'] == "aerodrome":
                return True
        return False

    def parse_node(self, n):
        tags = n.tags
        if self.is_aeroway_airport(tags):
            self.coordinates.append((n.location.lat, n.location.lon))
    
    def parse_area(self, a):
        geom = self.wkbfab.create_multipolygon(a)
        multipolyfon = wkblib.loads(geom, hex=True)
        self.geoms.append(multipolyfon)
                    
    def node(self, n):
        if self.is_aeroway_airport(n.tags):
            self.parse_node(n)

    # area also deals with the ways
    def area(self, a):
        if self.is_aeroway_airport(a.tags):
            self.parse_area(a)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This script accepts name of\
     the file to parse and exports extracted into the corresponding file.')

    parser.add_argument("-v", "--verbose",
                        help="increase output verbosity",
                        action="store_true")

    parser.add_argument('-i', "--input-file",
                        help="File to load OSM-formatted data from.", 
                        required=True)
    
    parser.add_argument('-e', "--envelope",
                        help="Outputs smallest rectangular polygon (with sides parallel to the\
 coordinate axes) that contains the object.", 
                        required=False)

    parser.add_argument('-m', "--minimum-rotated-rectangle",
                        help="Outputs general minimum bounding rectangle that contains the\
 object. Unlike envelope this rectangle is not constrained to be parallel to the coordinate\
 axes. If the convex hull of the object is a degenerate (line or point) this degenerate is\
 returned.", 
                        required=False)
    
    parser.add_argument('-o', "--output-id",
                        help="Meaningful filename part to export data to.\
                        $OUTPUT_ID_area.txt and $OUTPUT_ID_node.txt files\
                         will be created.",
                        required=True)

    args = parser.parse_args()

    if args.verbose:
        print("Parsing {} to export airports to {}_nodes.txt and\
 {}_areas.txt.".format(
            args.input_file, 
            args.output_id, 
            args.output_id))

    h = AerowayNodesHandler()

    if args.envelope and args.minimum_rotated_rectangle:
        args.envelope = False

    h.envelope = args.envelope
    h.minimum_rotated_rectangle = args.minimum_rotated_rectangle

    h.apply_file("{}".format(args.input_file), locations=True, 
                                                    idx='flex_mem')

    if args.verbose:
        print("Number of nodes: %d\nNumber of areas: %d" %
         (len(h.coordinates), len(h.geoms)))

    h.export("{}".format(args.output_id))

    if args.verbose:
        print("Export finished")
