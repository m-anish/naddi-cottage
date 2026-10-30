"""Blender (bpy) scene for the dome-extension washroom.

usage: python3 scene.py <palette:p1|p2> <view:v1|v2|cut|line_cut|line_v1> <out.png> [samples] [width] [height]
"""
import sys, math, random
import bpy, bmesh
from mathutils import Vector, Matrix
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geom import *

M = 0.3048  # ft -> m


def V(x, y, z):
    return Vector((x * M, y * M, z * M))


ROOM_C = V(0, 4.0, 3.5)
LOWCOST = False
FRONT_LEDGE_Y = front_y(LEDGE_H)

# ------------------------------------------------------------------ utils
def clip_poly(poly, f):
    """Sutherland-Hodgman clip of 3D polygon (list of Vector) keeping f(p) >= 0"""
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        fa, fb = f(a), f(b)
        if fa >= 0:
            out.append(a)
        if (fa >= 0) != (fb >= 0):
            t = fa / (fa - fb)
            out.append(a + (b - a) * t)
    return out


# interior half-spaces in feet coords (p in metres -> convert)
def hs_right(p):
    x, y, z = p.x / M, p.y / M, p.z / M
    return A * (FW / 2 - x) - C * y - z


def hs_left(p):
    x, y, z = p.x / M, p.y / M, p.z / M
    return A * (FW / 2 + x) - C * y - z


def hs_front(p):
    return p.y / M - T15 * p.z / M


def hs_back(p):
    return D + T15 * p.z / M - p.y / M


def clip_inside(poly, eps=0.0):
    for f in (hs_right, hs_left, hs_front, hs_back):
        poly = clip_poly(poly, lambda p, f=f: f(p) + eps)
        if len(poly) < 3:
            return poly
    return poly


def face_normal(poly):
    n = Vector((0, 0, 0))
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        n.x += (a.y - b.y) * (a.z + b.z)
        n.y += (a.z - b.z) * (a.x + b.x)
        n.z += (a.x - b.x) * (a.y + b.y)
    return n.normalized() if n.length > 0 else n


def orient_in(poly, target=None):
    target = target or ROOM_C
    c = sum(poly, Vector()) / len(poly)
    if face_normal(poly).dot(target - c) < 0:
        poly = list(reversed(poly))
    return poly


COLL = None


def add_obj(name, verts, faces, mat=None, mats=None, smooth=False, coll=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    (coll or COLL).objects.link(ob)
    if mats:
        for m in mats:
            me.materials.append(m)
    elif mat:
        me.materials.append(mat)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    planar_uv(ob)
    return ob


def poly_obj(name, poly, mat, thick=0.0, rim_mat=None, coll=None):
    ob = add_obj(name, poly, [list(range(len(poly)))], mat, coll=coll)
    if thick:
        sm = ob.modifiers.new("solid", "SOLIDIFY")
        sm.thickness = thick
        sm.offset = -1.0
        sm.use_even_offset = True
        if rim_mat:
            ob.data.materials.append(rim_mat)
            sm.material_offset_rim = 1
            sm.material_offset = 0
    return ob


def planar_uv(ob):
    me = ob.data
    if not me.polygons:
        return
    uv = me.uv_layers.new(name="UV")
    for p in me.polygons:
        n = p.normal
        if abs(n.z) > 0.95:
            e1 = Vector((1, 0, 0))
        else:
            e1 = n.cross(Vector((0, 0, 1))).normalized()
        e2 = n.cross(e1).normalized()
        if e2.z < 0:
            e2 = -e2
        for li in p.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = (co.dot(e1), co.dot(e2))


def box(name, cmin, cmax, mat, bevel=0.0, coll=None):
    x0, y0, z0 = cmin
    x1, y1, z1 = cmax
    vs = [V(x0, y0, z0), V(x1, y0, z0), V(x1, y1, z0), V(x0, y1, z0),
          V(x0, y0, z1), V(x1, y0, z1), V(x1, y1, z1), V(x0, y1, z1)]
    fs = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    ob = add_obj(name, vs, fs, mat, coll=coll)
    if bevel:
        b = ob.modifiers.new("bev", "BEVEL")
        b.width = bevel * M
        b.segments = 3
        b.limit_method = "ANGLE"
    return ob


def prism(name, ring0, ring1, mat, coll=None, bevel=0.0):
    """two equal-length rings of Vectors -> closed solid"""
    n = len(ring0)
    vs = list(ring0) + list(ring1)
    fs = [list(range(n))[::-1], list(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        fs.append([i, j, n + j, n + i])
    ob = add_obj(name, vs, fs, mat, coll=coll)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.uv_layers.remove(ob.data.uv_layers[0])
    planar_uv(ob)
    if bevel:
        b = ob.modifiers.new("bev", "BEVEL")
        b.width = bevel * M
        b.segments = 3
        b.limit_method = "ANGLE"
    return ob


def cyl(name, p0, p1, r, mat, seg=24, coll=None, cap=True):
    p0, p1 = Vector(p0), Vector(p1)
    ax = (p1 - p0)
    L = ax.length
    q = ax.normalized().to_track_quat("Z", "Y")
    vs, fs = [], []
    for k, base in enumerate((0, L)):
        for i in range(seg):
            a = 2 * math.pi * i / seg
            vs.append(p0 + q @ Vector((r * math.cos(a), r * math.sin(a), base)))
    for i in range(seg):
        j = (i + 1) % seg
        fs.append([i, j, seg + j, seg + i])
    if cap:
        fs.append(list(range(seg))[::-1])
        fs.append(list(range(seg, 2 * seg)))
    return add_obj(name, vs, fs, mat, smooth=True, coll=coll)


def set_smooth_mod(ob):
    try:
        ob.data.set_sharp_from_angle(angle=math.radians(35))
    except Exception:
        pass


# ------------------------------------------------------------------ materials
def nodes_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    return m, nt, bsdf


def inp(bsdf, *names):
    for n in names:
        if n in bsdf.inputs:
            return bsdf.inputs[n]
    raise KeyError(names)


def simple(name, col, rough=0.5, metal=0.0, coat=0.0, spec=0.5):
    m, nt, b = nodes_mat(name)
    inp(b, "Base Color").default_value = (*col, 1)
    inp(b, "Roughness").default_value = rough
    inp(b, "Metallic").default_value = metal
    if coat:
        inp(b, "Coat Weight", "Coat").default_value = coat
        inp(b, "Coat Roughness").default_value = 0.05
    return m


def tex_coord(nt, kind="UV"):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    return tc.outputs[kind]


def noise(nt, vec, scale, detail=6, rough=0.55, dim="3D"):
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail
    n.inputs["Roughness"].default_value = rough
    nt.links.new(vec, n.inputs["Vector"])
    return n


def mixc(nt, fac, c1, c2):
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    nt.links.new(fac, mx.inputs[0])
    for i, c in ((6, c1), (7, c2)):
        if isinstance(c, tuple):
            mx.inputs[i].default_value = (*c, 1)
        else:
            nt.links.new(c, mx.inputs[i])
    return mx.outputs[2]


def ramp(nt, fac, stops):
    r = nt.nodes.new("ShaderNodeValToRGB")
    nt.links.new(fac, r.inputs[0])
    els = r.color_ramp.elements
    els[0].position, els[0].color = stops[0][0], (*stops[0][1], 1)
    els[1].position, els[1].color = stops[-1][0], (*stops[-1][1], 1)
    for pos, col in stops[1:-1]:
        e = els.new(pos)
        e.color = (*col, 1)
    return r.outputs[0]


def bump(nt, b, height, strength=0.2, dist=0.002):
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = strength
    bp.inputs["Distance"].default_value = dist
    nt.links.new(height, bp.inputs["Height"])
    nt.links.new(bp.outputs[0], inp(b, "Normal"))
    return bp


def plaster(name, col, col2, rough=0.8, scale=1.6, bump_s=0.08):
    m, nt, b = nodes_mat(name)
    co = tex_coord(nt, "Object")
    n1 = noise(nt, co, scale, 5, 0.6)
    n2 = noise(nt, co, scale * 9, 8, 0.65)
    f = nt.nodes.new("ShaderNodeMath")
    f.operation = "MULTIPLY_ADD"
    nt.links.new(n1.outputs[0], f.inputs[0])
    f.inputs[1].default_value = 0.8
    nt.links.new(n2.outputs[0], f.inputs[2])
    rr = ramp(nt, n1.outputs[0], [(0.35, col2), (0.65, col)])
    nt.links.new(rr, inp(b, "Base Color"))
    inp(b, "Roughness").default_value = rough
    bump(nt, b, n2.outputs[0], bump_s, 0.003)
    return m


def tiles(name, c1, c2, grout, tile_w_ft, tile_h_ft, offset=0.5, rough=0.55, gap_in=0.12,
          cleft=0.25, grout_rough=0.9, noise_scale=6.0, coord="UV", tone_var=0.6, gloss_var=0.0):
    m, nt, b = nodes_mat(name)
    co = tex_coord(nt, coord)
    br = nt.nodes.new("ShaderNodeTexBrick")
    W = tile_w_ft * M
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = W
    br.inputs["Row Height"].default_value = tile_h_ft * M
    br.inputs["Mortar Size"].default_value = gap_in / 12 * M
    br.inputs["Mortar Smooth"].default_value = 0.2
    br.offset = offset
    br.offset_frequency = 2
    br.inputs["Bias"].default_value = 0.0
    br.inputs["Color1"].default_value = (*c1, 1)
    br.inputs["Color2"].default_value = (*c2, 1)
    br.inputs["Mortar"].default_value = (*grout, 1)
    nt.links.new(co, br.inputs["Vector"])
    nz = noise(nt, co, noise_scale, 10, 0.62)
    col = mixc(nt, nz.outputs[0], br.outputs["Color"], br.outputs["Color"])
    # darken/lighten with noise
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "OVERLAY"
    mul.inputs[0].default_value = tone_var
    nt.links.new(br.outputs["Color"], mul.inputs[6])
    nt.links.new(nz.outputs[0], mul.inputs[7])
    nt.links.new(mul.outputs[2], inp(b, "Base Color"))
    # roughness: tiles vs grout
    rmix = nt.nodes.new("ShaderNodeMix")
    rmix.data_type = "FLOAT"
    nt.links.new(br.outputs["Fac"], rmix.inputs[0])
    rmix.inputs[2].default_value = rough
    rmix.inputs[3].default_value = grout_rough
    nt.links.new(rmix.outputs[0], inp(b, "Roughness"))
    # bump: grout recess + cleft noise
    hb = nt.nodes.new("ShaderNodeMath")
    hb.operation = "MULTIPLY_ADD"
    nt.links.new(nz.outputs[0], hb.inputs[0])
    hb.inputs[1].default_value = cleft
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    nt.links.new(br.outputs["Fac"], inv.inputs[1])
    nt.links.new(inv.outputs[0], hb.inputs[2])
    bump(nt, b, hb.outputs[0], 0.35, 0.004)
    return m


def wood(name, c_light, c_dark, rough=0.45, scale=4.0, along="X"):
    m, nt, b = nodes_mat(name)
    co = tex_coord(nt, "Object")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 22.0, 1.0) if along == "X" else (22.0, 1.0, 1.0)
    if along == "Z":
        mp.inputs["Scale"].default_value = (22.0, 22.0, 1.0)
    nt.links.new(co, mp.inputs["Vector"])
    nz = noise(nt, mp.outputs[0], scale, 6, 0.6)
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.inputs["Scale"].default_value = 3.0
    wv.inputs["Distortion"].default_value = 2.5
    wv.inputs["Detail"].default_value = 3.0
    nt.links.new(mp.outputs[0], wv.inputs["Vector"])
    f = nt.nodes.new("ShaderNodeMix")
    f.data_type = "FLOAT"
    f.inputs[0].default_value = 0.45
    nt.links.new(wv.outputs["Fac"], f.inputs[2])
    nt.links.new(nz.outputs[0], f.inputs[3])
    col = ramp(nt, f.outputs[0], [(0.2, c_dark), (0.55, c_light), (0.9, c_dark)])
    nt.links.new(col, inp(b, "Base Color"))
    inp(b, "Roughness").default_value = rough
    bump(nt, b, wv.outputs["Fac"], 0.05, 0.001)
    return m


def planks(name, c1, c2, plank_w_ft, plank_l_ft, gap_in=0.06, rough=0.55):
    """wood-look boards (WPC) laid along level lines"""
    m, nt, b = nodes_mat(name)
    co = tex_coord(nt, "UV")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = plank_l_ft * M
    br.inputs["Row Height"].default_value = plank_w_ft * M
    br.inputs["Mortar Size"].default_value = gap_in / 12 * M
    br.offset = 0.37
    br.inputs["Color1"].default_value = (*c1, 1)
    br.inputs["Color2"].default_value = (*c2, 1)
    br.inputs["Mortar"].default_value = (0.08, 0.06, 0.05, 1)
    nt.links.new(co, br.inputs["Vector"])
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 30.0, 1.0)
    nt.links.new(co, mp.inputs["Vector"])
    nz = noise(nt, mp.outputs[0], 3.0, 8, 0.6)
    ov = nt.nodes.new("ShaderNodeMix")
    ov.data_type = "RGBA"
    ov.blend_type = "OVERLAY"
    ov.inputs[0].default_value = 0.35
    nt.links.new(br.outputs["Color"], ov.inputs[6])
    nt.links.new(nz.outputs[0], ov.inputs[7])
    nt.links.new(ov.outputs[2], inp(b, "Base Color"))
    inp(b, "Roughness").default_value = rough
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    nt.links.new(br.outputs["Fac"], inv.inputs[1])
    bump(nt, b, inv.outputs[0], 0.3, 0.003)
    return m


def glass_mat(name, tint=(0.92, 0.97, 0.96), rough=0.0, frosted=False):
    m, nt, b = nodes_mat(name)
    inp(b, "Base Color").default_value = (*tint, 1)
    inp(b, "Transmission Weight", "Transmission").default_value = 1.0
    inp(b, "Roughness").default_value = 0.35 if frosted else rough
    inp(b, "IOR").default_value = 1.45
    # shadow-ray transparency trick so light passes through
    out = [n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"][0]
    lp = nt.nodes.new("ShaderNodeLightPath")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    tr.inputs[0].default_value = (*tint, 1)
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Shadow Ray"], mx.inputs[0])
    nt.links.new(b.outputs[0], mx.inputs[1])
    nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    return m


def emit_mat(name, col, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*col, 1)
    em.inputs[1].default_value = strength
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def towel_mat(name, col):
    m, nt, b = nodes_mat(name)
    co = tex_coord(nt, "Object")
    nz = noise(nt, co, 180.0, 2, 0.5)
    rr = ramp(nt, nz.outputs[0], [(0.3, tuple(c * 0.82 for c in col)), (0.7, col)])
    nt.links.new(rr, inp(b, "Base Color"))
    inp(b, "Roughness").default_value = 0.95
    try:
        inp(b, "Sheen Weight").default_value = 0.6
    except KeyError:
        pass
    bump(nt, b, nz.outputs[0], 0.4, 0.002)
    return m


def fabric_mat(name, col):
    m, nt, b = nodes_mat(name)
    co = tex_coord(nt, "Object")
    nz = noise(nt, co, 260.0, 3, 0.5)
    rr = ramp(nt, nz.outputs[0], [(0.3, tuple(c * 0.9 for c in col)), (0.7, col)])
    nt.links.new(rr, inp(b, "Base Color"))
    inp(b, "Roughness").default_value = 0.9
    try:
        inp(b, "Sheen Weight").default_value = 0.4
        inp(b, "Transmission Weight").default_value = 0.0
    except KeyError:
        pass
    try:
        inp(b, "Subsurface Weight").default_value = 0.15
    except KeyError:
        pass
    bump(nt, b, nz.outputs[0], 0.12, 0.001)
    return m


def palette(p):
    P = {}
    P["poche"] = simple("poche", (0.11, 0.105, 0.1), 0.9)
    P["ceramic"] = simple("ceramic", (0.88, 0.88, 0.86), 0.06, coat=0.6)
    P["mirror"] = simple("mirror", (0.93, 0.94, 0.94), 0.015, metal=1.0)
    P["glass"] = glass_mat("glass", (0.97, 0.99, 0.985))
    P["frosted"] = glass_mat("frosted", (0.95, 0.97, 0.97), frosted=True)
    P["upvc"] = simple("upvc", (0.86, 0.86, 0.84), 0.35)
    P["steel"] = simple("steel", (0.75, 0.75, 0.74), 0.25, metal=1.0)
    P["ext"] = plaster("ext", (0.78, 0.76, 0.72), (0.7, 0.68, 0.64), 0.85)
    P["leaf"] = simple("leaf", (0.06, 0.2, 0.07), 0.45)
    P["pot"] = plaster("pot", (0.55, 0.36, 0.25), (0.45, 0.28, 0.2), 0.8, 8)
    P["yellow"] = simple("yellow", (0.75, 0.55, 0.08), 0.5)
    P["ground"] = plaster("ground", (0.2, 0.25, 0.12), (0.16, 0.2, 0.1), 0.95, 0.6)
    if p == "p1":
        P["floor"] = tiles("slate_floor", (0.065, 0.072, 0.068), (0.105, 0.112, 0.104), (0.17, 0.17, 0.16), 2.0, 1.0,
                           offset=0.5, rough=0.5, gap_in=0.14, cleft=0.55, noise_scale=7, coord="UV", tone_var=0.55)
        P["shower_floor"] = tiles("slate_shower", (0.065, 0.072, 0.068), (0.1, 0.108, 0.1), (0.17, 0.17, 0.16), 0.5, 0.5,
                                  offset=0.0, rough=0.45, gap_in=0.16, cleft=0.55, noise_scale=9, coord="UV", tone_var=0.55)
        P["wall_dry"] = plaster("lime_dry", (0.86, 0.83, 0.77), (0.8, 0.76, 0.7), 0.82, 1.4, 0.05)
        P["wall_wet"] = plaster("micro_wet", (0.62, 0.6, 0.56), (0.54, 0.52, 0.48), 0.42, 1.8, 0.04)
        P["back_wet"] = tiles("slate_wall", (0.14, 0.15, 0.145), (0.2, 0.21, 0.2), (0.24, 0.24, 0.23), 1.0, 0.25,
                              offset=0.5, rough=0.45, gap_in=0.08, cleft=0.45, noise_scale=8, tone_var=0.6)
        P["ledge_face"] = P["wall_dry"]
        P["ledge_face_wet"] = P["wall_wet"]
        P["ledge_top"] = tiles("slate_slab", (0.11, 0.12, 0.115), (0.13, 0.14, 0.135), (0.11, 0.12, 0.115), 8.0, 4.0,
                               offset=0.0, rough=0.38, gap_in=0.0, cleft=0.15, noise_scale=5, tone_var=0.5)
        P["counter"] = P["ledge_top"]
        P["metal"] = simple("brass", (0.8, 0.6, 0.34), 0.28, metal=1.0)
        P["wood"] = wood("deodar", (0.62, 0.42, 0.24), (0.42, 0.26, 0.13), 0.45)
        P["door"] = wood("deodar_door", (0.6, 0.41, 0.23), (0.43, 0.27, 0.14), 0.72, along="Z")
        P["trim"] = P["wood"]
        P["towel"] = towel_mat("towel", (0.78, 0.72, 0.62))
        P["towel2"] = towel_mat("towel2", (0.42, 0.45, 0.38))
        P["cabinet"] = P["wood"]
    elif p == "p3":
        kota1, kota2 = (0.13, 0.165, 0.155), (0.165, 0.2, 0.19)
        P["floor"] = tiles("kota_floor", kota1, kota2, (0.15, 0.17, 0.16), 2.0, 2.0,
                           offset=0.0, rough=0.62, gap_in=0.07, cleft=0.18, noise_scale=6, coord="UV", tone_var=0.6)
        P["shower_floor"] = tiles("kota_shower", kota1, kota2, (0.15, 0.17, 0.16), 1.0, 1.0,
                                  offset=0.0, rough=0.66, gap_in=0.08, cleft=0.2, noise_scale=7, coord="UV", tone_var=0.6)
        P["wall_dry"] = plaster("whitewash", (0.85, 0.82, 0.76), (0.8, 0.77, 0.71), 0.88, 1.3, 0.06)
        P["wall_wet"] = tiles("ceramic_6x6", (0.79, 0.77, 0.71), (0.76, 0.74, 0.68), (0.6, 0.59, 0.56), 0.5, 0.5,
                              offset=0.0, rough=0.3, gap_in=0.1, cleft=0.02, noise_scale=10, tone_var=0.12)
        P["back_wet"] = P["wall_wet"]
        P["ledge_face"] = P["wall_wet"]
        P["ledge_face_wet"] = P["wall_wet"]
        P["ledge_top"] = tiles("kota_slab", (0.15, 0.19, 0.18), (0.18, 0.215, 0.205), (0.15, 0.19, 0.18), 8.0, 4.0,
                               offset=0.0, rough=0.42, gap_in=0.0, cleft=0.1, noise_scale=5, tone_var=0.55)
        P["counter"] = P["ledge_top"]
        P["metal"] = simple("chrome", (0.9, 0.9, 0.9), 0.1, metal=1.0)
        P["wood"] = wood("pine", (0.74, 0.55, 0.34), (0.58, 0.4, 0.22), 0.55)
        P["door"] = simple("sage_door", (0.2, 0.27, 0.19), 0.62)
        P["trim"] = P["wood"]
        P["towel"] = towel_mat("towel", (0.72, 0.66, 0.55))
        P["towel2"] = towel_mat("towel2", (0.33, 0.4, 0.31))
        P["cabinet"] = P["ledge_top"]
        P["curtain"] = fabric_mat("curtain", (0.74, 0.7, 0.62))
        P["head_r"] = 0.33
    else:
        P["floor"] = tiles("porcelain", (0.66, 0.65, 0.63), (0.7, 0.69, 0.67), (0.55, 0.55, 0.53), 2.0, 2.0,
                           offset=0.0, rough=0.5, gap_in=0.1, cleft=0.05, noise_scale=40, coord="UV", tone_var=0.25)
        P["shower_floor"] = tiles("porcelain_sm", (0.64, 0.63, 0.61), (0.68, 0.67, 0.65), (0.55, 0.55, 0.53), 0.33, 0.33,
                                  offset=0.0, rough=0.55, gap_in=0.1, cleft=0.05, noise_scale=40, coord="UV", tone_var=0.25)
        P["wall_dry"] = planks("wpc_oak", (0.62, 0.48, 0.33), (0.56, 0.42, 0.28), 0.5, 8.0)
        P["wall_wet"] = tiles("hpl_white", (0.88, 0.88, 0.86), (0.88, 0.88, 0.86), (0.6, 0.6, 0.58), 4.0, 8.0,
                              offset=0.0, rough=0.25, gap_in=0.12, cleft=0.0, noise_scale=3, tone_var=0.05)
        P["back_wet"] = tiles("subway_white", (0.86, 0.87, 0.86), (0.84, 0.85, 0.84), (0.72, 0.72, 0.7), 0.5, 0.25,
                              offset=0.5, rough=0.12, gap_in=0.08, cleft=0.03, noise_scale=12, tone_var=0.1)
        P["ledge_face"] = simple("hpl_face", (0.88, 0.88, 0.86), 0.3)
        P["ledge_face_wet"] = P["ledge_face"]
        P["ledge_top"] = tiles("kota", (0.34, 0.4, 0.38), (0.38, 0.43, 0.41), (0.34, 0.4, 0.38), 8.0, 4.0,
                               offset=0.0, rough=0.35, gap_in=0.0, cleft=0.1, noise_scale=5, tone_var=0.55)
        P["counter"] = P["ledge_top"]
        P["metal"] = simple("matte_black", (0.025, 0.025, 0.025), 0.42, metal=0.6)
        P["wood"] = wood("oak", (0.72, 0.57, 0.4), (0.58, 0.44, 0.3), 0.5)
        P["door"] = simple("white_door", (0.85, 0.85, 0.83), 0.68)
        P["trim"] = P["wood"]
        P["towel"] = towel_mat("towel", (0.86, 0.86, 0.84))
        P["towel2"] = towel_mat("towel2", (0.5, 0.58, 0.62))
        P["cabinet"] = simple("cab_white", (0.86, 0.86, 0.84), 0.45)
    return P


# ------------------------------------------------------------------ build
def build(P, cutaway=False):
    global COLL
    COLL = bpy.context.scene.collection
    T = 0.35  # wall assembly thickness (ft)

    # ---- floor (split dry / shower)
    fpoly = [V(-FW / 2, 0, 0), V(FW / 2, 0, 0), V(BW / 2, D, 0), V(-BW / 2, D, 0)]
    dry = clip_poly(fpoly, lambda p: GLASS_Y * M - p.y)
    wet = clip_poly(fpoly, lambda p: p.y - GLASS_Y * M)
    for nm, pl, mt in (("floor_dry", dry, P["floor"]), ("floor_wet", wet, P["shower_floor"])):
        pl = orient_in(pl, Vector((0, 1, 5)))
        poly_obj(nm, pl, mt, thick=0.33 * M, rim_mat=P["poche"])
    if LOWCOST:   # square trap, four-way falls
        box("drain", (-0.25, 5.85, 0.0), (0.25, 6.35, 0.012), P["steel"])
    else:         # linear drain
        box("drain", (-1.35, 6.62, 0.0), (1.35, 6.78, 0.012), P["steel"])

    # ---- side slopes (split at glass line)
    for sd, nm in ((1, "R"), (-1, "L")):
        if cutaway and sd == 1:
            continue
        quad = [V(sd * FW / 2, 0, 0), V(sd * BW / 2, D, 0), V(0, APEX_B[1], APEX_B[2]), V(0, APEX_F[1], APEX_F[2])]
        d_ = clip_poly(quad, lambda p: GLASS_Y * M - p.y)
        w_ = clip_poly(quad, lambda p: p.y - GLASS_Y * M)
        poly_obj("slope_dry_" + nm, orient_in(d_), P["wall_dry"], T * M, P["poche"])
        poly_obj("slope_wet_" + nm, orient_in(w_), P["wall_wet"], T * M, P["poche"])

    # ---- front wall with portal notch (in-plane coords u, v)
    def fw(u, v):
        return V(u, v * S15, v * C15)
    vh = DOOR_H / C15
    notch = [fw(-FW / 2, 0), fw(-DOOR_HW, 0), fw(-DOOR_HW, vh), fw(DOOR_HW, vh), fw(DOOR_HW, 0), fw(FW / 2, 0), fw(0, HF)]
    ob = poly_obj("front_wall", orient_in(notch), P["wall_dry"], T * M, P["poche"])
    py = front_y(DOOR_H)
    for sd in (-1, 1):
        cheek = [V(sd * DOOR_HW, 0, 0), V(sd * DOOR_HW, 0, DOOR_H), V(sd * DOOR_HW, py, DOOR_H)]
        poly_obj("cheek", orient_in(cheek, V(0, 0.5, 3)), P["wall_dry"], 0.1 * M)
    soffit = [V(-DOOR_HW, 0, DOOR_H), V(DOOR_HW, 0, DOOR_H), V(DOOR_HW, py, DOOR_H), V(-DOOR_HW, py, DOOR_H)]
    poly_obj("soffit", orient_in(soffit, V(0, 0.5, 3)), P["wall_dry"], 0.1 * M)
    # door + frame (closed, at y=0, inside face)
    box("door_leaf", (-DOOR_HW + 0.06, -0.15, 0.03), (DOOR_HW - 0.06, -0.02, DOOR_H - 0.06), P["door"], bevel=0.01)
    for sd in (-1, 1):
        box("jamb", (sd * DOOR_HW - (0.12 if sd > 0 else 0), -0.2, 0), (sd * DOOR_HW + (0.12 if sd < 0 else 0), 0.06, DOOR_H), P["trim"])
    box("head", (-DOOR_HW, -0.2, DOOR_H - 0.12), (DOOR_HW, 0.06, DOOR_H), P["trim"])
    # handle
    cyl("handle_rose", V(DOOR_HW - 0.35, -0.02, 3.4), V(DOOR_HW - 0.35, 0.03, 3.4), 0.1 * M, P["metal"])
    cyl("handle", V(DOOR_HW - 0.35, 0.05, 3.4), V(DOOR_HW - 0.85, 0.05, 3.4), 0.035 * M, P["metal"])
    cyl("handle_n", V(DOOR_HW - 0.35, 0.0, 3.4), V(DOOR_HW - 0.35, 0.06, 3.4), 0.035 * M, P["metal"])

    # ---- back wall with window hole
    def bw(u, v):
        return V(u, D + v * S15, v * C15)
    hw = lambda v: BW / 2 * (1 - v / HB)
    v0, v1 = WIN_V
    pieces = [
        [bw(-BW / 2, 0), bw(BW / 2, 0), bw(hw(v0), v0), bw(-hw(v0), v0)],
        [bw(-hw(v1), v1), bw(hw(v1), v1), bw(0, HB)],
        [bw(-hw(v0), v0), bw(-WIN_HW, v0), bw(-WIN_HW, v1), bw(-hw(v1), v1)],
        [bw(WIN_HW, v0), bw(hw(v0), v0), bw(hw(v1), v1), bw(WIN_HW, v1)],
    ]
    for i, pc in enumerate(pieces):
        poly_obj(f"back_{i}", orient_in(pc), P["back_wet"], T * M, P["poche"])
    # window frame + frosted glass + reveal
    fr = 0.12
    n_back = Vector((0, -C15, S15))  # inward normal of back wall (toward room)
    def bwo(u, v, o):
        return bw(u, v) - n_back * o * M
    ring_out = [bwo(-WIN_HW, v0, 0), bwo(WIN_HW, v0, 0), bwo(WIN_HW, v1, 0), bwo(-WIN_HW, v1, 0)]
    for (ua, va, ub, vb) in ((-WIN_HW, v0, WIN_HW, v0 + fr), (-WIN_HW, v1 - fr, WIN_HW, v1),
                             (-WIN_HW, v0, -WIN_HW + fr, v1), (WIN_HW - fr, v0, WIN_HW, v1)):
        r0 = [bwo(ua, va, 0.0), bwo(ub, va, 0.0), bwo(ub, vb, 0.0), bwo(ua, vb, 0.0)]
        r1 = [bwo(ua, va, 0.3), bwo(ub, va, 0.3), bwo(ub, vb, 0.3), bwo(ua, vb, 0.3)]
        prism("winframe", r0, r1, P["upvc"])
    # reveal sides (into wall thickness)
    gl = [bwo(-WIN_HW, v0, 0.2), bwo(WIN_HW, v0, 0.2), bwo(WIN_HW, v1, 0.2), bwo(-WIN_HW, v1, 0.2)]
    wg = add_obj("win_glass", gl, [[0, 1, 2, 3]], P["frosted"])
    wg.visible_glossy = False

    # ---- ledges
    yl = FRONT_LEDGE_Y
    LT = 0.1  # slab thickness
    for sd in (-1, 1):
        def ring(y):
            if cutaway and sd == 1:   # show the hollow knee wall
                return [V(sd * (ledge_x(y) + 0.25), y, 0.002), V(sd * ledge_x(y), y, 0.002), V(sd * ledge_x(y), y, LEDGE_H - LT),
                        V(sd * (ledge_x(y) + 0.25), y, LEDGE_H - LT)]
            return [V(sd * half_floor(y), y, 0.002), V(sd * ledge_x(y), y, 0.002), V(sd * ledge_x(y), y, LEDGE_H - LT),
                    V(sd * (slope_x_at(LEDGE_H - LT, y) + 0.05), y, LEDGE_H - LT)]
        # split faces dry/wet: two prisms
        for nm, ya, yb, mt in (("ledge_dry", yl, GLASS_Y, P["ledge_face"]), ("ledge_wet", GLASS_Y, D, P["ledge_face_wet"])):
            lob = prism(nm, ring(ya), ring(yb), mt)
            if cutaway and sd == 1:
                lob.data.materials.append(P["poche"])
                for poly in lob.data.polygons:
                    nrm = poly.normal
                    if nrm.x > 0.5:
                        poly.material_index = 1
        # slab top (overhang 1")
        def slab_ring(y, z0):
            return [V(sd * (ledge_x(y) - 0.08), y, z0), V(sd * (slope_x_at(z0, y) + 0.12), y, z0)]
        r0 = slab_ring(yl, LEDGE_H - LT) + slab_ring(yl, LEDGE_H)[::-1]
        r1 = slab_ring(D, LEDGE_H - LT) + slab_ring(D, LEDGE_H)[::-1]
        prism("ledge_slab", r0, r1, P["ledge_top"], bevel=0.015)
        # front ledge (triangle section)
        x0, x1 = sd * DOOR_HW, sd * (ledge_x(yl) + 0.6)
        tri = lambda x: [V(x, -0.02, 0.002), V(x, yl, 0.002), V(x, yl, LEDGE_H)]
        prism("ledge_front", tri(x0), tri(x1), P["ledge_face"])

    # ---- vanity (right)
    o = Vector((ledge_x(VAN_Y), VAN_Y))
    s_dir = Vector((-SIN_E_, COS_E_))
    t_dir = Vector((-COS_E_, -SIN_E_))
    def lp(s, t, z):
        q = o + s_dir * s + t_dir * t
        return V(q.x, q.y, z)
    tb = -(LEDGE_DX - LEDGE_H / A) * COS_E_ - 0.15
    ctr0 = [lp(-1.25, tb, LEDGE_H - LT), lp(1.25, tb, LEDGE_H - LT), lp(1.25, 1.04, LEDGE_H - LT), lp(-1.25, 1.04, LEDGE_H - LT)]
    ctr1 = [lp(-1.25, tb, LEDGE_H + 0.003), lp(1.25, tb, LEDGE_H + 0.003), lp(1.25, 1.04, LEDGE_H + 0.003), lp(-1.25, 1.04, LEDGE_H + 0.003)]
    prism("counter", ctr0, ctr1, P["counter"], bevel=0.015)
    # under-counter shelf + side panels
    sh0 = [lp(-1.15, 0.0, 0.75), lp(1.15, 0.0, 0.75), lp(1.15, 0.95, 0.75), lp(-1.15, 0.95, 0.75)]
    sh1 = [lp(-1.15, 0.0, 0.85), lp(1.15, 0.0, 0.85), lp(1.15, 0.95, 0.85), lp(-1.15, 0.95, 0.85)]
    prism("van_shelf", sh0, sh1, P["cabinet"], bevel=0.01)
    for s in (-1.25, 1.17):
        p0 = [lp(s, 0.0, 0.002), lp(s, 1.0, 0.002), lp(s, 1.0, LEDGE_H - LT), lp(s, 0.0, LEDGE_H - LT)]
        p1 = [lp(s + 0.08, 0.0, 0.002), lp(s + 0.08, 1.0, 0.002), lp(s + 0.08, 1.0, LEDGE_H - LT), lp(s + 0.08, 0.0, LEDGE_H - LT)]
        prism("van_side", p0, p1, P["cabinet"], bevel=0.01)
    # rolled towels on shelf
    for i, s in enumerate((-0.6, 0.0, 0.6)):
        a = lp(s, 0.1, 1.07)
        b_ = lp(s, 0.85, 1.07)
        cyl("towel_roll", a, b_, 0.21 * M, P["towel"] if i != 1 else P["towel2"], seg=20)
    # vessel basin
    bc = lp(0.0, 0.45, LEDGE_H)
    basin(bc, 0.72, 0.5, 0.45, P["ceramic"], s_dir)
    # faucet: deck tall spout behind basin
    fb = lp(0.0, -0.18, LEDGE_H)
    ft = fb + Vector((0, 0, 1.05 * M))
    cyl("tap_post", fb, ft, 0.05 * M, P["metal"])
    sp_end = ft + Vector((t_dir.x, t_dir.y, 0)) * 0.42 * M
    cyl("tap_spout", ft, sp_end, 0.04 * M, P["metal"])
    cyl("tap_tip", sp_end, sp_end - Vector((0, 0, 0.12 * M)), 0.04 * M, P["metal"])
    lv = fb + Vector((0, 0, 0.75 * M))
    cyl("tap_lever", lv, lv + Vector((s_dir.x, s_dir.y, 0)) * 0.25 * M, 0.025 * M, P["metal"])
    # soap + plant on counter
    sp = lp(0.95, 0.35, LEDGE_H)
    cyl("soap", sp, sp + Vector((0, 0, 0.42 * M)), 0.1 * M, P["frosted"] if True else P["ceramic"])
    cyl("soap_pump", sp + Vector((0, 0, 0.42 * M)), sp + Vector((0, 0, 0.52 * M)), 0.025 * M, P["metal"])
    plant(lp(-1.0, 0.38, LEDGE_H), P)

    # mirror on right slope (unless cutaway)
    if not cutaway:
        mirror_on_slope(P, framed=not LOWCOST)
        # vanity light: small linear sconce above mirror
    # ---- WC (left)
    wc(P, btw=LOWCOST)
    # ---- towel rail on front ledge face (right)
    towel_rail(P, simple=LOWCOST)
    # ---- shower separation
    if LOWCOST:
        partition(P)
    else:
        glass_screen(P)
    # ---- shower fittings
    shower(P)
    # ---- ridge trim + exhaust fan
    ridge(P, cutaway)
    # shower shelf bottles on left ledge slab in shower
    for i, (yy, h, mt) in enumerate(((5.0, 0.62, "ceramic"), (5.35, 0.5, "towel2"), (5.65, 0.42, "metal"))):
        x = -(ledge_x(yy) + 0.3)
        cyl("bottle", V(x, yy, LEDGE_H), V(x, yy, LEDGE_H + h), 0.12 * M, P[mt], seg=20)
    # rolled towel on left ledge shelf between WC and glass
    ya, yb = 3.15, 3.85
    xa, xb = -(ledge_x(ya) + 0.26), -(ledge_x(yb) + 0.26)
    cyl("towel_l", V(xa, ya, LEDGE_H + 0.19), V(xb, yb, LEDGE_H + 0.19), 0.19 * M, P["towel2"], seg=24)
    for ob in bpy.data.objects:
        if ob.type == "MESH" and (ob.name.startswith("wc_") or ob.name.startswith("basin") or ob.name.startswith("box")):
            fix_normals(ob)


def fix_normals(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()


SIN_E_ = math.sin(math.radians(EDGE_ANG))
COS_E_ = math.cos(math.radians(EDGE_ANG))


def basin(center, rs, rt, h, mat, s_dir):
    """oval vessel basin: rings of ellipses"""
    seg = 48
    prof = [(0.55, 0.0), (0.75, 0.05), (0.92, 0.25), (1.0, 0.7), (1.0, 1.0), (0.93, 1.0), (0.9, 0.72), (0.78, 0.4), (0.0, 0.32)]
    t_dir = Vector((-s_dir.y, s_dir.x))
    vs, fs = [], []
    for k, (r, zf) in enumerate(prof):
        for i in range(seg):
            a = 2 * math.pi * i / seg
            q = s_dir * (rs * r * math.cos(a)) + t_dir * (rt * r * math.sin(a))
            vs.append(center + Vector((q.x * M, q.y * M, zf * h * M)))
    for k in range(len(prof) - 1):
        for i in range(seg):
            j = (i + 1) % seg
            fs.append([k * seg + i, k * seg + j, (k + 1) * seg + j, (k + 1) * seg + i])
    fs.append(list(range(seg))[::-1])
    ob = add_obj("basin", vs, fs, mat, smooth=True)
    return ob


def plant(base, P):
    cyl("pot", base, base + Vector((0, 0, 0.42 * M)), 0.2 * M, P["pot"], seg=24)
    random.seed(3)
    for i in range(9):
        a = random.uniform(0, 2 * math.pi)
        tilt = random.uniform(0.05, 0.35)
        L = random.uniform(0.9, 1.5) * M
        w = 0.09 * M
        root = base + Vector((0, 0, 0.38 * M))
        d = Vector((math.cos(a) * math.sin(tilt), math.sin(a) * math.sin(tilt), math.cos(tilt)))
        side = Vector((-math.sin(a), math.cos(a), 0)) * w
        n = 6
        vs = []
        for k in range(n + 1):
            f = k / n
            width = math.sin(math.pi * min(0.98, 0.15 + f * 0.85)) * (1 - f * 0.8)
            c = root + d * L * f
            vs += [c - side * width, c + side * width]
        fs = [[2 * k, 2 * k + 1, 2 * k + 3, 2 * k + 2] for k in range(n)]
        ob = add_obj("leaf", vs, fs, P["leaf"], smooth=True)
        sm = ob.modifiers.new("s", "SOLIDIFY")
        sm.thickness = 0.004


def slope_frame_R():
    n = Vector((-A, -C, -1)).normalized()  # inward normal of right slope
    h = Vector((-TAPER, 1, 0)).normalized()
    d = Vector((0, 0, 1)) - n * n.z
    d.normalize()
    return n, h, d


def mirror_on_slope(P, framed=True):
    n, h, d = slope_frame_R()
    zc = 5.45
    y = VAN_Y + 0.25
    xc = slope_x_at(zc, y)
    c = Vector((xc, y, zc))
    half_v = (6.3 - 4.6) / 2 / d.z
    half_h = 1.15
    def corners(off, grow=0.0):
        pts = []
        for sh, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            p = c + h * (sh * (half_h + grow)) + d * (sv * (half_v + grow)) + n * off
            pts.append(Vector((p.x * M, p.y * M, p.z * M)))
        return pts
    if framed:
        prism("mirror_frame", corners(0.005, 0.06), corners(0.05, 0.06), P["metal"])
        gl = corners(0.055)
        add_obj("mirror", orient_in(gl), [[0, 1, 2, 3]], P["mirror"])
    else:   # plain mirror, polished edges, glued to the board
        prism("mirror", corners(0.005), corners(0.03), P["mirror"])
    # warm LED strip above mirror
    top = [corners(0.06, 0.06)[3], corners(0.06, 0.06)[2]]
    a, b = top
    up = Vector((d.x, d.y, d.z)) * 0.08 * M
    nn = Vector((n.x, n.y, n.z)) * 0.03 * M
    add_obj("mirror_led", [a + up, b + up, b + up * 2 + nn, a + up * 2 + nn], [[0, 1, 2, 3]], emit_mat("led_mirror", (1.0, 0.8, 0.55), 6.0))
    # area light in front of mirror top, pointing down-in
    L = bpy.data.lights.new("vanity_light", "AREA")
    L.shape = "RECTANGLE"
    L.size = 2.0 * M
    L.size_y = 0.15 * M
    L.energy = 25
    L.color = (1.0, 0.82, 0.62)
    lo = bpy.data.objects.new("vanity_light", L)
    COLL.objects.link(lo)
    pc = c + d * (half_v + 0.25) + n * 0.25
    lo.location = Vector((pc.x * M, pc.y * M, pc.z * M))
    tgt = Vector((1.2, VAN_Y, 2.5)) * M
    lo.rotation_euler = (tgt - lo.location).to_track_quat("-Z", "Y").to_euler()


def outline_rounded(back_hw=0.52, side_hw=0.59, L=1.77, n=40):
    pts = [(-back_hw, 0.0)]
    pts.append((-side_hw, 0.45))
    # elliptical front
    for k in range(n + 1):
        a = math.pi * k / n
        pts.append((-side_hw * math.cos(a), 0.45 + (L - 0.45) * math.sin(a)))
    pts.append((side_hw, 0.45))
    pts.append((back_hw, 0.0))
    # dedupe
    out = []
    for p in pts:
        if not out or (abs(out[-1][0] - p[0]) > 1e-6 or abs(out[-1][1] - p[1]) > 1e-6):
            out.append(p)
    return out


def wc(P, btw=False):
    o = Vector((-ledge_x(WC_Y), WC_Y))
    s_dir = Vector((SIN_E_, COS_E_))
    t_dir = Vector((COS_E_, -SIN_E_))
    def lp(s, t, z):
        q = o + s_dir * s + t_dir * t
        return V(q.x, q.y, z)
    ol = outline_rounded()
    # body: tapered loft from z=0.95 (smaller) to 1.30
    rings = []
    prof = ((0.82, 0.62, 0.72), (0.95, 0.86, 0.9), (1.12, 0.98, 0.98), (1.25, 1.0, 1.0), (1.30, 1.0, 1.0))
    if btw:   # floor-standing back-to-wall pan
        prof = ((0.0, 0.74, 0.8), (0.3, 0.74, 0.82), (0.8, 0.84, 0.88), (0.98, 0.93, 0.94), (1.12, 0.98, 0.98),
                (1.25, 1.0, 1.0), (1.30, 1.0, 1.0))
    for z, sc, ts in prof:
        rings.append([lp(sx * sc, sy * ts, z) for sx, sy in ol])
    n = len(ol)
    vs = [v for r in rings for v in r]
    fs = []
    for k in range(len(rings) - 1):
        for i in range(n):
            j = (i + 1) % n
            fs.append([k * n + i, k * n + j, (k + 1) * n + j, (k + 1) * n + i])
    fs.append(list(range(n))[::-1])
    fs.append(list(range((len(rings) - 1) * n, len(rings) * n)))
    ob = add_obj("wc_body", vs, fs, P["ceramic"], smooth=True)
    sub = ob.modifiers.new("sub", "SUBSURF")
    sub.levels = 2
    sub.render_levels = 2
    # lid
    r0 = [lp(sx * 0.97, 0.06 + sy * 0.96, 1.31) for sx, sy in ol]
    r1 = [lp(sx * 0.97, 0.06 + sy * 0.96, 1.37) for sx, sy in ol]
    lid = prism("wc_lid", r0, r1, P["ceramic"])
    sub = lid.modifiers.new("sub", "SUBSURF")
    sub.levels = 2
    sub.render_levels = 2
    # flush plate on ledge face
    fp0 = [lp(-0.42, -0.005, 1.75), lp(0.42, -0.005, 1.75), lp(0.42, -0.005, 2.3), lp(-0.42, -0.005, 2.3)]
    fp1 = [lp(-0.42, 0.03, 1.75), lp(0.42, 0.03, 1.75), lp(0.42, 0.03, 2.3), lp(-0.42, 0.03, 2.3)]
    prism("flush", fp0, fp1, P["metal"], bevel=0.008)
    for s in (-0.17, 0.17):
        a = lp(s, 0.03, 2.025)
        cyl("flush_btn", a, a + Vector((t_dir.x, t_dir.y, 0)) * 0.012 * M, 0.13 * M, P["steel"] if P["metal"].name != "brass" else P["metal"])
    # health faucet + holder
    hb = lp(1.05, 0.0, 1.6)
    cyl("hf_holder", hb, hb + Vector((t_dir.x, t_dir.y, 0)) * 0.12 * M, 0.06 * M, P["metal"])
    hs = hb + Vector((t_dir.x, t_dir.y, 0)) * 0.12 * M
    cyl("hf_head", hs + Vector((0, 0, -0.1 * M)), hs + Vector((0, 0, 0.28 * M)), 0.055 * M, P["metal"])
    # paper holder
    pb = lp(-1.0, 0.0, 1.85)
    cyl("tp_arm", pb, pb + Vector((t_dir.x, t_dir.y, 0)) * 0.22 * M, 0.02 * M, P["metal"])
    pr = pb + Vector((t_dir.x, t_dir.y, 0)) * 0.13 * M
    cyl("tp_roll", pr - Vector((s_dir.x, s_dir.y, 0)) * 0.18 * M, pr + Vector((s_dir.x, s_dir.y, 0)) * 0.18 * M, 0.17 * M, P["ceramic"], seg=24)


def towel_rail(P, simple=False):
    y = FRONT_LEDGE_Y + 0.12
    x0, x1 = 1.6, 3.1
    if simple:   # plain towel bar on two stand-offs
        for x in (x0 + 0.04, x1 - 0.04):
            cyl("bar_stand", V(x, FRONT_LEDGE_Y, 2.35), V(x, y, 2.35), 0.03 * M, P["metal"])
        cyl("towel_bar", V(x0, y, 2.35), V(x1, y, 2.35), 0.028 * M, P["metal"])
    else:
        for x in (x0, x1):
            cyl("rail_post", V(x, y, 0.45), V(x, y, 2.4), 0.035 * M, P["metal"])
            cyl("rail_stand", V(x, y - 0.12, 2.0), V(x, y, 2.0), 0.02 * M, P["metal"])
        for z in (0.6, 1.05, 1.5, 1.95, 2.35):
            cyl("rail_bar", V(x0, y, z), V(x1, y, z), 0.025 * M, P["metal"])
    # hanging towel over top bar
    vs = []
    fs = []
    prof = [(0.0, 2.38), (0.06, 2.42), (0.12, 2.38), (0.15, 1.7), (0.17, 1.2), (0.18, 1.12)]
    for k, (dy, z) in enumerate(prof):
        vs += [V(x0 + 0.12, y - 0.06 + dy, z), V(x1 - 0.12, y - 0.06 + dy, z)]
    prof2 = [(0.0, 2.38), (-0.04, 1.8), (-0.05, 1.45)]
    for k in range(len(prof) - 1):
        fs.append([2 * k, 2 * k + 1, 2 * k + 3, 2 * k + 2])
    base = len(vs)
    for k, (dy, z) in enumerate(prof2):
        vs += [V(x0 + 0.12, y - 0.06 + dy, z), V(x1 - 0.12, y - 0.06 + dy, z)]
    fs.append([0, 1, base + 1, base])
    for k in range(len(prof2) - 1):
        fs.append([base + 2 * k, base + 2 * k + 1, base + 2 * k + 3, base + 2 * k + 2])
    ob = add_obj("towel_hang", vs, fs, P["towel"], smooth=True)
    sm = ob.modifiers.new("s", "SOLIDIFY")
    sm.thickness = 0.02


def glass_screen(P):
    gy = GLASS_Y
    t = 0.03
    for sd in (-1, 1):
        lx = ledge_x(gy)
        big = [V(sd * GLASS_DOOR_HW, gy, 0.02), V(sd * lx, gy, 0.02), V(sd * lx, gy, LEDGE_H + 0.002),
               V(sd * 6.0, gy, LEDGE_H + 0.002), V(sd * 6.0, gy, GLASS_TOP), V(sd * GLASS_DOOR_HW, gy, GLASS_TOP)]
        pl = clip_poly(big, (hs_right if sd > 0 else hs_left))
        pl = clip_poly(pl, lambda p: (hs_right(p) if sd > 0 else hs_left(p)) - 0.03)
        r1 = [p + Vector((0, t * M, 0)) for p in pl]
        prism("glass_fixed", pl, r1, P["glass"])
        # floor channel
        box("channel", (min(sd * GLASS_DOOR_HW, sd * lx), gy - 0.03, 0), (max(sd * GLASS_DOOR_HW, sd * lx), gy + 0.06, 0.06), P["metal"])
    # door (closed)
    d0 = [V(-GLASS_DOOR_HW + 0.02, gy, 0.05), V(GLASS_DOOR_HW - 0.02, gy, 0.05), V(GLASS_DOOR_HW - 0.02, gy, GLASS_TOP), V(-GLASS_DOOR_HW + 0.02, gy, GLASS_TOP)]
    d1 = [p + Vector((0, t * M, 0)) for p in d0]
    prism("glass_door", d0, d1, P["glass"])
    for z in (0.6, GLASS_TOP - 0.6):
        box("hinge", (-GLASS_DOOR_HW - 0.06, gy - 0.05, z - 0.2), (-GLASS_DOOR_HW + 0.12, gy + 0.08, z + 0.2), P["metal"], bevel=0.01)
    # pull handle
    cyl("pull", V(GLASS_DOOR_HW - 0.25, gy - 0.12, 2.6), V(GLASS_DOOR_HW - 0.25, gy - 0.12, 4.4), 0.03 * M, P["metal"])
    for z in (2.7, 4.3):
        cyl("pull_s", V(GLASS_DOOR_HW - 0.25, gy - 0.12, z), V(GLASS_DOOR_HW - 0.25, gy, z), 0.02 * M, P["metal"])


def partition(P):
    """Palette 3: 4" tiled brick partition on the screen line, leaving an A-shaped opening."""
    y0, y1 = GLASS_Y - PART_T / 2, GLASS_Y + PART_T / 2
    for sd in (-1, 1):
        lo, hi = [], []
        for y in (y0, y1):
            xs = slope_x_at(LEDGE_H, y) + 0.06
            lo.append([V(sd * OP_HW, y, 0.003), V(sd * (half_floor(y) + 0.06), y, 0.003),
                       V(sd * xs, y, LEDGE_H), V(sd * OP_HW, y, LEDGE_H)])
            hi.append([V(sd * OP_HW, y, LEDGE_H), V(sd * xs, y, LEDGE_H),
                       V(sd * OP_HW, y, side_z(OP_HW, y) + 0.12)])
        prism("partition_lo", lo[0], lo[1], P["wall_wet"])
        ob = prism("partition_hi", hi[0], hi[1], P["wall_wet"])
        # dry-side face above the 2'-9" datum is whitewashed, like the slopes
        ob.data.materials.append(P["wall_dry"])
        for poly in ob.data.polygons:
            if poly.normal.y < -0.5:
                poly.material_index = 1
    # Kota threshold in the opening
    box("threshold", (-OP_HW, y0, 0.0), (OP_HW, y1, 0.02), P["ledge_top"])
    # curtain rod (shower side) + curtain bunched to the left
    ry = y1 + 0.13
    rz = 6.3
    cyl("curtain_rod", V(-OP_HW, ry, rz), V(OP_HW, ry, rz), 0.035 * M, P["metal"])
    xa, xb = -OP_HW + 0.03, -OP_HW + 0.62
    nx, nz = 64, 14
    vs, fs = [], []
    for j in range(nz + 1):
        z = 0.22 + (rz - 0.1 - 0.22) * j / nz
        flare = 1.0 + 0.25 * (1 - j / nz)
        for i in range(nx + 1):
            f = i / nx
            x = xa + (xb - xa) * f * (0.93 + 0.07 * flare)
            yy = ry + 0.05 * flare * math.sin(2 * math.pi * f * 4.5)
            vs.append(V(x, yy, z))
    for j in range(nz):
        for i in range(nx):
            a = j * (nx + 1) + i
            fs.append([a, a + 1, a + nx + 2, a + nx + 1])
    ob = add_obj("curtain", vs, fs, P["curtain"], smooth=True)
    sm = ob.modifiers.new("s", "SOLIDIFY")
    sm.thickness = 0.006
    for i in range(7):
        x = xa + (xb - xa) * i / 6
        cyl("ring", V(x, ry - 0.03, rz - 0.02), V(x, ry + 0.03, rz - 0.02), 0.05 * M, P["metal"], seg=12)


def shower(P):
    sx, sy, sz = SHOWER_HEAD
    rz = side_z(0, sy)
    cyl("shower_arm", V(sx, sy, sz), V(sx, sy, rz + 0.1), 0.04 * M, P["metal"])
    cyl("rain_head", V(sx, sy, sz - 0.05), V(sx, sy, sz + 0.02), P.get("head_r", 0.42) * M, P["metal"], seg=48)
    # mixer on back wall
    n_back = Vector((0, -C15, S15))
    def bpt(u, z):
        return V(u, back_y(z), z) + n_back * 0.0
    c = bpt(-0.95, 3.25)
    cyl("mixer_plate", c, c + n_back * 0.03 * M, 0.25 * M, P["metal"], seg=40)
    cyl("mixer_lever", c + n_back * 0.03 * M, c + n_back * 0.2 * M, 0.04 * M, P["metal"])
    # hand shower holder + handset
    h = bpt(-0.95, 4.05)
    cyl("hs_holder", h, h + n_back * 0.12 * M, 0.05 * M, P["metal"])
    hp = h + n_back * 0.14 * M
    cyl("hs_handle", hp - Vector((0, 0, 0.35 * M)), hp + Vector((0, 0, 0.12 * M)), 0.045 * M, P["metal"])
    cyl("hs_face", hp + Vector((0, 0, 0.12 * M)), hp + Vector((0, 0, 0.22 * M)), 0.13 * M, P["metal"])


def structure(P):
    """existing yellow dome/extension frame members along the cut edges"""
    r = 0.11
    edges = [((FW / 2, 0, 0), APEX_F), ((-FW / 2, 0, 0), APEX_F), ((FW / 2, 0, 0), (-FW / 2, 0, 0)),
             ((BW / 2, D, 0), APEX_B), ((-BW / 2, D, 0), APEX_B), ((BW / 2, D, 0), (-BW / 2, D, 0)),
             (APEX_F, APEX_B), ((FW / 2, 0, 0), (BW / 2, D, 0)), ((-FW / 2, 0, 0), (-BW / 2, D, 0))]
    for a, b in edges:
        a, b = Vector(a), Vector(b)
        n = (a + b) / 2 - Vector((0, 3.8, 3.0))
        n.normalize()
        off = n * 0.14
        cyl("strut", (a + off) * M, (b + off) * M, r * M, P["yellow"], seg=4)


def ridge(P, cutaway):
    # timber V-trim along ridge on both slopes
    for sd in ((-1,) if cutaway else (-1, 1)):
        a0 = Vector(APEX_F)
        b0 = Vector(APEX_B)
        # offset down the slope by w
        w = 0.33
        def down(p):
            x, y, z = p
            # move along slope steepest-down direction toward side sd
            n = Vector((sd * -A, -C, -1)).normalized() if sd > 0 else Vector((A, -C, -1)).normalized()
            d = Vector((0, 0, 1)) - n * n.z
            d.normalize()
            q = Vector(p) - d * w
            return q, n
        q0, n = down(a0)
        q1, _ = down(b0)
        pts = [a0, b0, q1, q0]
        pts = [Vector((p.x, p.y, p.z)) + n * 0.03 for p in pts]
        pl = [Vector((p.x * M, p.y * M, p.z * M)) for p in pts]
        poly_obj("ridge_trim", orient_in(pl), P["trim"], 0.06 * M)
    # LED line under the ridge (camera-visible emitter) + area light doing the lighting
    a = Vector(APEX_F) + Vector((0, 0.5, -0.45 - 0.5 * C))
    b = Vector(APEX_B) + Vector((0, -0.4, -0.3 + 0.4 * C))
    ob = cyl("ridge_led", a * M, b * M, 0.025 * M, emit_mat("led", (1.0, 0.83, 0.6), 2.0), seg=8)
    ob.visible_shadow = False
    L = bpy.data.lights.new("ridge_light", "AREA")
    L.shape = "RECTANGLE"
    mid = (a + b) / 2
    ln = (b - a).length
    L.size = 0.25 * M
    L.size_y = ln * M
    L.energy = 70
    L.color = (1.0, 0.84, 0.64)
    lo = bpy.data.objects.new("ridge_light", L)
    COLL.objects.link(lo)
    lo.location = (mid - Vector((0, 0, 0.12))) * M
    dirv = (b - a).normalized()
    # rectangle local Y along ridge, local -Z down
    zax = Vector((0, 0, 1))
    yax = dirv
    xax = yax.cross(zax).normalized()
    zax = xax.cross(yax).normalized()
    lo.matrix_world = Matrix((xax, yax, zax)).transposed().to_4x4() @ Matrix.Identity(4)
    lo.location = (mid - Vector((0, 0, 0.12))) * M
    # shower downlight
    S = bpy.data.lights.new("shower_spot", "SPOT")
    S.energy = 35
    S.spot_size = math.radians(95)
    S.spot_blend = 0.7
    S.shadow_soft_size = 0.05
    S.color = (1.0, 0.86, 0.68)
    so = bpy.data.objects.new("shower_spot", S)
    COLL.objects.link(so)
    so.location = V(0, 6.35, side_z(0, 6.35) - 0.15)
    so.rotation_euler = (math.radians(12), 0, 0)
    # exhaust fan grille on right slope
    if not cutaway:
        n, h, d = slope_frame_R()
        c = Vector((slope_x_at(8.0, 3.35), 3.35, 8.0)) + n * 0.02
        cyl("fan", c * M, (c + n * 0.06) * M, 0.32 * M, P["upvc"], seg=40)


# ------------------------------------------------------------------ world, cameras
def setup_world(kind="interior"):
    w = bpy.data.worlds.new("W")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    if kind == "white":
        bg.inputs[0].default_value = (1, 1, 1, 1)
        bg.inputs[1].default_value = 1.0
        return
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs[1].default_value = 0.45
    mr.inputs[2].default_value = 0.85
    nt.links.new(sep.outputs[2], mr.inputs[0])
    col = ramp(nt, mr.outputs[0], [(0.0, (0.75, 0.78, 0.8)), (1.0, (0.36, 0.55, 0.85))])
    nt.links.new(col, bg.inputs[0])
    bg.inputs[1].default_value = 0.9 if kind == "interior" else 1.0


def add_sun(strength=3.5, rot=(math.radians(42), math.radians(8), math.radians(150))):
    s = bpy.data.lights.new("sun", "SUN")
    s.energy = strength
    s.angle = math.radians(2.5)
    s.color = (1.0, 0.95, 0.88)
    so = bpy.data.objects.new("sun", s)
    COLL.objects.link(so)
    so.rotation_euler = rot


def window_light():
    L = bpy.data.lights.new("win_day", "AREA")
    L.shape = "RECTANGLE"
    L.size = 1.2 * M
    L.size_y = 1.6 * M
    L.energy = 22
    L.color = (0.88, 0.93, 1.0)
    lo = bpy.data.objects.new("win_day", L)
    COLL.objects.link(lo)
    v = sum(WIN_V) / 2
    p = Vector((0, D + v * S15, v * C15)) + Vector((0, C15, -S15)) * 0.9
    lo.location = p * M
    lo.visible_glossy = False
    tgt = Vector((0, 3.0, 1.5)) * M
    lo.rotation_euler = (tgt - lo.location).to_track_quat("-Z", "Y").to_euler()


def camera(loc_ft, rot_deg, lens, shift=(0, 0), ortho=None):
    cam = bpy.data.cameras.new("cam")
    cam.lens = lens
    cam.sensor_width = 36
    cam.shift_x, cam.shift_y = shift
    cam.clip_start = 0.05
    if ortho:
        cam.type = "ORTHO"
        cam.ortho_scale = ortho
    co = bpy.data.objects.new("cam", cam)
    COLL.objects.link(co)
    co.location = V(*loc_ft)
    co.rotation_euler = tuple(math.radians(a) for a in rot_deg)
    bpy.context.scene.camera = co
    return co


def look_cam(loc_ft, tgt_ft, lens, shift=(0, 0)):
    co = camera(loc_ft, (0, 0, 0), lens, shift)
    d = V(*tgt_ft) - co.location
    co.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return co


def render_settings(samples, w, h, exposure=0.0, look="AgX - Medium High Contrast"):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.025
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.glossy_bounces = 4
    sc.cycles.transmission_bounces = 8
    sc.cycles.diffuse_bounces = 4
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.cycles.blur_glossy = 1.0
    sc.cycles.sample_clamp_indirect = 8.0
    sc.render.resolution_x = w
    sc.render.resolution_y = h
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = look
    except Exception:
        pass
    sc.view_settings.exposure = exposure
    sc.render.image_settings.file_format = "PNG"
    sc.render.threads_mode = "AUTO"


import os
CUT_CAM = tuple(float(v) for v in os.environ.get("CUT_CAM", "12.8,4.6,13.6").split(","))
CUT_TGT = tuple(float(v) for v in os.environ.get("CUT_TGT", "-1.0,3.7,2.6").split(","))
CUT_LENS = float(os.environ.get("CUT_LENS", "22"))


def pass_mat(kind):
    m = bpy.data.materials.new("pass_" + kind)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[1].default_value = 1.0
    nt.links.new(em.outputs[0], out.inputs[0])
    if kind == "normal":
        g = nt.nodes.new("ShaderNodeNewGeometry")
        vm = nt.nodes.new("ShaderNodeVectorMath")
        vm.operation = "MULTIPLY_ADD"
        vm.inputs[1].default_value = (0.5, 0.5, 0.5)
        vm.inputs[2].default_value = (0.5, 0.5, 0.5)
        nt.links.new(g.outputs["Normal"], vm.inputs[0])
        nt.links.new(vm.outputs[0], em.inputs[0])
    elif kind == "depth":
        cd = nt.nodes.new("ShaderNodeCameraData")
        mth = nt.nodes.new("ShaderNodeMath")
        mth.operation = "DIVIDE"
        mth.inputs[1].default_value = 12.0
        nt.links.new(cd.outputs["View Z Depth"], mth.inputs[0])
        nt.links.new(mth.outputs[0], em.inputs[0])
    elif kind == "id":
        oi = nt.nodes.new("ShaderNodeObjectInfo")
        cmb = nt.nodes.new("ShaderNodeCombineXYZ")
        f1 = nt.nodes.new("ShaderNodeMath"); f1.operation = "MULTIPLY"; f1.inputs[1].default_value = 7.31
        f2 = nt.nodes.new("ShaderNodeMath"); f2.operation = "FRACT"
        f3 = nt.nodes.new("ShaderNodeMath"); f3.operation = "MULTIPLY"; f3.inputs[1].default_value = 13.7
        f4 = nt.nodes.new("ShaderNodeMath"); f4.operation = "FRACT"
        nt.links.new(oi.outputs["Random"], f1.inputs[0]); nt.links.new(f1.outputs[0], f2.inputs[0])
        nt.links.new(oi.outputs["Random"], f3.inputs[0]); nt.links.new(f3.outputs[0], f4.inputs[0])
        nt.links.new(oi.outputs["Random"], cmb.inputs[0]); nt.links.new(f2.outputs[0], cmb.inputs[1]); nt.links.new(f4.outputs[0], cmb.inputs[2])
        nt.links.new(cmb.outputs[0], em.inputs[0])
    elif kind == "white":
        em.inputs[0].default_value = (1, 1, 1, 1)
    elif kind == "holdout":
        nt.nodes.remove(em)
        h = nt.nodes.new("ShaderNodeHoldout")
        nt.links.new(h.outputs[0], out.inputs[0])
    return m


def line_render(out, W, H, ss=2):
    import numpy as np
    from PIL import Image, ImageFilter
    sc = bpy.context.scene
    for ob in list(bpy.data.objects):
        if ob.type == "LIGHT":
            bpy.data.objects.remove(ob)
    setup_world("white")
    sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0.0
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 1
    sc.cycles.use_denoising = False
    sc.cycles.use_adaptive_sampling = False
    sc.cycles.max_bounces = 0
    sc.cycles.filter_width = 0.01
    sc.render.resolution_x, sc.render.resolution_y = W * ss, H * ss
    sc.render.resolution_percentage = 100
    for vt in ("Raw", "Standard"):
        try:
            sc.view_settings.view_transform = vt
            break
        except Exception:
            pass
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "16"
    sc.render.image_settings.color_mode = "RGBA"
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and o.name != "ground"]
    orig = {o.name: [s.material for s in o.material_slots] for o in meshes}
    is_glass = {o.name: any(m and m.name in ("glass", "frosted") for m in orig[o.name]) and o.name.startswith(("glass", "win_glass"))
                for o in meshes}
    def assign(fn):
        for o in meshes:
            m = fn(o)
            if not o.material_slots:
                o.data.materials.append(m)
            for sl in o.material_slots:
                sl.link = "OBJECT"
                sl.material = m
    def shoot(path):
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        import imageio.v3 as iio
        raw = iio.imread(path)
        im = raw.astype(np.float32) / (65535.0 if raw.dtype == np.uint16 else 255.0)
        if im.shape[2] == 3:
            im = np.concatenate([im, np.ones(im.shape[:2] + (1,), np.float32)], axis=2)
        if sc.view_settings.view_transform == "Standard":
            c = im[..., :3]
            im[..., :3] = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
        return im
    tmp = out[:-4]
    mats = {k: pass_mat(k) for k in ("normal", "depth", "id", "white", "holdout")}
    imgs = {}
    for k in ("normal", "id"):
        for o in meshes:
            o.hide_render = is_glass[o.name]
        assign(lambda o, k=k: mats[k])
        imgs[k] = shoot(f"{tmp}_{k}.png")
    for o in meshes:
        o.hide_render = False
    sc.render.film_transparent = True
    assign(lambda o: mats["white"] if is_glass[o.name] else mats["holdout"])
    glass = shoot(f"{tmp}_glass.png")[..., 3]
    def edges(img, thr, rel=None):
        e = np.zeros(img.shape[:2], bool)
        for ax in (0, 1):
            d = np.abs(np.diff(img, axis=ax))
            if d.ndim == 3:
                d = d.max(axis=2)
            if rel is not None:
                base = np.minimum(np.delete(img, -1, axis=ax), np.delete(img, 0, axis=ax))
                d = d / np.maximum(base, 1e-4)
            m = d > thr
            if ax == 0:
                e[:-1] |= m
            else:
                e[:, :-1] |= m
        return e
    a = imgs["normal"][..., 3] > 0.5
    E = edges(imgs["normal"][..., :3], 0.12) | edges(imgs["id"][..., :3], 0.002)
    G = edges(glass[..., None], 0.5)

    line = np.full(E.shape + (3,), 255, np.uint8)
    ink = np.array([38, 36, 34], np.uint8)
    blue = np.array([70, 125, 165], np.uint8)
    from PIL import ImageFilter
    Em = Image.fromarray((E * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))
    Gm = Image.fromarray((G * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))
    E2, G2 = np.asarray(Em) > 0, np.asarray(Gm) > 0
    line[G2] = blue
    line[E2] = ink
    img = Image.fromarray(line).resize((W, H), Image.LANCZOS)
    img.save(out)
    import os
    for k in ("normal", "depth", "id", "glass"):
        try:
            os.remove(f"{tmp}_{k}.png")
        except OSError:
            pass


def main():
    # works both as `python3 x.py args` and `blender -b --python x.py -- args`
    argv = sys.argv[sys.argv.index('--'):] if '--' in sys.argv else sys.argv
    pal, view, out = argv[1], argv[2], argv[3]
    samples = int(argv[4]) if len(argv) > 4 else 128
    W = int(argv[5]) if len(argv) > 5 else 1500
    H = int(argv[6]) if len(argv) > 6 else 1000
    bpy.ops.wm.read_factory_settings(use_empty=True)
    global COLL
    COLL = bpy.context.scene.collection
    global LOWCOST
    LOWCOST = (pal == "p3")
    P = palette(pal)
    cut = view in ("cut", "line_cut")
    build(P, cutaway=cut)
    exposure = 0.0
    if view in ("v1", "line_v1"):
        camera((0.0, 0.95, 5.0), (90, 0, 0), 14.0, shift=(0, -0.17))
        setup_world("interior")
        window_light()
        exposure = -0.4
    elif view == "v4":
        look_cam((1.45, 1.55, 4.8), (-1.7, 4.3, 2.4), 15.0)
        setup_world("interior")
        window_light()
        exposure = -0.4
    elif view == "v3":
        camera((0.0, 3.72, 4.9), (90, 0, 180), 13.0, shift=(0, -0.12))
        setup_world("interior")
        window_light()
        exposure = -0.4
    elif view == "v2":
        camera((0.0, 6.35, 4.85), (90, 0, 180), 14.0, shift=(0, -0.14))
        setup_world("interior")
        window_light()
        exposure = -0.4
    elif view in ("cut",):
        look_cam(CUT_CAM, CUT_TGT, CUT_LENS)
        setup_world("exterior")
        add_sun(3.2, (math.radians(38), math.radians(10), math.radians(115)))
        structure(P)
        g = [V(-40, -40, -0.34), V(40, -40, -0.34), V(40, 40, -0.34), V(-40, 40, -0.34)]
        gob = add_obj("ground", g, [[0, 1, 2, 3]], P["ground"])
        gob.is_shadow_catcher = True
        bpy.context.scene.render.film_transparent = True
        exposure = 0.0
    elif view == "line_cut":
        look_cam(CUT_CAM, CUT_TGT, CUT_LENS)
        structure(P)
    if view.startswith("line"):
        if view == "line_v1":
            camera((0.0, 0.95, 5.0), (90, 0, 0), 14.0, shift=(0, -0.17))
        elif view == "line_v2":
            camera((0.0, 6.35, 4.85), (90, 0, 180), 14.0, shift=(0, -0.14))
        line_render(out, W, H)
        print("WROTE", out)
        return
    transp = bpy.context.scene.render.film_transparent
    render_settings(samples, W, H, exposure)
    bpy.context.scene.render.film_transparent = transp
    bpy.context.scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print("WROTE", out)


if __name__ == "__main__":
    main()
