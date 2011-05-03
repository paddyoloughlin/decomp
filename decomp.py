#!/usr/bin/python
#
# decomp.py
# Decomposes a model into several different parts.

from collections import defaultdict

def read_model(filename):
    """Parses an .obj file format mesh.

    filename: Path to an obj format file with a mesh.
    returns: list of vertices, list of normals, list of faces

    Each vertices is a 3-tuple of floats giving the cartesian coordinates (x, y, z) of the vertex.
    Each normal is a 3 tuple of floats giving the direction of the normal it specifies.
    Each face is a list of 3-tuples. Each 3-tuple represents a point that defines the edges of the
     face. So triangles will have 3, quads will have 4 - len(face).
     The first element in each 3-tuple is the index of the vertex that defines that point.
     The second is the index of the texture coordinate of the point
        - Unused in this version. Is always None.
     The third is the index of the normal to the point in the normals list.
    """

    # Open the file and read it in.
    modelfile = open(filename)
    lines = modelfile.readlines()
    modelfile.close()
    del modelfile

    verts = []
    norms = []
    faces = []

    # Read the line from the file.
    for line in lines:
        # Split it by the whitespace
        words = line.split()

        if not words:
            continue

        if words[0] == "v":
            # Vertex
            # format: "v %{x}f %{y}f %{z}f
            x, y, z = float(words[1]), float(words[2]), float(words[3])
            verts.append((x, y, z))
        elif words[0] == "vn":
            # Vertex Normal
            # format: "vn %{x}f %{y}f %{z}f
            x, y, z = float(words[1]), float(words[2]), float(words[3])
            norms.append((x, y, z))
        elif words[0] == "vt":
            # Currently not handling texture coords
            pass
        elif words[0] == "f":
            # Face
            # format: "f node node node..."
            # node : "%{v}i" | "%{v}i//%{n}i" | "%{v}i/%{t}i | "%{v}i/%{t}i/%{n}i
            face = ()
            # Parse each vertex in the face, one at a time.
            for vert in words[1:]:
                if vert.find('//') != -1:
                    # A v//n node
                    v, n = map(lambda x: x - 1, vert.split('//'))
                    t = None
                else:
                    elems = vert.split('/')
                    if len(elems) == 1:
                        v = int(vert) - 1
                        n = t = None
                    elif len(elems) == 2:
                        v, t = int(elems[0]) - 1, int(elems[1]) - 1
                        n = None
                    elif len(elems) == 3:
                        v, t, n = int(elems[0]) - 1, int(elems[1]) - 1, int(elems[2]) - 1
                    else:
                        raise Exception, "Invalid face format: %s" % line

                # Append node to the face
                face = face + ((v, t, n),)

            if len(face) not in (3, 4):
                raise Exception, "Face bad number of sides encountered (%i): %s" % (len(face), line)

            # Add this face to the face list
            faces.append(face)
        else:
            # Some other kind of line. Ignore for now
            pass

    return verts, norms, faces


class Edge(object):
    """Class representing edge objects
    """

    def __init__(self, a, b, length):
        """Create an edge between vertex index a and vertex index b.

        Args:
            a: (int) index into an array of vertices. One endpoint of the edge.
            b: (int) the other endpoint of the edge. Like 'a', an index into an
                array of vertices.
            length: (numeric) euclidean length of the edge.
        """
        assert a != b, "Parameters must be different. Value=%s" % str(a)
        self.a = min(a, b)
        self.b = max(a, b)
        self.length = length

    def cmp_shortest_edge(self, other):
        """Compare two edges to determine which is smaller by euclidean length.

        Used to provide an ordering of edges. e.g. for a min-heap of edges by
        euclidean length.

        Args:
            other: (Edge) edge to compare this one with.
        """
        return self.length < other.length

    def cmp_longest_edge(self, other):
        """Compare two edges to determine which is longer by euclidean length.

        Used to provide an ordering of edges. e.g. for a max-heap of edges by
        euclidean length.

        Args:
            other: (Edge) edge to compare this one with.
        """
        return self.length > other.length

    def get_ends(self):
        """Get the ends of the edge as a tuple of vertex indices.

        Returns:
            a 2-tuple.
        """
        return (self.a, self.b)


class EdgeSpace(object):
    """A class to combine edges to list that their members index into and
    provide some geometry calculations for them.
    """
    def __init__(self, vertices):
        """Args:
        vertices: (list) sequence of vertices that the class will use for
        calculations.
        """
        self.vertices = vertices

    def calc_distance(self, vertexindex1, vertexindex2):
        """Determine the euclidean distance between two vertices.

        Args:
            vertexindex1: (int) index into self.vertices.
            vertexindex2: (int) index into self.vertices

        Returns:
            the euclidean distance between the vertices represented by
            vertexindex1 and vertexindex2 as a float.
        """
        v1 = self.vertices[vertexindex1]
        v2 = self.vertices[vertexindex2]

        x = v2[0] - v1[0]
        y = v2[1] - v1[1]
        z = v2[2] - v1[2]

        return ((x ** 2) + (y ** 2) + (z ** 2)) ** 0.5

    def create_mid(self, edge):
        """Create a vertex which lies on the mid-point of edge.

        Args:
            edge: (Edge) an edge object.

        Returns:
            the mid-point of the edge as a float 3-tuple.
        """
        v1 = self.vertices[edge.a]
        v2 = self.vertices[edge.b]

        x = (v1[0] + v2[0]) / 2
        y = (v1[1] + v2[0]) / 2
        z = (v1[2] + v2[0]) / 2

        return (x, y, z)

    def collapse_edge(self, edge):
        self.vertices.append(self.create_mid(edge))
        return len(self.vertices) - 1


def create_edges(faces, edgespace):
    """Create the data structures for use in skeletonisation.
    """
    edge_map = defaultdict(dict)
    edge_heap = HeapTree(cmp=Edge.cmp_shortest_edge)

    print "Creating edges:"

    for i, f in enumerate(faces):
        for p in range(len(f)):
            # Create the Edge.
            p1 = f[p - 1][0]
            p2 = f[p][0]
            edge = Edge(p1, p2, edgespace.calc_distance(p1, p2))

            # Add it to the heap.
            edge_node = edge_heap.add(edge)

            # Add the node to the map of vertices to edges.
            edge_map[p1][p2] = edge_node
            edge_map[p2][p1] = edge_node

        percent_done = int(i / len(f))
        if percent_done % 5 == 0:
            print "%i done"

    return edge_heap, edge_map


def skeletonise(edgespace, edge_heap, edge_map):
    removed_edges = []
    while len(edge_heap) > 0:
        skeletonise_step(edge_heap, edgespace, edge_map, removed_edgenodes)


def skeletonise_step(edge_heap, edgespace, edge_map, removed_edgenodes):
    # Remove the shortest edge.
    try:
        shortest = edge_heap.deleteroot()
    except IndexError:
        # Heap is empty, so leave the loop.
        return

    removed_edgenodes.append(shortest)

    # TODO: Remove connected faces and add to the ATL.
    # TODO: Ensure skeletal edges are removed from the heap and stored.
    # TODO: Removed duplicate edges from after the collapse.

    # Find the new point that this edge should be collapsed to and the index it
    # will be stored at.
    new_vert_index = edgespace.collapse_edge(shortest.value)

    # The edges that were connected to shortest are now connected to the new
    # vertex.
    # Also, remove the connections to the old vertices from the mapping.
    for i in shortest.value.get_ends():
        for j, edgeinfo in edge_map[i].items():
            # TODO: Figure out what to do here next!
            edge_map[new_vert_index][j] = edgeinfo
        del edge_map[i]

    # Remove shortest from the list of connections.
    del edge_map[new_vert_index][shortest]

    # Update each of the connected edges to use the new node instead of the old.
    for edgenode in connections[new_vert_index]:
        # TODO: Move edge that's connected to a vertex that's being deleted to
        # its replacement.
        edge_heap._bubbleup(edgenode)
        edge_heap._bubbledown(edgenode)


def main():
    # Read in the mesh from the file.
    verts, norms, faces = read_model("/home/paddy/dev/decomp/Models/cow-1500.obj")

    # We dont use the normals at the moment, so leave that out.
    del norms

    # Create edges.
    edgespace = EdgeSpace(verts)
    edge_heap, edge_map = create_edges(faces, edgespace)

    skeletonise(edgespace, edge_heap, edge_map)


if __name__ == '__main__':
    main()

