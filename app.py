# REQUIRED LIBRARIES
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from pathlib import Path
import io

# --- CONFIG ---
st.set_page_config(
    page_title="AI Workout & Diet Planner",
    page_icon="💪",
    layout="wide"
)

# --- BMI FUNCTIONS ---
def calculate_bmi(weight, height_cm):
    h = height_cm / 100
    return round(weight / (h * h), 2)

def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

# --- PDF FUNCTION ---
def generate_pdf(text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    content = [Paragraph(p, styles["Normal"]) for p in text.split("\n\n")]
    doc.build(content)
    buffer.seek(0)
    return buffer

# --- DYNAMIC PLAN GENERATOR ---
def generate_plan(planner_name, age, gender, bmi, category, goal, diet_type, budget, equipment, calories):

    equipment_text = ", ".join(equipment) if equipment else "bodyweight exercises only"

    workout_focus = {
        "Weight Loss": "fat burning, high repetitions, and cardiovascular exercises",
        "Muscle Gain": "progressive overload strength training with proper recovery",
        "Maintain Fitness": "balanced strength, flexibility, and endurance training"
    }

    diet_focus = {
        "Weight Loss": "controlled calories with high fiber and protein",
        "Muscle Gain": "protein-rich meals with complex carbohydrates",
        "Maintain Fitness": "balanced nutrition with adequate vitamins and minerals"
    }

    plan = f"""
<b>PERSONALIZED WORKOUT AND DIET PLAN</b>

<b>Name:</b> {planner_name if planner_name else "AI Fitness Planner"}

<b>PROFILE OVERVIEW</b>

This fitness plan is designed for a {age}-year-old {gender.lower()} student with a BMI of {bmi} ({category}). 
The primary fitness goal is {goal.lower()}, focusing on {workout_focus[goal]}. 
The program is suitable for individuals using {equipment_text} and following a {diet_type.lower()} diet within a {budget.lower()} budget.
The recommended daily calorie intake is around {calories} kcal for sustainable results.

<b>WEEKLY WORKOUT PLAN</b>
Monday – Full Body Strength:
Push-ups 3×12, Squats 3×15, Plank 3×30 seconds.
Tuesday – Cardio & Core:
Jogging or brisk walking for 30 minutes, Mountain climbers 3×15, Leg raises 3×12.
Wednesday – Upper Body:
Dumbbell curls 3×12, Shoulder press 3×10, Triceps dips 3×12.
Thursday – Active Recovery:
Yoga and stretching for 30 minutes with breathing exercises.
Friday – Lower Body:
Lunges 3×10 per leg, Squats 3×15, Calf raises 3×20.
Saturday – Cardio + Abs:
Skipping or cycling 25 minutes, Crunches 3×15, Plank 3×40 seconds.
Sunday – Rest or light walking.

<b>DIET PLAN (INDIAN & BUDGET FRIENDLY)</b>
Diet strategy: {diet_focus[goal]}.

<i>Early Morning:</i> Warm water with lemon and 5 soaked almonds.  
<i>Breakfast:</i> Vegetable oats or idli with sambar and {"paneer or tofu" if diet_type=="Vegetarian" else "boiled eggs"}.  
<i>Mid-Morning:</i> One seasonal fruit such as apple or banana.  
<i>Lunch:</i> Brown rice or chapatis, dal or {"paneer curry" if diet_type=="Vegetarian" else "grilled chicken"}, mixed vegetable sabzi, curd.  
<i>Evening Snack:</i> Sprouts chaat or roasted peanuts.  
<i>Dinner:</i> Chapatis with vegetable curry and {"paneer bhurji" if diet_type=="Vegetarian" else "egg curry"}.

<b>HYDRATION & LIFESTYLE</b>
Drink at least 2.5–3 liters of water daily.
Sleep 7–8 hours for recovery.
Avoid junk food and sugary drinks.
Maintain consistency and track progress weekly.

<b>FINAL ADVICE</b>
This plan is student-friendly, affordable, and safe. 
Follow it consistently for 8–12 weeks to improve fitness, stamina, and overall health.
"""

    return plan.strip()

# --- UI ---
st.title("💪 Personalized Workout & Diet Planner")

st.sidebar.header("👤 User Details")

planner_name = st.sidebar.text_input(
    "Name",
    value="",
    placeholder="Enter Your Name"
)

age = st.sidebar.number_input("Age", 10, 80, 21)
gender = st.sidebar.selectbox("Gender", ["Male", "Female"])
height = st.sidebar.number_input("Height (cm)", 120, 220, 170)
weight = st.sidebar.number_input("Weight (kg)", 30, 150, 65)
goal = st.sidebar.selectbox("Fitness Goal", ["Weight Loss", "Muscle Gain", "Maintain Fitness"])
diet_type = st.sidebar.selectbox("Diet Preference", ["Vegetarian", "Non-Vegetarian"])
budget = st.sidebar.selectbox("Monthly Food Budget", ["Low", "Medium", "High"])
equipment = st.sidebar.multiselect(
    "Available Equipment",
    ["Bodyweight", "Dumbbells", "Resistance Bands", "Gym Access"]
)

# --- BMI DISPLAY ---
bmi = calculate_bmi(weight, height)
category = bmi_category(bmi)

st.subheader("📊 BMI Analysis")
st.metric("BMI", bmi)
st.info(f"BMI Category: **{category}**")

# --- CALORIES ---
calories_map = {
    "Weight Loss": 1800,
    "Maintain Fitness": 2200,
    "Muscle Gain": 2600
}
daily_calories = calories_map[goal]

st.subheader("🔥 Daily Calorie Recommendation")
st.write(f"**{daily_calories} kcal/day**")

# --- GENERATE PLAN ---
if st.button("🧠 Generate Workout & Diet Plan"):
    plan = generate_plan(
        planner_name, age, gender, bmi, category,
        goal, diet_type, budget,
        equipment, daily_calories
    )
    st.session_state["plan"] = plan
    st.markdown(plan, unsafe_allow_html=True)
    st.success("✅ Plan generated successfully!")

# --- PDF DOWNLOAD ---
if "plan" in st.session_state:
    pdf = generate_pdf(st.session_state["plan"])
    st.download_button(
        "📄 Download as PDF",
        data=pdf,
        file_name="Workout_Diet_Plan.pdf",
        mime="application/pdf"
    )

# --- EXERCISE DEMOS ---
st.subheader("🏋️ Exercise Demonstrations")

IMAGE_DIR = Path(__file__).parent / "Images"
exercise_images = {
    "Push-ups": IMAGE_DIR / "pushup.jpg",
    "Squats": IMAGE_DIR / "Squats.jpg",
    "Plank": IMAGE_DIR / "Plank.jpg",
    "Dumbbell Curls": IMAGE_DIR / "DumbbellCurls.jpg"
}

cols = st.columns(4)
for col, (name, img) in zip(cols, exercise_images.items()):
    if img.exists():
        col.image(str(img), caption=name, use_container_width=True)

# --- PROGRESS TRACKING ---
st.subheader("📈 Progress Tracking")

progress = pd.DataFrame({
    "Week": ["Week 1", "Week 2", "Week 3", "Week 4"],
    "Weight (kg)": [weight, weight-0.5, weight-1, weight-1.5]
})

fig, ax = plt.subplots()
ax.plot(progress["Week"], progress["Weight (kg)"], marker="o")
ax.set_xlabel("Week", color="blue")
ax.set_ylabel("Weight (kg)", color="blue")
ax.set_title("Expected Weight Progress", color="green")
st.pyplot(fig)

# --- FOOTER ---
st.markdown("---")
st.caption("Perfect for Students | Budget Friendly | Simple & Effective")
