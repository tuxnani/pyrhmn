def get_diet_plan(bmi_category):
    """Returns a tailored diet plan for an Indian context."""
    if bmi_category == 'Underweight':
        return """
        #### **Goal: Healthy Weight Gain**
        Focus on nutrient-dense, calorie-rich foods.
        - **Breakfast:** Poha/Upma with peanuts, or a glass of full-fat milk with a banana.
        - **Mid-morning:** A handful of nuts (almonds, walnuts) or a fruit.
        - **Lunch:** Two rotis or a bowl of rice, dal, vegetable curry, and a serving of curd.
        - **Evening Snack:** A cup of tea with a couple of biscuits, or roasted chana.
        - **Dinner:** Similar to lunch, or a light khichdi with ghee.
        - **Hydration:** Drink plenty of water and buttermilk.
        """
    elif bmi_category == 'Normal Weight':
        return """
        #### **Goal: Maintain a Balanced Lifestyle**
        Maintain your healthy weight with a balanced diet.
        - **Breakfast:** A bowl of idli-sambar, dosa, or vegetable paratha.
        - **Mid-morning:** Seasonal fruit like an apple or an orange.
        - **Lunch:** A balanced thali with one or two rotis, dal, mixed vegetable subzi, and a small salad.
        - **Evening Snack:** A cup of green tea or a light snack like a roasted makhanas.
        - **Dinner:** A light meal, such as a bowl of soup with vegetables or a simple dal and rice.
        - **Hydration:** Aim for 8-10 glasses of water daily.
        """
    elif bmi_category == 'Overweight':
        return """
        #### **Goal: Gradual Weight Loss**
        Focus on calorie deficit with high-fiber, low-fat foods.
        - **Breakfast:** A bowl of oats with milk or a moong dal cheela.
        - **Mid-morning:** A small bowl of sprouts or cucumber slices.
        - **Lunch:** One roti, a large portion of vegetable curry, dal, and a generous salad. Avoid rice.
        - **Evening Snack:** Buttermilk or a handful of roasted chana.
        - **Dinner:** A very light meal like vegetable soup or grilled paneer/tofu.
        - **Hydration:** Drink warm water throughout the day.
        """
    else:  # Obesity
        return """
        #### **Goal: Significant Lifestyle Change**
        Strictly focus on whole foods, portion control, and minimizing processed items.
        - **Breakfast:** A high-protein breakfast like paneer bhurji or a protein smoothie.
        - **Mid-morning:** A small portion of a fibrous fruit like guava or pear.
        - **Lunch:** A bowl of brown rice, a large portion of vegetable curry, and a generous salad.
        - **Evening Snack:** Avoid snacks. If hungry, have a cup of green tea.
        - **Dinner:** A very light meal before 8 PM, such as a large bowl of vegetable soup.
        - **Hydration:** Drink plenty of water and herbal teas.
        """