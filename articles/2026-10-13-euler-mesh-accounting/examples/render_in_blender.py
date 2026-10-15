"""Render actual indexed teaching meshes in Blender 4.3.2 / Cycles CPU. MIT.
Run after mesh_lab.py: blender -b --factory-startup --python render_in_blender.py
The thin edge overlay is a display aid; counts come from the original imported mesh.
"""
from pathlib import Path
import bpy,json,math
from mathutils import Vector
H=Path(__file__).resolve().parent;O=H/'rendered';O.mkdir(exist_ok=True)
models=json.loads((H/'meshes.json').read_text());expected=json.loads((H/'results.json').read_text())['models'];records=[]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=48;s.cycles.use_denoising=False;s.cycles.seed=20261013
s.render.resolution_x=720;s.render.resolution_y=550;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='Standard';s.world.color=(.8,.8,.8);s.render.film_transparent=False
mat=bpy.data.materials.new('Teal clay');mat.diffuse_color=(.22,.59,.53,1)
edge_mat=bpy.data.materials.new('Dark mesh edges');edge_mat.diffuse_color=(.015,.08,.09,1)
floor_mat=bpy.data.materials.new('Ivory floor');floor_mat.diffuse_color=(.88,.87,.82,1)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-3));floor=bpy.context.object;floor.data.materials.append(floor_mat)
bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';s.camera=cam
bpy.ops.object.light_add(type='AREA',location=(-4,-5,9));bpy.context.object.data.energy=1100;bpy.context.object.data.size=7
for name,data in models.items():
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(data['vertices'],[],data['faces']);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);mesh.materials.append(mat)
    counts={'V':len(mesh.vertices),'E':len(mesh.edges),'F':len(mesh.polygons)}
    assert all(counts[k]==expected[name][k] for k in counts),(name,counts)
    v=[Vector(p) for p in data['vertices']];lo=Vector(tuple(min(p[k] for p in v) for k in range(3)));hi=Vector(tuple(max(p[k] for p in v) for k in range(3)));center=(lo+hi)/2;size=max(hi-lo);floor.location.z=lo.z-.15
    cam.location=center+Vector((5,-7,5))*max(1,size/2);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=max(4.2,size*1.75)
    curve=bpy.data.curves.new('Indexed edges '+name,'CURVE');curve.dimensions='3D';curve.bevel_depth=.009*max(1,size/3);curve.bevel_resolution=1
    for e in mesh.edges:
        sp=curve.splines.new('POLY');sp.points.add(1)
        for i,idx in enumerate(e.vertices):sp.points[i].co=(*data['vertices'][idx],1)
    wire=bpy.data.objects.new('Display-only edge overlay',curve);bpy.context.collection.objects.link(wire);curve.materials.append(edge_mat)
    s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
    records.append({'name':name,'original_mesh_counts':counts,'chi':counts['V']-counts['E']+counts['F'],'file':'rendered/'+name+'.png','overlay_in_counts':False})
    bpy.data.objects.remove(wire,do_unlink=True);bpy.data.objects.remove(obj,do_unlink=True)
(H/'blender-results.json').write_text(json.dumps({'blender':bpy.app.version_string,'engine':'Cycles CPU','samples':48,'seed':20261013,'image_size':[720,550],'images':records},ensure_ascii=False,indent=2)+'\n')
