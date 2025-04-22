from ..models.profile import UserProfile

def update_total_score(user, additional_score):
    profile = user.profile
    profile.total_score += additional_score
    profile.level = calculate_level(profile.total_score)
    profile.tier = calculate_tier(profile.total_score)
    profile.save()
    return profile

def calculate_level(score):
    return (score // 100) + 1

def calculate_tier(score):
    if score < 300:
        return "Bronze"
    elif score < 600:
        return "Silver"
    else:
        return "Gold"
