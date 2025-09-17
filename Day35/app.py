import streamlit as st
from diet_plans import get_diet_plan
from workout_plans import get_workout_plan


def calculate_bmi(weight_kg, height_m):
    """Calculates BMI using the standard formula."""
    return weight_kg / (height_m ** 2)


def get_bmi_category(bmi):
    """Categorizes BMI based on WHO standards for adults."""
    if bmi < 18.5:
        return 'Underweight'
    elif 18.5 <= bmi < 24.9:
        return 'Normal Weight'
    elif 25 <= bmi < 29.9:
        return 'Overweight'
    else:
        return 'Obesity'


# Set up the Streamlit app interface
st.set_page_config(page_title="Indian BMI & Wellness Guide", page_icon="🏋️‍♂️", layout="wide")

st.title("Indian BMI Calculator & Wellness Guide 🇮🇳")
st.markdown("Enter your details to calculate your BMI and get personalized diet and workout recommendations.")

# Input fields for user data
with st.sidebar:
    st.header("Your Details")
    weight = st.number_input("Enter your weight (in kg)", min_value=1.0, value=70.0, step=0.1)
    height_cm = st.number_input("Enter your height (in cm)", min_value=1.0, value=170.0, step=0.1)

    # Convert height from cm to meters for BMI calculation
    height_m = height_cm / 100

# Button to trigger the calculation and display
if st.sidebar.button("Calculate My BMI"):
    if height_m > 0 and weight > 0:
        bmi = calculate_bmi(weight, height_m)
        bmi_category = get_bmi_category(bmi)

        st.subheader("Your Results")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Your BMI is:", f"{bmi:.2f}")

        with col2:
            st.metric("Your BMI Category:", bmi_category)

        st.info("BMI Categories: Underweight (<18.5), Normal Weight (18.5-24.9), Overweight (25-29.9), Obesity (>=30)")

        st.markdown("---")

        # Displaying recommendations
        st.header("Personalized Recommendations")

        diet_plan_text = get_diet_plan(bmi_category)
        workout_plan_text = get_workout_plan(bmi_category)

        # Diet Section
        st.subheader("🍽️ Diet Plan (Indian Context)")
        st.markdown(diet_plan_text)

        # Workout Section
        st.subheader("💪 Workout Plan (Indian Climate)")
        st.markdown(workout_plan_text)

    else:
        st.error("Please enter valid weight and height values.")

st.markdown("---")
st.markdown("Built with ❤️ for a healthier India.")