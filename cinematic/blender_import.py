"""Optional Blender bridge (requires Blender + NumPy; not executed in the lab)."""
import bpy, numpy as np, math, sys
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if len(args)<2: raise SystemExit('blender -b -t 4 -P blender_import.py -- scene.npz output.blend [CYCLES|BLENDER_EEVEE_NEXT] [day|gold|cinematic]')
source,output=args[:2];engine=args[2] if len(args)>2 else 'CYCLES';look=args[3] if len(args)>3 else 'gold'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
a=np.load(source);v=a['vertices'].reshape(-1,3);v=v[:,[0,2,1]];v[:,1]*=-1;faces=np.arange(len(v),dtype=np.int32).reshape(-1,3);colors=a['colors'].astype('float32')/255
mesh=bpy.data.meshes.new('Quest approved geometry');mesh.from_pydata(v.tolist(),[],faces.tolist());mesh.update();obj=bpy.data.objects.new('Quest',mesh);bpy.context.collection.objects.link(obj)
attr=mesh.color_attributes.new(name='Palette',type='FLOAT_COLOR',domain='CORNER');rgba=np.ones((len(v),4),dtype='float32');rgba[:,:3]=np.repeat(np.where(colors<=.04045,colors/12.92,((colors+.055)/1.055)**2.4),3,axis=0);attr.data.foreach_set('color',rgba.ravel())
mat=bpy.data.materials.new('Baked KayKit palette');mat.use_nodes=True;n=mat.node_tree.nodes;node=n.new('ShaderNodeVertexColor');node.layer_name='Palette';bs=n.get('Principled BSDF');mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.72;obj.data.materials.append(mat)
scene=bpy.context.scene;scene.render.engine=engine;scene.render.resolution_x=3840;scene.render.resolution_y=2160;scene.render.resolution_percentage=100
if engine=='CYCLES': scene.cycles.samples=64;scene.cycles.use_denoising=True
co=.76;si=math.sqrt(1-co*co);target=Vector((960,-(540-283)/co,0));direction=Vector((0,-si,co));bpy.ops.object.camera_add(location=target+direction*2500);cam=bpy.context.object;cam.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1920;cam.data.clip_end=6000;scene.camera=cam
looks={'day':((-.55,.95,.30),(1,.96,.88),3.0),'gold':((-.8,.56,.36),(1,.72,.42),3.2),'cinematic':((.72,.29,-.47),(1,.48,.23),2.3)};d,c,e=looks[look];d=Vector((d[0],-d[2],d[1])).normalized();bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler();sun.data.color=c;sun.data.energy=e;sun.data.angle=math.radians(7);scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.45,.62,.8,1);scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.55
scene.view_settings.view_transform='AgX';scene.render.filepath=str(Path(output).with_suffix('.png'));bpy.ops.wm.save_as_mainfile(filepath=str(Path(output).resolve()));bpy.ops.render.render(write_still=True)
