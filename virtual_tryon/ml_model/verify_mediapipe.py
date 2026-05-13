
try:
    import mediapipe as mp
    print("MediaPipe Path:", mp.__file__)
    has_solutions = hasattr(mp, "solutions")
    print("Has Solutions:", has_solutions)
    if has_solutions:
        try:
            from mediapipe.solutions import pose as mp_pose
            print("mp.solutions.pose import: SUCCESS")
            try:
                detector = mp_pose.Pose(
                    static_image_mode=True,
                    model_complexity=1,
                    enable_segmentation=False,
                    min_detection_confidence=0.5
                )
                print("MediaPipe Pose initialized successfully!")
            except Exception as e:
                print("MediaPipe Pose initialization FAILED:", e)
        except Exception as e:
            print("mp.solutions.pose import: FAILED", e)
    else:
        print("Classic MediaPipe API is NOT available. Please reinstall mediapipe.")
except ImportError as e:
    print("mediapipe import failed:", e)