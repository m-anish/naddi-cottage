# Onshape export goes here

Export the dome structure from Onshape (struts only) as:

- **glTF** (.gltf or .glb): for Blender, keeps part colours.
- **STEP** (.step): exact geometry, for checking dimensions.

In Onshape: right-click the Part Studio or Assembly tab › Export › choose the format.

Note the units Onshape exports in (usually metres for glTF, the document's units for STEP) and which axis is up, so the model can be lined up with `code/dome.py` (origin at the floor centre, z up, floor on the lower pentagon ring).
