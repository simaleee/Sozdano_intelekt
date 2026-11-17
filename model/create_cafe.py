"""Run: blender -b --python model/create_cafe.py. Dimensions in metres."""
import bpy, math, random, os
from mathutils import Vector
random.seed(18)
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != 'Collection': bpy.data.collections.remove(c)
groups={}
def group(name):
    if name not in groups:
        c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); groups[name]=c
    return groups[name]
current='Interior'
def finish(o,name,mat):
    o.name=name
    for c in list(o.users_collection): c.objects.unlink(o)
    group(current).objects.link(o)
    if mat: o.data.materials.append(mat)
    return o
def material(name,color,metal=0,rough=.6):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    return m
cream=material('Warm mineral plaster',(.73,.68,.56)); white=material('Porcelain',(.91,.87,.76)); stone=material('Sandstone',(.54,.48,.37)); dark=material('Bronze black',(.055,.068,.061),.65,.32)
wood=material('Honey oak',(.40,.23,.10)); green=material('Sage velvet',(.16,.25,.18)); terra=material('Terracotta',(.50,.19,.10)); brass=material('Brushed brass',(.56,.37,.13),.75,.27)
leaf=material('Olive foliage',(.14,.23,.09)); stainless=material('Brushed stainless steel',(.48,.53,.52),.8,.27); soil=material('Soil',(.075,.052,.029)); ground=material('Warm paving',(.38,.40,.35))
glass=material('Smoked architectural glass',(.40,.61,.62),.15,.16)
glass.diffuse_color=(.40,.61,.62,.24); p=glass.node_tree.nodes.get('Principled BSDF'); p.inputs['Alpha'].default_value=.24
glass.surface_render_method='DITHERED'
lightmat=material('Warm luminous glass',(1,.73,.36)); p=lightmat.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(1,.58,.22,1); p.inputs['Emission Strength'].default_value=2
# Subtle procedural wood grain in the editable Blender source.
p=wood.node_tree.nodes.get('Principled BSDF'); n=wood.node_tree.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=4; n.inputs['Detail'].default_value=2
b=wood.node_tree.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value=.16; b.inputs['Distance'].default_value=.035; wood.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']); wood.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
def box(name,loc,size,mat,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('Soft crafted edges','BEVEL'); mod.width=bevel; mod.segments=2
        bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return finish(o,name,mat)
def cyl(name,loc,r,depth,mat,vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc); o=bpy.context.object
    for f in o.data.polygons: f.use_smooth=True
    return finish(o,name,mat)
def sphere(name,loc,scale,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,location=loc); o=bpy.context.object; o.scale=scale
    for f in o.data.polygons: f.use_smooth=True
    return finish(o,name,mat)
def text(name,body,loc,size,mat,rotation=(math.pi/2,0,0)):
    bpy.ops.object.text_add(location=loc,rotation=rotation); o=bpy.context.object; o.data.body=body; o.data.align_x='CENTER'; o.data.size=size; o.data.extrude=.008
    finish(o,name,mat); bpy.ops.object.convert(target='MESH'); return bpy.context.object
def wallx(name,x1,x2,y,h=3.5,mat=cream,z=0): return box(name,((x1+x2)/2,y,z+h/2),(x2-x1,.22,h),mat)
def wally(name,x,y1,y2,h=3.5,mat=cream,z=0): return box(name,(x,(y1+y2)/2,z+h/2),(.22,y2-y1,h),mat)
def doorx(name,x1,x2,y):
    wallx(name+' lintel',x1,x2,y,.9,cream,2.6)
    for x in (x1,x2): box('Door jamb',(x,y,1.3),(.06,.27,2.6),wood)
def doory(name,x,y1,y2):
    wally(name+' lintel',x,y1,y2,.9,cream,2.6)
    for y in (y1,y2): box('Door jamb',(x,y,1.3),(.27,.06,2.6),wood)
def pot(x,y,size=1):
    cyl('Stone planter',(x,y,.30*size),.28*size,.6*size,stone)
    cyl('Soil',(x,y,.61*size),.25*size,.025,soil)
    cyl('Tree trunk',(x,y,1.10*size),.035*size,1.05*size,wood,12)
    for i in range(7):
        a=i*2.4; sphere('Olive foliage',(x+math.cos(a)*.23*size,y+math.sin(a)*.23*size,(1.25+i*.08)*size),(.29*size,.26*size,.32*size),leaf)
def chair(x,y,a=0):
    # local chair faces -Y; rotated as one small assembly.
    before=set(bpy.data.objects)
    box('Upholstered chair seat',(x,y,.48),(.50,.50,.13),green,.065)
    box('Curved oak chair back',(x,y+.22,.81),(.52,.075,.52),wood,.05)
    box('Chair back cushion',(x,y+.168,.83),(.43,.05,.32),green,.04)
    for dx in [-.18,.18]:
        for dy in [-.18,.18]: cyl('Chair leg',(x+dx,y+dy,.23),.022,.46,dark,8)
    from mathutils import Matrix
    tr=Matrix.Translation((x,y,0)) @ Matrix.Rotation(a,4,'Z') @ Matrix.Translation((-x,-y,0))
    for o in set(bpy.data.objects)-before: o.matrix_world=tr @ o.matrix_world
def table(x,y,r=.61):
    cyl('Round oak dining table',(x,y,.76),r,.075,wood,40); cyl('Table pedestal',(x,y,.38),.055,.72,dark); cyl('Table foot',(x,y,.035),.30,.06,dark)
    cyl('Small ceramic vase',(x,y,.86),.055,.14,terra); sphere('Table flower',(x,y,.98),(.075,.075,.10),leaf)
    for dx in [-.28,.28]:
        cyl('Ceramic plate',(x+dx,y,.81),.12,.016,white); cyl('Coffee cup',(x+dx,y+.20,.85),.045,.08,white)
def pendant(x,y):
    cyl('Pendant cable',(x,y,3.06),.012,.75,dark,8)
    bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=.37,radius2=.10,depth=.22,location=(x,y,2.66)); finish(bpy.context.object,'Spun brass pendant',brass)
    cyl('Pendant diffuser',(x,y,2.55),.31,.025,lightmat)
def booth(x,y,length):
    box('Banquette plinth',(x,y,.23),(length,.68,.46),wood,.04); box('Sage banquette seat',(x,y-.04,.51),(length,.74,.16),green,.07)
    box('Sage banquette back',(x,y+.31,.90),(length,.16,.8),green,.06)
    for xx in range(int(length/.32)): box('Upholstery seam',(x-length/2+.18+xx*.32,y+.218,.93),(.012,.008,.61),wood)

current='Site'
box('Presentation plinth',(13,2,-.44),(44,18,.35),ground,.3)
box('Front terrace',(15,-2,-.16),(36,4,.20),stone,.08)
for x in range(-3,34,2): box('Paving joint',(x,-2,-.05),(.025,3.8,.012),ground)
for y in [-3,-2,-1]: box('Paving joint',(15,y,-.05),(36,.025,.012),ground)
for x in [-2,7,16,25,33]: pot(x,-3.2,1.35)
current='Floors'
box('Main foundation',(16,3.9,-.16),(32.4,8.2,.32),stone)
box('Annex foundation',(-3,5.4,-.16),(6.2,5.2,.32),stone)
box('Main terrazzo',(16,3.9,.015),(32,7.8,.035),cream)
box('Annex tile',(-3,5.4,.015),(6,4.8,.035),stone)
# Alternating oak strips make the two public rooms legible in the cutaway.
for x in range(56):
    xx=.25+x*.46
    if xx<14: ymax=4.15 if xx>6 else 7.65
    else: ymax=7.65
    box('Oak floor board',(xx,ymax/2,.045),(.445,ymax-.06,.035),wood)
current='Walls'
wallx('Rear facade',0,32,7.8); wally('East facade',32,0,1); doory('Main entrance',32,1,2.6); wally('East facade',32,2.6,7.8)
wallx('Annex rear',-6,0,7.8); wallx('Annex front',-6,-1.4,3); doorx('Service access',-1.4,0,3); wally('Annex west',-6,3,7.8)
wally('West wall',0,0,3); doory('Annex passage',0,3,4.3); wally('Annex partition',0,4.3,7.8)
# Kitchen 6, utility 7 and corridor 5 along the rear of room 8.
wallx('Kitchen front',7.4,9,4.3); doorx('Kitchen opening',9,10.1,4.3); wallx('Kitchen front',10.1,14,4.3)
wally('Utility partition',6,4.3,7.8); wally('Kitchen partition',7.4,4.3,7.8); wally('Kitchen corridor',12.6,5.5,7.8)
wallx('Utility doorway header',6,7.4,4.3,.9,cream,2.6)
# Connection between the two dining rooms.
wally('Hall separation',14,0,1.8); doory('Wide hall portal',14,1.8,3.6); wally('Hall separation',14,3.6,7.8)
wally('Lobby partition',26,0,1.3); doory('Lobby portal',26,1.3,3); wally('Lobby partition',26,3,7.8)
wallx('Kitchen 2 front',26,28.4,4.4); doorx('Kitchen 2 entrance',28.4,29.5,4.4); wallx('Kitchen 2 front',29.5,32,4.4)
wallx('WC3 front',26,27.9,2.8); wally('WC3 side',27.9,2.8,3.35); doory('WC3 entry',27.9,3.35,4.4)
wally('Annex WC',-1.5,5.5,7.8); wallx('WC11 partition',-1.5,-.95,5.5); doorx('WC11 entry',-.95,0,5.5)
current='Facade'
# Full-height glazed frontage with real open entry portals.
for a,b in [(0,14),(14,26),(26,32)]:
    wallx('Stone fascia',a,b,0,.75,cream,2.75)
    wallx('Stone window sill',a,b,0,.32,stone)
    for i in range(round((b-a)/2)+1):
        x=a+(b-a)*i/round((b-a)/2); box('Bronze window mullion',(x,0,1.52),(.065,.12,2.47),dark)
    box('Front glass',((a+b)/2,0,1.52),(b-a-.12,.025,2.36),glass)
for x in [0,14,26,32]: box('Facade pier',(x,-.10,1.75),(.30,.48,3.5),stone)
for x in [0,14,26]:
    for j in range(7): box('Oak facade fins',(x-.32+j*.11,-.37,1.75),(.055,.10,3.25),wood)
box('Entrance canopy',(32.85,1.8,2.85),(1.9,3.4,.16),dark,.05)
box('Entrance glass',(32,1.8,1.28),(.025,1.48,2.52),glass)
box('Entrance brass handle',(32.08,1.6,1.2),(.06,.04,.55),brass)
for i in range(3): box('Entrance step',(32.2+i*.34,1.8,-.08-i*.055),(.7,2.4,.14),stone)
box('Long bronze canopy',(16,-.78,2.85),(32.5,1.6,.13),dark,.035)
for x in [3,10,18,23,29]:
    box('Facade sconce',(x,-.17,2.35),(.09,.13,.34),brass); box('Facade sconce glow',(x,-.25,2.35),(.06,.025,.23),lightmat)
text('Cafe identity','T E R R A   /   C A F E',(20,-.145,3.02),.35,dark)
text('Facade subtitle','C O F F E E    •    K I T C H E N',(6,-.145,3.12),.19,dark)
current='Roof'
box('Main roof',(16,3.9,3.64),(32.6,8.4,.28),cream,.04); box('Annex roof',(-3,5.4,3.64),(6.5,5.4,.28),cream,.04)
box('Main roof membrane',(16,3.9,3.80),(32.15,7.95,.035),dark)
for y in [-.22,8.02]: box('Parapet',(16,y,3.93),(32.65,.14,.35),stone)
for x in [-.22,32.22]: box('Parapet',(x,3.9,3.93),(.14,8.3,.35),stone)
for x in [8,29]:
    box('Rooftop ventilation',(x,6,4.12),(1.3,1,.6),stainless,.05)
    for j in range(8): box('Vent grille',(x-.5+j*.14,5.49,4.12),(.045,.025,.4),dark)
current='Interior'
# Dining room 8: intimate lounge, banquettes and a coffee counter.
booth(3,6.95,4.7)
for x in [1.5,3.3,5.1]: table(x,5.95,.55); chair(x,5.0,math.pi); pendant(x,5.95)
for x in [2.2,5.2,8.2,11.2]:
    table(x,1.9); chair(x-.90,1.9,math.pi/2); chair(x+.90,1.9,-math.pi/2); pendant(x,1.9)
# Coffee counter, fluted timber front, stone top, espresso machine.
box('Coffee counter',(9.9,3.45,.54),(4.8,.8,1.08),wood,.04); box('Travertine counter',(9.9,3.45,1.12),(5,.94,.12),white,.03)
for i in range(46): box('Counter oak fluting',(7.62+i*.10,3.03,.54),(.045,.04,.95),stone,.012)
box('Espresso machine',(9.1,3.45,1.42),(.8,.48,.48),stainless,.04); box('Espresso front',(9.1,3.19,1.41),(.7,.035,.25),dark)
for x in [8.9,9.2]: cyl('Coffee group',(x,3.14,1.32),.06,.1,brass); cyl('Counter cup',(x,3.4,1.7),.045,.09,white)
box('Pastry display',(11.3,3.45,1.43),(1,.58,.55),glass,.02)
for x in [11,11.3,11.6]: sphere('Pastry',(x,3.4,1.22),(.11,.07,.055),terra)
# Dining room 4: central communal table and two generous seating rows.
booth(20.1,7.02,9.3)
for x in [16.4,18.9,21.4,23.9]:
    table(x,6,.65); chair(x,5.02,math.pi); pendant(x,6)
    table(x,1.65,.6); chair(x-.87,1.65,math.pi/2); chair(x+.87,1.65,-math.pi/2); pendant(x,1.65)
box('Communal oak table',(20.2,3.85,.78),(4.6,.95,.10),wood,.06)
for x in [18.5,21.9]: box('Communal table leg',(x,3.85,.38),(.13,.68,.76),dark)
for x in [18.6,19.7,20.8,21.9]: chair(x,3,math.pi); chair(x,4.7,0)
for x in [18.7,20.2,21.7]: cyl('Table vase',(x,3.85,.94),.09,.22,terra); pendant(x,3.85)
for x,y in [(0.6,3.9),(13.4,6.7),(15,6.9),(25.2,6.9),(25.2,.7),(30.7,.7)]: pot(x,y)
# Acoustic timber panels and framed abstract compositions on the rear wall.
for a,b in [(1,5.5),(15,25)]:
    for i in range(int((b-a)/.18)): box('Oak acoustic slat',(a+i*.18,7.62,1.8),(.065,.09,2.9),wood)
for x in [16.7,20.2,23.7]:
    box('Gallery frame',(x,7.48,2.12),(1.25,.09,1.45),brass,.02); box('Gallery paper',(x,7.42,2.12),(1.14,.025,1.34),white)
    o=cyl('Abstract art disc',(x-.12,7.395,2.22),.38,.018,terra,40); o.rotation_euler[0]=math.pi/2
    box('Abstract art shape',(x+.24,7.37,1.86),(.30,.02,.60),green,.08)
text('Coffee wall sign','S L O W   M O R N I N G S',(3,7.50,2.45),.25,brass)
# Lobby: host station and upholstered waiting bench.
box('Host desk',(28.9,1.1,.52),(1.5,.65,1.04),wood,.05); box('Host stone top',(28.9,1.1,1.07),(1.6,.72,.08),white,.02)
booth(30.3,3.85,2.3); text('Welcome sign','T E R R A',(30.2,4.25,2.2),.28,brass)
# Two equipped kitchens, a pantry and two sanitary rooms.
current='Service'
def kitchen(x1,x2,y):
    span=x2-x1
    box('Stainless kitchen base',((x1+x2)/2,y,.44),(span,.68,.88),stainless,.025); box('Kitchen worktop',((x1+x2)/2,y,.91),(span+.06,.75,.07),stainless)
    for i in range(int(span/.65)): box('Cabinet seam',(x1+.3+i*.65,y-.347,.44),(.015,.012,.74),dark)
    box('Range cooker',(x1+.7,y,.97),(1.05,.6,.07),dark)
    for dx in [-.25,.25]:
        for dy in [-.15,.15]: cyl('Cooktop burner',(x1+.7+dx,y+dy,1.02),.10,.02,stainless)
    box('Extractor hood',(x1+.7,y,2.2),(1.25,.85,.25),stainless,.04); box('Extractor duct',(x1+.7,y,2.75),(.4,.4,.9),stainless)
    box('Inset sink',(x2-.6,y,.96),(.7,.45,.025),dark,.08); cyl('Tap',(x2-.6,y+.23,1.1),.025,.3,stainless)
    box('Tall refrigerator',(x2-.5,y-1.1,1),(1,.8,2),stainless,.04); box('Fridge handle',(x2-.88,y-1.52,1.1),(.04,.04,.58),dark)
kitchen(7.7,12.25,7.3); kitchen(26.5,31.5,7.3)
box('Kitchen prep island',(10.1,5.6,.46),(2.1,.7,.92),stainless,.03)
box('Kitchen prep island',(29,5.6,.46),(2,.7,.92),stainless,.03)
for x in [-5.5,-3.8]:
    for z in [.35,1.0,1.65,2.3]:
        box('Pantry shelving',(x,7.22,z),(1.35,.65,.06),wood)
        for i in range(3): box('Pantry storage jar',(x-.4+i*.4,7.2,z+.16),(.25,.29,.27),white,.025)
    for xx in [x-.63,x+.63]: box('Shelf upright',(xx,7.22,1.2),(.055,.55,2.4),dark)
def toilet(x,y):
    cyl('WC pedestal',(x,y,.22),.20,.44,white); sphere('WC bowl',(x,y-.12,.42),(.28,.38,.16),white); box('WC cistern',(x,y+.24,.64),(.48,.18,.65),white,.07)
    box('Wall hung basin',(x+.55,y-.48,.8),(.5,.4,.16),white,.06); cyl('Basin faucet',(x+.55,y-.34,.96),.02,.22,stainless)
    box('Mirror',(x+.55,y-.22,1.45),(.48,.035,.7),stainless,.03)
toilet(26.65,3.8); toilet(-.95,7.1)
current='Lighting'
world=bpy.context.scene.world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.79,.85,1); world.node_tree.nodes['Background'].inputs[1].default_value=.5
bpy.ops.object.light_add(type='SUN',location=(12,-8,16)); o=bpy.context.object; o.rotation_euler=(.5,-.4,-.5); o.data.energy=2.5; o.data.angle=.22; finish(o,'Afternoon sun',None)
for x in [3,10,19,24,29]:
    bpy.ops.object.light_add(type='AREA',location=(x,3.5,3.3)); o=bpy.context.object; o.data.energy=170; o.data.shape='DISK'; o.data.size=5; finish(o,'Interior fill',None)
# Join objects per collection and material for responsive browser navigation.
for name,c in groups.items():
    buckets={}
    for o in list(c.objects):
        if o.type=='MESH': buckets.setdefault(o.data.materials[0].name if o.data.materials else 'None',[]).append(o)
    for mat,objs in buckets.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in objs: o.select_set(True)
        bpy.context.view_layer.objects.active=objs[0]; bpy.ops.object.join(); bpy.context.object.name=name+'__'+mat
scene=bpy.context.scene
bpy.ops.object.camera_add(location=(43,-35,28)); cam=bpy.context.object; cam.name='Exterior camera'; cam.rotation_euler=(Vector((13,3,0))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=48; scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.cycles.use_denoising=True; scene.render.resolution_x=1600; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'model','terra-cafe.blend'))
bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'model','terra-cafe.glb'),export_format='GLB',export_cameras=False,export_lights=False,export_apply=True)
scene.render.filepath=os.path.join(ROOT,'preview.jpg'); scene.render.image_settings.file_format='JPEG'; scene.render.image_settings.quality=90
bpy.ops.render.render(write_still=True)
for o in groups['Roof'].objects: o.hide_render=True
for o in groups['Facade'].objects: o.hide_render=True
scene.render.filepath=os.path.join(ROOT,'interior.jpg'); bpy.ops.render.render(write_still=True)
print('CAFE_BUILD_COMPLETE')
