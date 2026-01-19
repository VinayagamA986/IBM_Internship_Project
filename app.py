# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from transformers import pipeline
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from pathlib import Path
from PIL import Image
import io

# --- CONFIG ---
st.set_page_config(
    page_title="AI Workout & Diet Planner",
    page_icon="💪",
    layout="wide"
)

# --- LOAD AI MODEL ---
@st.cache_resource
def load_model():
    return pipeline("text2text-generation", model="google/flan-t5-large")

model = load_model()

# --- BMI FUNCTIONS ---
def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100
    bmi = weight / (height_m ** 2)
    return round(bmi, 2)

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
    content = [Paragraph(line, styles["Normal"]) for line in text.split("\n")]
    doc.build(content)
    buffer.seek(0)
    return buffer

# --- FIXED BASE PLAN (~500 WORDS) ---
def get_base_plan():
    return """
DETAILED WORKOUT AND DIET PLAN

PROFILE OVERVIEW
This plan is designed for a student aiming to improve overall health, maintain an ideal BMI, and achieve their fitness goals safely. It balances strength training, cardio, flexibility, and budget-friendly Indian nutrition. Suitable for beginners and intermediate learners.

WEEKLY WORKOUT PLAN
Monday – Full Body Strength:
Push-ups 3x12, Squats 3x15, Plank 3x30s
Tuesday – Cardio & Core:
Jogging 30 min, Mountain Climbers 3x15, Leg Raises 3x12
Wednesday – Upper Body:
Dumbbell Curls 3x12, Shoulder Press 3x10, Triceps Dips 3x12
Thursday – Active Recovery:
Yoga 30 min, Breathing exercises 10 min
Friday – Lower Body:
Lunges 3x10 per leg, Squats 3x15, Calf Raises 3x20
Saturday – Cardio + Abs:
Cycling/Skipping 25 min, Crunches 3x15, Plank 3x40s
Sunday – Rest or Light Walking

DIET PLAN (INDIAN & BUDGET-FRIENDLY)
Early Morning:
Warm water with lemon, 5 soaked almonds
Breakfast:
Vegetable oats or 2 idlis with sambar, Boiled egg or Paneer
Mid-Morning:
One seasonal fruit
Lunch:
Brown rice/2 chapatis, Dal or Grilled chicken, Vegetable curry, Curd
Evening Snack:
Roasted peanuts or Sprouts chaat
Dinner:
2 chapatis with vegetable sabzi, Paneer bhurji or Egg curry

HYDRATION & LIFESTYLE
Drink 2.5–3 liters water daily
Sleep 7–8 hours
Avoid junk food & sugary drinks
Track progress weekly

FINAL ADVICE
Consistency is the key. Follow this plan daily for sustainable results.
"""

# --- USER INPUTS ---
st.title("💪 Personalized Workout & Diet Planner with AI")

st.sidebar.header("👤 User Details")
age = st.sidebar.number_input("Age", 10, 80, 21)
gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])
height = st.sidebar.number_input("Height (cm)", 120, 220, 170)
weight = st.sidebar.number_input("Weight (kg)", 30, 150, 65)
goal = st.sidebar.selectbox("Fitness Goal", ["Weight Loss", "Muscle Gain", "Maintain Fitness"])
diet_type = st.sidebar.selectbox("Diet Preference", ["Vegetarian", "Non-Vegetarian"])
budget = st.sidebar.selectbox("Monthly Food Budget", ["Low", "Medium", "High"])
equipment = st.sidebar.multiselect("Available Equipment", ["Bodyweight", "Dumbbells", "Resistance Bands", "Gym Access"])

# --- BMI DISPLAY ---
bmi = calculate_bmi(weight, height)
category = bmi_category(bmi)

st.subheader("📊 BMI Analysis")
st.metric("BMI Value", bmi)
st.info(f"BMI Category: **{category}**")

# --- CALORIE ESTIMATION ---
st.subheader("🔥 Weekly Calorie Requirement")
calories_map = {"Weight Loss": 1800, "Maintain Fitness": 2200, "Muscle Gain": 2600}
daily_calories = calories_map[goal]
weekly_calories = daily_calories * 7
st.write(f"**Daily Calories:** {daily_calories} kcal")
st.write(f"**Weekly Calories:** {weekly_calories} kcal")

# --- GENERATE AI + HYBRID PLAN ---
if st.button("🧠 Generate AI Fitness Plan"):
    with st.spinner("Generating personalized plan..."):
        equip_text = ", ".join(equipment) if equipment else "No equipment"
        base_plan = get_base_plan()

        prompt = f"""
You are a fitness expert. Take this base plan (~500 words) and customize it for a user:

User Details:
Age: {age}
Gender: {gender}
Height: {height} cm
Weight: {weight} kg
BMI: {bmi} ({category})
Goal: {goal}
Diet Type: {diet_type}
Budget: {budget}
Equipment: {equip_text}
Daily Calories: {daily_calories}

Base Plan:
{base_plan}

Instructions:
- Adjust workouts based on BMI and goal.
- Include gender-specific considerations.
- Suggest Indian meals based on budget and diet type.
- Keep it simple for students with limited equipment.
- Keep total length around 500 words.
"""

        result = model(prompt, max_length=1500, do_sample=False)[0]["generated_text"]
        st.session_state["plan"] = result
        st.success("✅ Personalized AI + Template Plan Generated")

# --- DISPLAY PLAN + PDF ---
if "plan" in st.session_state:
    st.subheader("📋 Your Personalized AI Plan")
    st.write(st.session_state["plan"])
    
    pdf = generate_pdf(st.session_state["plan"])
    st.download_button(
        label="📄 Download Plan as PDF",
        data=pdf,
        file_name="AI_Fitness_Plan.pdf",
        mime="application/pdf"
    )

# --- EXERCISE DEMOS ---
st.subheader("🏋️ Exercise Demonstrations")
exercise_images = {
    "Push-ups": Path(__file__).parent / "Images" / "pushup.jpg",
    "Squats":  Path(__file__).parent / "Images" / "Squats.jpg",
    "Plank":  Path(__file__).parent / "Images" / "Plank.jpg",
    "Dumbbell Curls":  Path(__file__).parent / "Images" / "DumbbellCurls.jpg"
}

cols = st.columns(4)
for col, (name, img) in zip(cols, exercise_images.items()):
    if img.exists():
        col.image(img, caption=name, use_container_width=True)
    else:
        col.write(f"Image not found: {name}")

# --- PROGRESS TRACKING ---
st.subheader("📈 Progress Tracking")
progress_data = pd.DataFrame({
    "Week": ["Week 1", "Week 2", "Week 3", "Week 4"],
    "Weight (kg)": [weight, weight-0.5, weight-1, weight-1.5]
})

fig, ax = plt.subplots()
ax.plot(progress_data["Week"], progress_data["Weight (kg)"], marker="o")
ax.set_xlabel("Week")
ax.set_ylabel("Weight (kg)")
ax.set_title("Weight Progress")
st.pyplot(fig)

# --- FOOTER ---
st.markdown("---")
st.caption("Perfect for Students and Fitness Enthusiasts")
st.caption("Follow daily tips strictly for best results")
