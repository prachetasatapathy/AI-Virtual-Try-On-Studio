
# --- New AI Try-On Pipeline ---
from ml_model.utils import remove_clothing_bg, pillow_to_bgra, feather_alpha, enhance_image

# MediaPipe Pose Setup
mp_pose = mp.solutions.pose
pose_detector = mp_pose.Pose(
    static_image_mode=True,
    model_complexity=1,
    enable_segmentation=False,
    min_detection_confidence=0.5
)

def detect_clothing_type(cloth_img_pil):
    w, h = cloth_img_pil.size
    aspect = w / h
    if aspect > 0.9 and aspect < 1.2:
        return "tshirt"
    elif aspect >= 1.2:
        return "lehenga"
    elif aspect < 0.9 and h > 1.5 * w:
        return "kurti"
    else:
        return "generic"

def get_body_landmarks(results, img_shape):
    h, w = img_shape[:2]
    lm = results.pose_landmarks.landmark
    def pt(idx): return (int(lm[idx].x * w), int(lm[idx].y * h))
    return {
        "left_shoulder": pt(11),
        "right_shoulder": pt(12),
        "left_hip": pt(23),
        "right_hip": pt(24),
        "mid_shoulder": ((pt(11)[0] + pt(12)[0]) // 2, (pt(11)[1] + pt(12)[1]) // 2),
        "mid_hip": ((pt(23)[0] + pt(24)[0]) // 2, (pt(23)[1] + pt(24)[1]) // 2),
    }

def get_cloth_warp_points(cloth_type, cloth_img, body_pts):
    h, w = cloth_img.shape[:2]
    src = np.float32([
        [0, 0], [w, 0], [w, h], [0, h]
    ])
    if cloth_type == "tshirt":
        dst = np.float32([
            body_pts["left_shoulder"],
            body_pts["right_shoulder"],
            body_pts["right_hip"],
            body_pts["left_hip"]
        ])
    elif cloth_type == "lehenga":
        l = body_pts["left_hip"]
        r = body_pts["right_hip"]
        s = body_pts["left_shoulder"]
        t = body_pts["right_shoulder"]
        dst = np.float32([
            (s[0], s[1]+20),
            (t[0], t[1]+20),
            (r[0]+40, r[1]+120),
            (l[0]-40, l[1]+120)
        ])
    elif cloth_type == "kurti":
        l = body_pts["left_hip"]
        r = body_pts["right_hip"]
        s = body_pts["left_shoulder"]
        t = body_pts["right_shoulder"]
        dst = np.float32([
            (s[0], s[1]),
            (t[0], t[1]),
            (r[0], r[1]+100),
            (l[0], l[1]+100)
        ])
    else:
        dst = np.float32([
            body_pts["left_shoulder"],
            body_pts["right_shoulder"],
            body_pts["right_hip"],
            body_pts["left_hip"]
        ])
    return src, dst

def process_virtual_tryon(user_image_path, cloth_image_path, output_dir):
    user_img = cv2.imread(user_image_path)
    if user_img is None:
        raise ValueError(f"Could not read user image: {user_image_path}")

    # Remove clothing background
    cloth_pil = remove_clothing_bg(cloth_image_path)
    cloth_type = detect_clothing_type(cloth_pil)
    cloth_bgra = pillow_to_bgra(cloth_pil)
    cloth_bgra = feather_alpha(cloth_bgra, feather_radius=8)

    # Pose detection
    img_rgb = cv2.cvtColor(user_img, cv2.COLOR_BGR2RGB)
    results = pose_detector.process(img_rgb)
    if not results.pose_landmarks:
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f"result_{uuid.uuid4().hex}.jpg"
        output_path = os.path.join(output_dir, output_filename)
        cv2.imwrite(output_path, user_img)
        return output_filename

    body_pts = get_body_landmarks(results, user_img.shape)
    src, dst = get_cloth_warp_points(cloth_type, cloth_bgra, body_pts)
    M = cv2.getPerspectiveTransform(src, dst)
    h, w = user_img.shape[:2]
    warped_cloth = cv2.warpPerspective(cloth_bgra, M, (w, h), borderMode=cv2.BORDER_TRANSPARENT)

    # Alpha blend
    result_img = user_img.copy()
    mask = warped_cloth[:, :, 3] > 0
    for c in range(3):
        result_img[:, :, c][mask] = (
            warped_cloth[:, :, c][mask] * (warped_cloth[:, :, 3][mask] / 255.0) +
            result_img[:, :, c][mask] * (1 - warped_cloth[:, :, 3][mask] / 255.0)
        )

    # Enhance output
    result_img = enhance_image(result_img)

    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"result_{uuid.uuid4().hex}.jpg"
    output_path = os.path.join(output_dir, output_filename)
    cv2.imwrite(output_path, result_img)
    return output_filename