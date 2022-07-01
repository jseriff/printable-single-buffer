# Printable Single Loop Buffer

**Beta Quality - Use at your own risk**

This is a single loop, expandable buffer for use with the Enraged Rabbit Carrot Feeder, or other MMU.  Each buffer assembly deals with one color, you can print as many as you need.  You can print as many extensions as required to buffer any length, although only ~950mm (500mm of extensions) has been tested by me.  It is intended to be mounted to 2020 extensions, but anything should work.

![Full Setup](/Images/FullSetup.jpeg?raw=true)

The project is generated with a code CAD tool called CadQuery - STLs and STEP files are generated from that, but the python file is the source of truth.  To get this to work in CadQuery, you must also use the cq_warehouse extension, including a custom connector defined as "13/32-28 asme_b18.3"

### Each Buffer Requires

#### Printable Parts
** Parts may not be properly aligned - use your judgment **
* buffer_intake.stl
* buffer_mount_a.stl
* buffer_mount_b.stl
* buffer_wheel.stl
* Some number of buffer_extensions_<X>.stl - X is the height of the extension in MM, you height needs to total slightly over half your reverse bowden length. You can mix and match these within a single buffer.

#### Other Parts
* 608 Bearing
* 2 PC4-M10 pass through bowden couplers
* 6 M3 Heat set inserts (Voron Standard)
* 2 M3 Heat set inserts per extension
* 6 M3x10 
* 2 M3x10 per extension
* 1 M3x12

### Assembly

* Add heatset inserts to the 4 screw holes on top of the A/B buffer mounts (the holes closest to the edges)
* Add a heatset insert to the flat side of the B mount, in the center
* Insert the bearing into the wheel
* Place the Buffer Mount A and B on either side of the wheel, with the bearing on the center post, and use hte M3x12 to attach.  Dont hulk this, you dont want to bind the wheel
* Screw the Intake to the top with M3x10
* Insert the Bowden couplers into the intake
* For each extension:  Add 2x heatset inserts to the top mounting holes - the orientation of the extension is the angled mounts are top, squared are bottom.
* To attach, use M3x10 from the buffer mount to the first extension, and so on
* Insert bowden tubes and push through until they hit plastic

### Notes

* There is also an STL for a mounting connector.  You can place this between two extensions (using longer screws), and use the additional screw holes to mount this to an extrusion or something else for stability.  I have my buffers mounted to extrusions only on the bottom, and they are surprisngly rigid and did not require this additional side mount.
* I use 3mm ID tube from the filament to the buffer, and 2.5mm ID for a small jump from the buffer to the ERCF
* The stl files are all tested, but the STEP file is not

### TODO

- [ ] Change mounting block on the buffer mount A/B so the screw captures both parts and the B mount is not "hanging loose"
- [ ] Add cutouts to the sides of the extensions to reduce plastic usage and provide better visibility
- [ ] Add small chamfer to inside of PTFE holes in buffer mount, to make loading/unloading a little easier
- [ ] Widen the entire assembly to make loading/unloading easier and reduce some friction on the filament
- [ ] Change the buffer mount attachment to no longer require removing screws to change filament

