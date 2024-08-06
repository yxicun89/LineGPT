def generate_training_menu(user_info):
    level = user_info['level']
    
    beginner_menu = "胸トレーニング: 2種目\n背中トレーニング: 2種目"
    intermediate_menu = "胸トレーニング: 3種目\n背中トレーニング: 3種目"
    advanced_menu = "胸トレーニング: 4種目\n背中トレーニング: 4種目"
    
    if level == '初心者':
        return beginner_menu
    elif level == '中級者':
        return intermediate_menu
    else:
        return advanced_menu

def analyze_meal_report(meal_report):
    analysis_result = {
        "P": 20,
        "F": 10,
        "C": 70,
        "total_kcal": 500
    }
    
    return analysis_result

def provide_meal_advice(analysis_result, target_pfc):
    advice = "タンパク質が不足しています。もう少しタンパク質を摂取しましょう。"
    return advice
