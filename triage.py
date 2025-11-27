from datetime import datetime

def calculate_priority(hr, bp, oxygen, temp):
    # Check deceased condition
    if hr == 0 and bp == 0 and oxygen == 0:
        return "Deceased"

    score = 0

    if hr > 130 or hr < 40:
        score += 3
    elif 40 <= hr <= 60 or 110 <= hr <= 130:
        score += 2
    else:
        score += 1

    if bp < 90 or bp > 180:
        score += 3
    else:
        score += 1

    if oxygen < 90:
        score += 3
    elif 90 <= oxygen <= 95:
        score += 2
    else:
        score += 1

    if temp > 39 or temp < 35:
        score += 2

    if score >= 9:
        return "Critical"
    elif score >= 6:
        return "High"
    elif score >= 4:
        return "Medium"
    else:
        return "Low"