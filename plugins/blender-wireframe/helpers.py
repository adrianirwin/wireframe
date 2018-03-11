#
#   helpers.py
#
#   Commonly used functions that perform mundane manipulation and
#   management tasks.
#


#
#   Imports
#

import bmesh


#
#   BMesh Functions
#

def object_to_bmesh(object):
    bm = bmesh.new()
    bm.from_mesh(object.data)
    bm.faces.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    return bm

def bmesh_to_object(bm, object):
    bm.to_mesh(object.data)
    bm.free()
    object.data.update()

def list_geometry(bm):
    return {"faces": list(bm.faces), "edges": list(bm.edges), "verts": list(bm.verts)}

#
#   Geometry Functions
#

#   Walk around the vert to find the next sharp edge on the 'fan' of faces
def find_next_sharp_edge(previous_face, previous_edge, vert, depth):
    #   TODO: This recursion depth limiter is currently arbitrary
    if depth < 10:
        for current_face in previous_edge.link_faces:
            if current_face is not previous_face:
                for current_edge in current_face.edges:
                    if current_edge is not previous_edge:
                        if current_edge.verts[0] is vert or current_edge.verts[1] is vert:
                            if current_edge.smooth is False:
                                new_vert = None
                                if current_edge.verts[0] is vert:
                                    new_vert = current_edge.verts[1]
                                else:
                                    new_vert = current_edge.verts[0]
                                return {"edge": current_edge, "vert": new_vert}
                            return find_next_sharp_edge(current_face, current_edge, vert, (depth + 1))
    return False


#
#   Metadata Functions
#

def vertex_groups_lock(object, groups, lock=True):
    for group in groups:
        object.vertex_groups[group].lock_weight = lock


#
#   __main__ Check
#

if __name__ == "__main__":
    print("helpers.py is not intended to be run as __main__")