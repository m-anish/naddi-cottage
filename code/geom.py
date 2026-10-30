"""Shared geometry for the dome-extension washroom.

Units: feet. Axes:
  x  across the opening (+x = right when standing in the main room looking in)
  y  depth, 0 at the front base line (dome edge), + toward the back window
  z  up, 0 at finished floor level
"""
import math

# Measured off the Onshape frame, Oct 2026 (docs/onshape_frame_check.md).
# Was FW 12 / BW 7 / D 7 / lean 15 deg, the last three estimated from photos:
# the real extension is shallower, wider at the back and leans less.
FW = 12.0          # front triangle side (ft) -- the dome's lower-ring edge, confirmed
BW = 8.30          # back triangle side (ft) -- 7.72 strut + hubs
D = 5.63           # floor depth front->back (ft)
LEAN = math.radians(12.0)   # front & back walls lean "back"; measured 12.1 and 12.6 deg

S15, C15, T15 = math.sin(LEAN), math.cos(LEAN), math.tan(LEAN)

HF = FW * math.sqrt(3) / 2      # in-plane height of front triangle
HB = BW * math.sqrt(3) / 2
APEX_F = (0.0, HF * S15, HF * C15)            # (0, 2.69, 10.04)
APEX_B = (0.0, D + HB * S15, HB * C15)        # (0, 8.57, 5.86)

# taper of floor edge: |x|edge = FW/2 - TAPER*y
TAPER = (FW - BW) / 2 / D                      # 0.357
YP = D / (1 - BW / FW)                         # pyramid vanishing point on floor (16.8)
# side plane: z = A*(FW/2 - |x|) - C*y
C = APEX_F[2] / (YP - APEX_F[1])
A = C * YP / (FW / 2)


def half_floor(y):
    return FW / 2 - TAPER * y


def side_z(x, y):
    """height of side slope above plan point"""
    return A * (FW / 2 - abs(x)) - C * y


def slope_x_at(z, y):
    """|x| of the side slope at height z, depth y"""
    return FW / 2 - (z + C * y) / A


def front_y(z):
    return z * T15


def back_y(z):
    return D + z * T15


def headroom(x, y):
    """max clear height above a floor point (vertical body)."""
    h = side_z(x, y)
    h = min(h, y / T15 if y > 0 else 0.0)  # front wall overhangs into the room
    return max(h, 0.0)


# ---------------- design parameters (Layout A, recommended) ----------------
LEDGE_H = 2.75     # 2'-9" service ledge / counter height
LEDGE_DX = 2.25    # ledge face: x-distance in from floor edge.
                   # Was 1.90, which left only 5'-11" over someone standing at the
                   # basin; 2.25 gives 6'-7". See drawing A-06.
LEDGE_SHELF = LEDGE_DX - LEDGE_H / A           # shelf depth (x) ~0.52 ft


def ledge_x(y):
    return half_floor(y) - LEDGE_DX


# unit vectors along / normal to the right-hand floor edge (in plan)
_L = math.hypot(FW / 2 - BW / 2, D)
EDGE_DIR_R = ((BW / 2 - FW / 2) / _L, D / _L)      # front -> back along right edge
NORM_R_IN = (-D / _L, -(FW / 2 - BW / 2) / _L)     # inward normal of right edge (points left & to front)
EDGE_ANG = math.degrees(math.atan(TAPER))          # 19.65 deg

GLASS_Y = 3.7        # shower screen line (was 4.0, on a 7 ft deep floor)
GLASS_DOOR_HW = 1.0  # half width of central glass door
GLASS_TOP = 6.5
SHOWER_HEAD = (0.0, 4.6, 7.0)   # was y=5.2, beyond the real back wall
WC_Y = 2.2           # WC centre (on left ledge face)
VAN_Y = 2.3          # vanity centre (on right ledge face)
DOOR_HW = 1.25       # 2'-6" door
DOOR_H = 6.667       # 6'-8"
WIN_V = (2.6, 3.75)  # back window in-plane v range (back wall is nearer now)
WIN_HW = 0.5

FT = 0.3048


def fmt_ftin(v):
    neg = v < 0
    v = abs(v)
    ft = int(v)
    inch = round((v - ft) * 12)
    if inch == 12:
        ft += 1
        inch = 0
    s = f"{ft}'-{inch}\""
    return ("-" if neg else "") + s


if __name__ == "__main__":
    print("apex F", APEX_F, "apex B", APEX_B)
    print("A,C", A, C, "taper", TAPER, "YP", YP, "edge ang", EDGE_ANG)
    print("ledge shelf", LEDGE_SHELF)
    print("floor area", (FW + BW) / 2 * D)
    for y in [0, 1.8, 2.4, 3, 4.3, 5, 5.45, 6, 7]:
        print(f"y={y:4.2f} half floor {half_floor(y):.2f} ledge {ledge_x(y):.2f} ridge {side_z(0,y):.2f}",
              " 6'0\" hw", round(slope_x_at(6, y), 2), " 6'6\" hw", round(slope_x_at(6.5, y), 2))

OP_HW = 1.2          # Palette 3: half width of the A-shaped opening in the tiled partition
PART_T = 0.33        # Palette 3: partition thickness incl. tiles (4")
