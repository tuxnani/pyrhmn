def get_workout_plan(bmi_category):
    """Returns a tailored workout plan, mindful of the Indian climate."""
    if bmi_category == 'Underweight':
        return """
        #### **Goal: Build Muscle Mass**
        Focus on strength training and compound movements.
        - **Strength Training:** 3-4 sessions per week. Focus on squats, push-ups, and lunges.
        - **Cardio:** Light cardio 2 times per week (e.g., a brisk 15-20 minute walk).
        - **Climate Tip:** Avoid intense outdoor cardio during peak sun hours (11 AM - 4 PM). Consider morning or evening sessions.
        - **Example:**
          - Day 1: Strength training (legs & core)
          - Day 2: Light walk or yoga
          - Day 3: Strength training (upper body)
          - Day 4: Rest
        """
    elif bmi_category == 'Normal Weight':
        return """
        #### **Goal: Maintain Fitness**
        A balanced mix of cardio and strength training is key.
        - **Cardio:** 3-4 sessions per week (30-45 minutes). Brisk walking, jogging, cycling, or swimming are great.
        - **Strength Training:** 2-3 sessions per week (bodyweight exercises like planks, push-ups, squats).
        - **Climate Tip:** Stay hydrated and listen to your body. Consider swimming as it's a great full-body workout that's climate-friendly.
        - **Example:**
          - Day 1: Cardio (jogging)
          - Day 2: Strength training
          - Day 3: Rest
          - Day 4: Cardio (cycling)
          - Day 5: Strength training
        """
    elif bmi_category == 'Overweight':
        return """
        #### **Goal: Calorie Burn**
        Prioritize consistent cardio and light strength training.
        - **Cardio:** Aim for 4-5 sessions per week (45-60 minutes). Brisk walking is highly effective.
        - **Strength Training:** 2 sessions per week (bodyweight exercises to build a base).
        - **Climate Tip:** Early morning walks or indoor workouts (yoga, dance classes) are ideal to beat the heat.
        - **Example:**
          - Day 1: Brisk walk
          - Day 2: Bodyweight workout
          - Day 3: Brisk walk
          - Day 4: Rest
          - Day 5: Brisk walk
        """
    else:  # Obesity
        return """
        #### **Goal: Begin a Journey**
        Start with low-impact exercises to protect joints and build endurance.
        - **Cardio:** Start with 3-4 sessions of gentle walking (20-30 minutes). Increase duration gradually.
        - **Strength Training:** Begin with basic bodyweight exercises (wall push-ups, chair squats).
        - **Climate Tip:** Stick to indoor exercises (home workout videos) or very early morning/late evening walks to avoid heat exhaustion.
        - **Example:**
          - Day 1: Gentle walk
          - Day 2: Light stretching & bodyweight exercises
          - Day 3: Gentle walk
          - Day 4: Rest
        """