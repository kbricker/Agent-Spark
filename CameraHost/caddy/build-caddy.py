# Rebuild the GarageBox drive caddy from Maladaptive's unmodified 5050 SFF STL.
#   blender -b --python build-caddy.py -- <source.stl> <output.stl>
# See README.md for how the numbers below were derived. In short:
#   the four tab members are much wider in Y than their bosses look, because the
#   ramps flare toward the floor, so each patch box spans the WHOLE member and every
#   boundary lands in a natural gap where there is no material. Cutting mid-member
#   slices a ramp and leaves a step.
import bpy, math, sys
argv=sys.argv[sys.argv.index("--")+1:]
src,dst=argv[0],argv[1]
HOLE=5.0   # clears the 4.53 mm screw shoulder by 0.47; dremel for more
# full structures, Y boundaries chosen to land in the natural gaps
#  (name, y_lo, y_hi, x_lo, x_hi, shift)
PATCH=[('L-A', 15.0, 70.0,  -6.0,  6.0, +1.0),
       ('L-B',115.0,149.9,  -1.0,  6.0, +1.0),
       ('R-A', 57.0, 90.0, 103.0,112.0, +2.5),
       ('R-B',119.0,149.9, 103.0,112.0, +2.5)]
# z from the floor top up, so the members move and the tray they stand on does not
ZLO, ZHI = 2.0, 17.6

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=src)
obj=bpy.context.selected_objects[0]; obj.name="part"

def box(x0,x1,y0,y1,z0,z1,name):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
    o=bpy.context.active_object; o.scale=(x1-x0,y1-y0,z1-z0); o.name=name
    bpy.ops.object.transform_apply(scale=True); return o
def boolean(t,c,op):
    md=t.modifiers.new("b",'BOOLEAN'); md.operation=op; md.object=c; md.solver='EXACT'
    bpy.context.view_layer.objects.active=t
    bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(c,do_unlink=True)
def dup(o,n):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True)
    bpy.context.view_layer.objects.active=o; bpy.ops.object.duplicate()
    d=bpy.context.active_object; d.name=n; return d

# move each member: copy the whole part, shift it, keep only the part inside the
# patch box, cut that box out of the original, drop the shifted member back in
for name,y0,y1,x0,x1,sh in PATCH:
    chunk=dup(obj,"chunk"); chunk.location.x += sh
    bpy.ops.object.transform_apply(location=True)
    boolean(chunk, box(x0,x1,y0,y1,ZLO,ZHI,"a"), 'INTERSECT')
    boolean(obj,   box(x0,x1,y0,y1,ZLO,ZHI,"b"), 'DIFFERENCE')
    boolean(obj, chunk, 'UNION')

# Holes at the MOVED wall centres. The 1.7 deg tilt and odd vertex count are load
# bearing: cutting concentric with the existing bore makes coplanar facets that the
# boolean mishandles, and a straight cut left 34 open edges at one hole.
for (x,y) in ((3.00,32.25),(3.00,133.75),(109.00,73.75),(109.00,133.75)):
    bpy.ops.mesh.primitive_cylinder_add(radius=HOLE/2, depth=40, vertices=97,
        location=(x,y,8.5), rotation=(math.radians(1.7), math.radians(90),0))
    boolean(obj, bpy.context.active_object, 'DIFFERENCE')

bpy.context.view_layer.objects.active=obj; obj.select_set(True)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles(threshold=1e-4)
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.wm.stl_export(filepath=dst, export_selected_objects=True)
print("TABS3_DONE")
