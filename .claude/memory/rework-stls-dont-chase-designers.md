---
name: rework-stls-dont-chase-designers
description: "Model came as STL only? Never suggest asking the designer for STEP; Kyle reworks the meshes in Blender or FreeCAD"
source: spark/rework-stls-dont-chase-designers@22
metadata:
  type: feedback
---

When a model comes only as STL, plan any change to it as an STL rework in Blender or FreeCAD. Don't propose going back to the designer for STEP or other source files.

**Why:** Kyle 2026-11-22, when Tylman's PETmachine files turned out to have no STEP and I suggested asking Tylman for it: "nonsense, we can rework them in blender or free cad, not going back to him". The tools to rework a mesh are already on hand, so asking the designer adds a dependency for nothing.

**How to apply:** Missing STEP is neither a blocker nor a question for Kyle. A file's license still governs sharing: for PETmachine, his files and our reworks of them stay out of every repo (Hive 1333.1).
