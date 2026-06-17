import cv2

# ── Config ────────────────────────────────────────────────────────────────────
CAMERA_INDEX = 1          # USB webcam — change to 1 if laptop cam takes slot 0
ARUCO_DICT   = cv2.aruco.DICT_4X4_50
SUBMIT_KEY   = ord(' ')   # spacebar to submit
QUIT_KEY     = ord('q')

# ── Setup ─────────────────────────────────────────────────────────────────────
dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
parameters = cv2.aruco.DetectorParameters()
detector   = cv2.aruco.ArucoDetector(dictionary, parameters)


def get_ordered_ids(corners, ids):
    """Sort detected markers left-to-right by their centre x position."""
    if ids is None:
        return []
    markers = []
    for i, corner in enumerate(corners):
        centre_x = corner[0][:, 0].mean()
        markers.append((centre_x, int(ids[i][0])))
    markers.sort(key=lambda m: m[0])   # sort by x position
    return [marker_id for _, marker_id in markers]


def draw_overlay(frame, corners, ids, ordered_ids):
    """Draw bounding boxes and IDs on the live frame."""
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)
    # Show the current sequence in the top-left corner
    seq_text = "Sequence: " + (str(ordered_ids) if ordered_ids else "none detected")
    cv2.putText(frame, seq_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(frame, "SPACE = submit   Q = quit", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    return frame


def run_detector():
    """
    Opens the webcam and continuously scans for ArUco markers.
    Returns the ordered list of detected IDs when the player presses SPACE.
    Returns None if the player quits with Q.
    """
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open camera at index {CAMERA_INDEX}. "
            "Try changing CAMERA_INDEX to 1 if a laptop webcam is taking slot 0."
        )

    print("Camera opened. Scanning for ArUco markers...")
    print("  Place your cards in view, then press SPACE to submit.")
    print("  Press Q to quit.\n")

    ordered_ids = []

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Warning: failed to grab frame — retrying...")
            continue

        corners, ids, _ = detector.detectMarkers(frame)
        ordered_ids = get_ordered_ids(corners, ids)

        frame = draw_overlay(frame, corners, ids, ordered_ids)
        cv2.imshow("Misty Maze — Card Scanner", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == SUBMIT_KEY:
            if not ordered_ids:
                print("No cards detected — place at least one card and try again.")
            else:
                print(f"\nSubmitted sequence: {ordered_ids}")
                break

        elif key == QUIT_KEY:
            print("Quit.")
            ordered_ids = None
            break

    cap.release()
    cv2.destroyAllWindows()
    return ordered_ids


# ── Run standalone for testing ─────────────────────────────────────────────────
if __name__ == "__main__":
    result = run_detector()
    if result is not None:
        print(f"Final sequence to validate: {result}")
    else:
        print("Session ended without submission.")