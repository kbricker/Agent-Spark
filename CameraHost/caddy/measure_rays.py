import trimesh, numpy as np
from collections import defaultdict

def xhits_grid(mesh, ys, zs):
    """For each (y,z) return sorted x of all surface crossings along +X."""
    tri = mesh.triangles            # (F,3,3)
    n   = mesh.face_normals
    Y, Z = np.meshgrid(ys, zs, indexing='ij')
    shape = Y.shape
    hits = defaultdict(list)
    ay, az = tri[:,0,1], tri[:,0,2]
    by, bz = tri[:,1,1], tri[:,1,2]
    cy, cz = tri[:,2,1], tri[:,2,2]
    ndotv0 = np.einsum('ij,ij->i', n, tri[:,0,:])
    ymin = np.minimum.reduce([ay,by,cy]); ymax = np.maximum.reduce([ay,by,cy])
    zmin = np.minimum.reduce([az,bz,cz]); zmax = np.maximum.reduce([az,bz,cz])
    for f in range(len(tri)):
        if abs(n[f,0]) < 1e-9:            # parallel to ray
            continue
        iy = np.where((ys >= ymin[f]) & (ys <= ymax[f]))[0]
        iz = np.where((zs >= zmin[f]) & (zs <= zmax[f]))[0]
        if len(iy)==0 or len(iz)==0: continue
        gy = ys[iy][:,None]; gz = zs[iz][None,:]
        # barycentric sign test in YZ
        d1 = (gy-by[f])*(az[f]-bz[f]) - (ay[f]-by[f])*(gz-bz[f])
        d2 = (gy-cy[f])*(bz[f]-cz[f]) - (by[f]-cy[f])*(gz-cz[f])
        d3 = (gy-ay[f])*(cz[f]-az[f]) - (cy[f]-ay[f])*(gz-az[f])
        neg = (d1<0)|(d2<0)|(d3<0); pos = (d1>0)|(d2>0)|(d3>0)
        inside = ~(neg & pos)
        if not inside.any(): continue
        x = (ndotv0[f] - n[f,1]*gy - n[f,2]*gz) / n[f,0]
        for a,b in zip(*np.where(inside)):
            hits[(iy[a], iz[b])].append(float(x[a,b]))
    return hits, shape

def solid_intervals(xs, tol=1e-6):
    xs = np.sort(np.array(xs))
    keep=[xs[0]]
    for v in xs[1:]:
        if v-keep[-1] > 1e-4: keep.append(v)
    xs=np.array(keep)
    if len(xs)%2: xs=xs[:-1]
    return list(zip(xs[0::2], xs[1::2]))
