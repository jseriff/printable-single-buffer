from distutils import extension
import cadquery as cq
from math import sqrt
from cq_warehouse.fastener import SocketHeadCapScrew, HeatSetNut, HexHeadScrew, IsoThread
from cq_warehouse.bearing import SingleRowCappedDeepGrooveBallBearing
import cq_warehouse.extensions

quickRender = False

wheel_radius = 35
wheel_thickness = 12

wheel_mount_gap = 6
wheel_mount_tolerance = 0.4
wheel_mount_wall_thickness = 2.5
wheel_mount_inner_width = wheel_radius * 2 + wheel_mount_gap * 2
wheel_mount_outer_width = wheel_mount_inner_width + wheel_mount_wall_thickness * 2
wheel_mount_height = wheel_radius * 2 + wheel_mount_gap
wheel_mount_outer_depth = wheel_thickness + wheel_mount_wall_thickness * 2 + wheel_mount_tolerance *2
wheel_mount_inner_depth = wheel_mount_outer_depth - wheel_mount_wall_thickness * 2
wheel_mount_intake_holder_thickness = 4
wheel_mount_intake_height = 8
wheel_mount_intake_inset = 12
wheel_mount_intake_attachment_inset = 5

extension_height = 150
extension_pattern_size = 10

extension_mount_width = 10
extension_mount_height = 8

mounting_connector_width = 20

buffer_cap = cq.Assembly(None, name="buffer_cap")

bearing = SingleRowCappedDeepGrooveBallBearing(size="M8-22-7", bearing_type="SKT")
wheel = (
    cq.Workplane("XZ")
        .cylinder(wheel_thickness, wheel_radius)
        .cut(cq.Solid.makeTorus(wheel_radius+2, wheel_thickness*0.45, dir=cq.Vector(0, 1, 0)).transformGeometry(cq.Matrix([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])))
        .faces(">Y")
        .workplane()
        .polarArray(wheel_radius - bearing.outer_diameter / 2 - 2, 0, 360, 8)
        .circle((wheel_radius - bearing.outer_diameter / 2) / 3 -1)
        .cutThruAll()
        .faces(">Y")
        .workplane()        
        .pressFitHole(bearing=bearing, baseAssembly=buffer_cap, fit="Loose")
        .cut(
            cq.Solid.makeTorus(wheel_radius - bearing.outer_diameter / 2, (wheel_radius - bearing.outer_diameter / 2) / 3, dir=cq.Vector(0, 1, 0))
                .transformGeometry(cq.Matrix([[1,0,0,0],[0,1,0,6],[0,0,1,0],[0,0,0,1]]))
            )
    )
buffer_cap.add(wheel, name="wheel", color=cq.Color(0.0, 1.0, 0.0, 0.2))

mountCenterScrew = SocketHeadCapScrew(size="M3-0.5", fastener_type="iso4762", length=12)
heatset = HeatSetNut(
    size="M3-0.5-6",
    fastener_type="Hilitchi",
    simple=quickRender,
)

patternSketch = (
    cq.Sketch()
        .rarray(wheel_mount_outer_width / 2, wheel_mount_height / 2, 2, 2)
        .rect(wheel_mount_outer_width/2.75,wheel_mount_height/2.75)
        .reset()
        .vertices()
        .fillet(2)
)

wheelMount = (
    cq.Workplane("XY")
        # make the outer box
        .box(wheel_mount_outer_width, wheel_mount_outer_depth, wheel_mount_height)
        # hollow it out
        .cut(
            cq.Workplane("XY")
            .box(wheel_mount_inner_width, wheel_mount_inner_depth, wheel_mount_height+1)
        )        
        # apply the filament reduction pattern
        .faces(">Y")
        .workplane()
        .placeSketch(patternSketch)
        .cutThruAll()
        # cut the friction reduction cylinder
        .faces(">Y").workplane(-wheel_mount_wall_thickness/2)
        .circle(wheel_radius-1)
        .extrude(-wheel_mount_outer_depth+wheel_mount_wall_thickness, combine="cut")
        # extrude the bearing mount
        .faces(">Y").workplane()
        .circle(bearing.bore_diameter/2)
        .extrude(-(wheel_thickness/2+wheel_mount_tolerance+wheel_mount_wall_thickness))
        .faces("<Y").workplane()
        .circle(bearing.bore_diameter/2)
        .extrude(-(wheel_thickness/2+wheel_mount_wall_thickness))
        #add the center attachment screw
        .faces(">Y")
        .workplane()
        .clearanceHole(fastener=mountCenterScrew, baseAssembly=buffer_cap, fit="Loose")            
        # add the center attachment heatset
        .faces("<Y")
        .workplane()
        .insertHole(fastener=heatset, baseAssembly=buffer_cap, manufacturingCompensation=0.3, fit="Loose")        
        # add the intake holder flange
        .faces(">Z").workplane(centerOption="CenterOfMass", offset=wheel_mount_intake_holder_thickness/2)
        .box(wheel_mount_outer_width, wheel_mount_outer_depth, wheel_mount_intake_holder_thickness)
        # add the heatsets to the flange for mounting the intake
        .faces(">Z").workplane()
        .rarray(wheel_mount_inner_width - wheel_mount_intake_attachment_inset, 7, 2, 2)
        .insertHole(fastener=heatset, baseAssembly=buffer_cap, manufacturingCompensation=0.3, fit="Loose")
        # add the passthrough cutouts for the filament
        .faces(">Z").workplane()
        .rarray(wheel_mount_inner_width - wheel_mount_intake_inset*2, 1, 2, 1)        
        .circle(1.5).extrude(-wheel_mount_intake_holder_thickness-1, combine="cut")
        # split the mount into two parts
        .faces("|Y").faces("<Y").workplane(-wheel_mount_outer_depth/2).split(keepTop=True, keepBottom=True)
)

extensionConnectorScrew = SocketHeadCapScrew(size="M3-0.5", fastener_type="iso4762", length=10)

wheelMountA = (
    wheelMount.solids(">Y")
        .faces("<Z")
        .workplane(-extension_mount_height/2)
        .rarray(wheel_mount_outer_width + extension_mount_width, 1, 2, 1)
        .box(extension_mount_width, wheel_mount_outer_depth, extension_mount_height)        
        .faces("+Z").faces(">X or <X").workplane()
        .rarray(wheel_mount_outer_width + extension_mount_width, 1, 2, 1)
        .clearanceHole(fastener=extensionConnectorScrew, baseAssembly=buffer_cap, fit="Loose")  
)
wheelMountB = wheelMount.solids("<Y")


intakeMountScrew = SocketHeadCapScrew(size="M3-0.5", fastener_type="iso4762", length=10)
intakeCouplerScrew = SocketHeadCapScrew(size="13/32-28", fastener_type="asme_b18.3", length=16, simple=False)
intake = (
    cq.Workplane("XY")
        .transformed(offset=(0, 0, wheel_mount_height /2 + wheel_mount_intake_height/2 + wheel_mount_intake_holder_thickness))
        .box(wheel_mount_outer_width, wheel_mount_outer_depth, wheel_mount_intake_height)
        .faces(">Z").workplane()
        .rarray(wheel_mount_inner_width - wheel_mount_intake_inset*2, 1, 2, 1)
        .threadedHole(fastener=intakeCouplerScrew, counterSunk=False, depth=8, fit="Loose")
        .faces(">Z").workplane()
        .rarray(wheel_mount_inner_width - wheel_mount_intake_attachment_inset, 7, 2, 2)
        .clearanceHole(fastener=intakeMountScrew, baseAssembly=buffer_cap, fit="Loose")            
)

extensionPattern = cq.Sketch()

if quickRender:
    extensionPattern.rect(10, 10)
else:
    cutouts = []
    cutoutEdgeGap = extension_pattern_size / 2 + 1.5
    for x in range(-12, 12):
        for y in range(-12, 12):
            cx = cutoutEdgeGap * x * 1.5
            cy = cutoutEdgeGap * (sqrt(3)/2 * x + sqrt(3) * y)
            if cx > -wheel_mount_inner_width/2 + cutoutEdgeGap and cx < wheel_mount_inner_width/2 - cutoutEdgeGap:
                if cy > -extension_height/2 + cutoutEdgeGap and cy < extension_height/2 - cutoutEdgeGap:
                    cutouts.append((cx, cy))

    extensionPattern.push(cutouts).regularPolygon(extension_pattern_size/2, 6, angle=30)


bufferExtension = (
    cq.Workplane("XY")
        # make the outer box
        .transformed(offset=(0, 0, -(wheel_mount_height/2+extension_height/2)))
        .box(wheel_mount_outer_width, wheel_mount_outer_depth, extension_height)
        # hollow it out
        .cut(
            cq.Workplane("XY")
            .transformed(offset=(0, 0, -(wheel_mount_height/2+extension_height/2)))
            .box(wheel_mount_inner_width, wheel_mount_inner_depth, extension_height+1)
        )        
        # add the top extension screw receivers
        .faces(">Z")
        .workplane(-(extension_mount_height+extension_mount_width)/2)
        .rarray(wheel_mount_outer_width + extension_mount_width, 1, 2, 1)
        .box(extension_mount_width, wheel_mount_outer_depth, extension_mount_height+extension_mount_width)
        .edges("<X or >X").edges("<Z")
        .chamfer(extension_mount_width-0.001)
        .faces(">Z").workplane()
        .rarray(wheel_mount_outer_width + extension_mount_width, 1, 2, 1)
        .insertHole(fastener=heatset, baseAssembly=buffer_cap, manufacturingCompensation=0.3, depth=6, fit="Loose")
        # add the bottom extension screw mounts
        .faces("<Z")
        .workplane(-extension_mount_height/2)
        .rarray(wheel_mount_outer_width + extension_mount_width, 1, 2, 1)
        .box(extension_mount_width, wheel_mount_outer_depth, extension_mount_height)        
        .faces("+Z").faces(">X or <X").faces("<Z")
        .workplane()
        .rarray(wheel_mount_outer_width + extension_mount_width, 1, 2, 1)
        .clearanceHole(fastener=extensionConnectorScrew, baseAssembly=buffer_cap, fit="Loose")          
        # add the filament reduction pattern
        .faces(">Y")
        # .faces(">>X[2]")
        .workplane(centerOption="CenterOfMass")
        .placeSketch(extensionPattern)
        .cutThruAll()
)

mountingConnector = (
    cq.Workplane("XY")
        # make the outer box
        .transformed(offset=(0, 0, -(wheel_mount_height/2+extension_height+extension_mount_height/2)))
        .box(wheel_mount_outer_width + extension_mount_width *2 + mounting_connector_width *2, wheel_mount_outer_depth, extension_mount_height)
        # hollow it out
        .cut(
            cq.Workplane("XY")
            .transformed(offset=(0, 0, -(wheel_mount_height/2+extension_height+extension_mount_height/2)))
            .box(wheel_mount_inner_width, wheel_mount_inner_depth, extension_mount_height+1)
        )            
        # add the extension screw passthrough
        .faces(">Z").workplane()
        .rarray(wheel_mount_outer_width + extension_mount_width, 1, 2, 1)
        .clearanceHole(fastener=extensionConnectorScrew, fit="Loose", counterSunk=False)          
        # add the mounting screw holes
        .faces(">Z").workplane()
        .rarray(wheel_mount_outer_width + extension_mount_width * 2 + mounting_connector_width, 1, 2, 1)
        .clearanceHole(fastener=extensionConnectorScrew, fit="Loose")          
)

buffer_cap.add(intake, name="intake", color=cq.Color("blue"))
buffer_cap.add(wheelMountA, name="mountA", color=cq.Color("White"))
buffer_cap.add(wheelMountB, name="mountB", color=cq.Color(1.0, 0.0, 0.0, 0.2))
buffer_cap.add(bufferExtension, name="extension", color=cq.Color('Purple'))
buffer_cap.add(mountingConnector, name="mounting", color=cq.Color('orange'))

if "show_object" in locals():    
    # show_object(wheel, name="Wheel")
    # show_object(wheelMountA, name="Mount Side A")
    # show_object(wheelMountB, name="Mount Side B")
    show_object(buffer_cap, name="Full Assembly")

if "show" in locals():
    show(buffer_cap)

cq.exporters.export(intake, f'/Users/jseriff/projects/cadquery/out/buffer_intake.stl')
cq.exporters.export(wheelMountA.rotateAboutCenter((1, 0, 0), -90), f'/Users/jseriff/projects/cadquery/out/buffer_mount_a.stl')
cq.exporters.export(wheelMountB.rotateAboutCenter((1, 0, 0), 90), f'/Users/jseriff/projects/cadquery/out/buffer_mount_b.stl')
cq.exporters.export(wheel.rotateAboutCenter((1, 0, 0), 90), f'/Users/jseriff/projects/cadquery/out/buffer_wheel.stl')
cq.exporters.export(bufferExtension, f'/Users/jseriff/projects/cadquery/out/buffer_extension_{extension_height}.stl')
cq.exporters.export(mountingConnector, f'/Users/jseriff/projects/cadquery/out/buffer_extrusion_mount.stl')

cq.exporters.export(intake, f'/Users/jseriff/projects/cadquery/out/buffer_intake.step')
cq.exporters.export(wheelMountA.rotateAboutCenter((1, 0, 0), -90), f'/Users/jseriff/projects/cadquery/out/buffer_mount_a.step')
cq.exporters.export(wheelMountB.rotateAboutCenter((1, 0, 0), 90), f'/Users/jseriff/projects/cadquery/out/buffer_mount_b.step')
cq.exporters.export(wheel.rotateAboutCenter((1, 0, 0), 90), f'/Users/jseriff/projects/cadquery/out/buffer_wheel.step')
cq.exporters.export(bufferExtension, f'/Users/jseriff/projects/cadquery/out/buffer_extension_{extension_height}.step')
cq.exporters.export(mountingConnector, f'/Users/jseriff/projects/cadquery/out/buffer_extrusion_mount.step')
