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

class Edge:
    """Class representing edge objects
    """
    def __init__(self, a, b, vertices):
        self.__a = min(a, b)
        self.__b = max(a, b)
        self.__length = self.calc_length()
        self.__vertices = vertices
        self.connecting_faces = set()

    def __cmp__(self, other):
        if self.__length < other.__length:
            return -1
        elif self.__length == other.__length:
            return 0
        else:
            return 1

    def get_length(self):
        return self.__length

    def get_ends(self):
        return (self.__a, self.__b)

    def calc_length(self):
        """Determine the euclidean length of this edge.
        """
        v1 = self.__vertices[self.a]
        v2 = self.__vertices[self.b]

        x = v2[0] - v1[0]
        y = v2[1] - v1[1]
        z = v2[2] - v1[2]

        return ((x ** 2) + (y ** 2) + (z ** 2)) ** 0.5

    def create_mid(self):
        """Create a vertex which lies on the mid-point of this edge.
        """
        v1 = self.__vertices[self.a]
        v2 = self.__vertices[self.b]

        x = (v1[0] + v2[0]) / 2
        y = (v1[1] + v2[0]) / 2
        z = (v1[2] + v2[0]) / 2

        return (x, y, z)

def create_edges(faces, verts):
    """Create the data structures for use in skeletonisation.
    """
    vert2edgenode = defaultdict(set)
    edge_heap = HeapTree()

    print "Creating edges:"

    for i, f in enumerate(faces):
        for p in range(len(f)):
            # Create the Edge.
            p1 = f[p - 1][0]
            p2 = f[p][0]
            edge = Edge(p1, p2, verts)

            # Add it to the heap.
            edge_node = edge_heap.add(edge)

            # Add the node to the map of vertices to edges.
            vert2edgenode[p1].add(edge_node)
            vert2edgenode[p2].add(edge_node)

            # Map this edge to the face it is connected to
            edge.connecting_faces.add(f)

        percent_done = int(i / len(f))
        if percent_done % 5 == 0:
            print "%i done"

    return edge_heap, vert2edgenode

def skeletonise(verts, edge_heap, connections):
    removed_edges = []
    while len(edge_heap) > 0:
        skeletonise_step(edge_heap, verts, connections, removed_edgenodes)


def skeletonise_step(edge_heap, verts, connections, removed_edgenodess)
    # Remove the shortest edge.
    try:
        shortest = edge_heap.deleteroot()
    except IndexError:
        # Heap is empty, so leave the loop.
        break

    removed_edgenodes.append(shortest)

    # Find the new point that this edge should be collapsed to and the index it
    # will be stored at.
    new_vert_index = len(verts)
    verts.append(shortest.value.create_mid())

    # The edges that were connected to shortest are now connected to the new
    # vertex.
    # Also, remove the connections to the old vertices from the mapping.
    for i in shortest.value.get_ends():
        connections[new_vert_index].add(connections[i])
        del connections[i]

    # Remove shortest from the list of connections.
    connections[new_vert_index].remove(shortest)

    # Update each of the connected edges to use the new node instead of the old.
    for edgenode in connections[new_vert_index]:
        edgenode.value.move(shortest.value, new_vert_index)
        edge_heap._bubbledown(edgenode)
        edge_heap._bubbleup(edgenode)


def main():
    # Read in the mesh from the file.
    verts, norms, faces = read_model("/home/paddy/dev/decomp/Models/cow-1500.obj")

    # We dont use the normals at the moment, so leave that out.
    del norms

    # Create edges.
    edge_heap, connections = create_edges(faces, verts)

    skeletonise(verts, edge_heap, connections)

if __name__ == '__main__':
    main()

