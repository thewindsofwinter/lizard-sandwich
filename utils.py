import numpy as np

DIST_HIP_TO_KNEE = 32  # cm
DIST_KNEE_TO_ANKLE = 32  # cm
DIST_ANKLE_TO_TIP = 15  # cm
DIST_BETWEEN_FOOT_CENTERS = 6 # cm


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

# 1, 2, 3, 4, 5, 6 (except minus 1 for joints)
#   1-4
#   | |
#   2 5
#  / /
# 3 6
# angles assumed to be in degrees
def calc_balance_from_six_angles(angles):
    left_hip = angles[0]
    left_knee = angles[1]
    left_foot = angles[2]

    right_hip = angles[3]
    right_knee = angles[4]
    right_foot = angles[5]

    top_angle = np.abs(right_hip - left_hip)
    dist_toe_l, angle_toe_l = calc_abs_dist_and_angle(left_hip, left_knee, left_foot)
    dist_toe_r, angle_toe_r = calc_abs_dist_and_angle(right_hip, right_knee, right_foot)
    dist_heel_l, angle_heel_l = calc_abs_dist_and_angle(left_hip, left_knee, 0)
    dist_heel_r, angle_heel_r = calc_abs_dist_and_angle(right_hip, right_knee, 0)
    dist_heel_l += DIST_ANKLE_TO_TIP
    dist_heel_r += DIST_ANKLE_TO_TIP

    print(top_angle)
    print("(dist, angle)")
    print("left toe:", dist_toe_l, angle_toe_l)
    print("right toe:", dist_toe_r, angle_toe_r)
    print("left heel:", dist_heel_l, angle_heel_l)
    print("right heel:", dist_heel_r, angle_heel_r)

print("balanced")
calc_balance_from_six_angles([90.0, 96.0, 48.0, 90.0, 96.0, 48.0])
print("feet apart, balanced")
calc_balance_from_six_angles([90.0, 134.0, 48.0, 70.0, 134.0, 68.0])