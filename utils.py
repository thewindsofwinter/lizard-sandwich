import numpy as np

DIST_HIP_TO_KNEE = 32  # cm
DIST_KNEE_TO_ANKLE = 32  # cm
DIST_ANKLE_TO_TIP = 15  # cm


test_cases = [
    {"hip_angle": 0, "knee_angle": 0, "ankle_angle": 0, "dist": 15},
    {"hip_angle": 90, "knee_angle": 180, "ankle_angle": 0, "dist": 49},
    {"hip_angle": 45, "knee_angle": 90, "ankle_angle": 45, "dist": np.sqrt((np.sqrt(2) * 32)**2 + 15**2)},
]


def calc_abs_dist_and_angle(hip_angle, knee_angle, ankle_angle, use_degrees=True):
    # print('Calculating:', hip_angle, knee_angle, ankle_angle)
    if use_degrees:
        hip_angle = -np.radians(hip_angle)
        knee_angle = np.radians(knee_angle)
        ankle_angle = -np.radians(ankle_angle)
    start = np.array([DIST_ANKLE_TO_TIP, 0])
    # print('start:', start)
    R_ankle = np.array(
        [
            [np.cos(ankle_angle), -np.sin(ankle_angle)],
            [np.sin(ankle_angle), np.cos(ankle_angle)],
        ]
    )
    ankle = -(np.dot(R_ankle, start) - np.array([DIST_KNEE_TO_ANKLE, 0]))
    # print('ankle:', ankle)
    R_knee = np.array(
        [
            [np.cos(knee_angle), -np.sin(knee_angle)],
            [np.sin(knee_angle), np.cos(knee_angle)],
        ]
    )
    knee = np.dot(R_knee, ankle) - np.array([DIST_HIP_TO_KNEE, 0])
    # print('knee:', knee)
    R_hip = np.array(
        [
            [np.cos(hip_angle), -np.sin(hip_angle)],
            [np.sin(hip_angle), np.cos(hip_angle)],
        ]
    )
    
    hip = np.dot(R_hip, knee)
    # print('hip:', hip)
    
    # return distance and angle
    dist, angle = np.linalg.norm(hip), np.degrees(np.arctan2(hip[1], hip[0]))
    print('dist:', dist)
    print('angle:', angle)
    
    return dist, angle

def test_calc_abs_dist_and_angle():
    for test_case in test_cases:
        hip_angle = test_case["hip_angle"]
        knee_angle = test_case["knee_angle"]
        ankle_angle = test_case["ankle_angle"]
        dist = test_case["dist"]
        assert np.isclose(calc_abs_dist_and_angle(hip_angle, knee_angle, ankle_angle)[0], dist)
        print("Test passed!")


test_calc_abs_dist_and_angle()