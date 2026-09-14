"""Pluggable local marker tracking.

OpenCV ArUco is the preferred backend when installed. The browser currently
keeps frames local and uses its small colour tracker; this module provides the
same signal contract for a native/WebAssembly adapter without moving video to
the server.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Marker:
    id: int
    x: float
    y: float
    rotation: float = 0.0
    visible: bool = True

def backend_name() -> str:
    try:
        import cv2  # noqa: F401
        return 'opencv-aruco'
    except ImportError:
        return 'colour-fallback'

def detect(frame, width: int, height: int) -> list[Marker]:
    """Detect ArUco markers from a local BGR/RGB image array.

    Returns normalized centers and in-plane rotation. Importing OpenCV is lazy
    so the base server remains installable without native CV wheels.
    """
    try:
        import cv2
    except ImportError:
        return []
    if not hasattr(cv2, 'aruco'):
        return []
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    corners, ids, _ = cv2.aruco.detectMarkers(frame, dictionary)
    if ids is None:
        return []
    result=[]
    for marker_corners, marker_id in zip(corners, ids.flatten()):
        pts=marker_corners[0]
        cx,cy=pts[:,0].mean()/width,pts[:,1].mean()/height
        rotation=float(__import__('math').degrees(__import__('math').atan2(pts[1,1]-pts[0,1],pts[1,0]-pts[0,0])))
        result.append(Marker(int(marker_id),cx,cy,rotation))
    return result
