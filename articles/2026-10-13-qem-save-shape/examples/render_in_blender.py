"""Render the actual original/QEM mesh in Blender 4.3.2. Original code, MIT.
Run: blender -b --factory-startup --python render_in_blender.py
This uses Blender as a renderer; it does not invoke Blender's Decimate modifier.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;DATA=json.loads((HERE/'results.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=96;scene.cycles.use_denoising=False
scene.render.resolution_x=900;scene.render.resolution_y=700;scene.render.resolution_percentage=100
scene.world.color=(.5,.5,.5);scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
mat=bpy.data.materials.new('Original jade clay');mat.diffuse_color=(.15,.43,.30,1)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.08));floor=bpy.context.object;floor.name='Neutral display ground'
fm=bpy.data.materials.new('Warm ground');fm.diffuse_color=(.74,.70,.61,1);floor.data.materials.append(fm)
bpy.ops.object.camera_add(location=(3.3,-4.8,3.0));camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,.25))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=3.5;scene.camera=camera
bpy.ops.object.light_add(type='AREA',location=(-3,-4,7));light=bpy.context.object;light.data.energy=650;light.data.shape='DISK';light.data.size=4
results={'blender_version':bpy.app.version_string,'engine':'Cycles CPU','samples':96,'camera':'orthographic, scale 3.5','operation':'import original teaching mesh arrays and render; no Blender simplification','images':[]}
for count,num in [('800','31'),('160','32')]:
    record=DATA['qem']['snapshots'][count];mesh=bpy.data.meshes.new('Original teaching terrain '+count);mesh.from_pydata(record['vertices'],[],record['faces']);mesh.update();obj=bpy.data.objects.new('Original teaching terrain '+count,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat)
    # Flat normals intentionally show the actual finite triangle surfaces.
    for face in mesh.polygons:face.use_smooth=False
    scene.render.filepath=str(HERE.parent/'assets'/f'{num}-blender-render-{count}.png');bpy.ops.render.render(write_still=True)
    results['images'].append({'file':f'assets/{num}-blender-render-{count}.png','vertices':len(mesh.vertices),'faces':len(mesh.polygons)})
    bpy.data.objects.remove(obj,do_unlink=True)
(HERE/'blender-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
