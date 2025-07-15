import requests
import streamlit as st # type: ignore
import streamlit.components.v1 as components # type: ignore
import pandas as pd
import json
import plotly.express as px # type: ignore
from datetime import datetime
from google.cloud import storage
from google.api_core.exceptions import NotFound # type: ignore
import random
import shutil
from google.oauth2 import service_account
import time
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "qwiklabs-gcp-04-991e2d63cfb0-424e0d2468ef.json"

# Page Config
st.set_page_config(page_title="AURA - UPS Fraud Detection", layout="wide", initial_sidebar_state="expanded")

# Initialize session state
if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"

# Custom CSS
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
    body {
        background: linear-gradient(to right, #fbc2eb, #a6c1ee);
        font-family: 'Segoe UI', sans-serif;
        scrollbar-width: thin;
        scrollbar-color: rgba(60, 60, 60, 0.8) transparent;
    }

    ::-webkit-scrollbar {
        width: 10px;
    }

    ::-webkit-scrollbar-track {
        background: transparent;
    }

    ::-webkit-scrollbar-thumb {
        background-color: rgba(51, 0, 0, 1);
        border-radius: 10px;
    }

    .sidebar-nav-container {
        background-color: #0000 !important;
        padding: 20px 10px;
        border-radius: 12px;
        margin-top: 20px;
        animation: fadeIn 1.2s ease-in-out;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
    }

    button[kind="primary"] {
    background-color: rgba(51, 0, 0, 1)  /* UPS Brown */
    border: 2px solid rgba(51, 0, 0, 1) !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    height: 50px;
    width: 100%;
    border-radius: 8px;
    margin-bottom: 10px;
    transition: all 0.3s ease-in-out;
    }

    button[kind="primary"]:hover {
        background-color: #ffd700 !important;
        color: #000 !important;
        transform: scale(1.01);
    }

    .sidebar-nav-title h2 {
        color: #ffd700;
        text-align: center;
        font-weight: 900;
        margin-bottom: 20px;
        letter-spacing: 1px;
        animation: fadeIn 1s ease-in-out;
    }

    .custom-header {
        background: rgba(51, 0, 0, 1);  /* UPS Brown */
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .sidebar-nav-title h2 {
        color: rgba(88, 89, 91, 1);  /* UPS Gray 1 */
        text-align: center;
        font-weight: 900;
        margin-bottom: 20px;
        letter-spacing: 1px;
        animation: fadeIn 1s ease-in-out;
    }

    .equal-box {
        background: #0000;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        height: 300px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.9); }
        to { opacity: 1; transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
.st-emotion-cache-1legitb {
    position: relative;
    top: 0px;
    background-color: rgba(51, 0, 0, 1);  /* UPS Brown */
    color: #212529;
    color-scheme: light;
    z-index: 999991;
    min-width: 200px;
    max-width: 600px;
    transform: none;
    transition: transform 300ms, min-width 300ms, max-width 300ms;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown(
    """
    <div style="text-align: center; margin-bottom: 15px; background-color: #ffc107; padding: 15px 10px; border-radius: 10px;">
        <div style="font-size: 22px; font-weight: 900; color: #000000; letter-spacing: 1px;">🛡️ AURA</div>
        <div style="font-size: 15px; font-weight: 700; color: #000000; letter-spacing: 0.5px;">AUtomated Risk Analysis</div>
    </div>
    """,
    unsafe_allow_html=True
)
# UPS Navbar Button Styling (Inject once globally)
st.markdown("""
<style>
/* Default Button Style */
div.stButton > button {
    background-color: rgba(51, 0, 0, 1);  /* UPS Brown */
    color: white;
    padding: 10px 25px;
    font-size: 16px;
    border: 2px solid white;  /* Yellow border */
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    margin-bottom: 10px;
    width: 100%;
    transition: all 0.3s ease-in-out;
}

/* Hover State */
div.stButton > button:hover {
    background-color: white !important;
    color: #000 !important;
}

/* Active (Click) State */
div.stButton > button:active {
    background-color: white !important;
    color: white !important;
    border: 2px solid white !important;
}
</style>
""", unsafe_allow_html=True)



# Sidebar Navigation
with st.sidebar:
    pages = {
        "🏠 Home": "Home",
        "📘 About": "About",
        "🤝 Fraud Lens": "Customer",
        "🕵️ Policy Managemnet": "Policy",
         "📁 Detect Fraud": "Upload",
        "📦  Business Insights": "Logic",
        "📊 Analytics": "Analytics",
        
    }

    for label, page in pages.items():
        if st.button(label, key=page):
            st.session_state.active_page = page

    st.markdown('</div>', unsafe_allow_html=True)  # Close sidebar container



# Header
st.markdown(f"""
<style>
@keyframes fadeInZoom {{
    0% {{
        opacity: 0;
        transform: scale(0.9) translateY(20px);
    }}
    100% {{
        opacity: 1;
        transform: scale(1) translateY(0);
    }}
}}

.custom-header-animated {{
    /*background: #FFB500; *//* UPS Yellow */
    background : #351C15;        
    padding: 25px;
    border-radius: 14px;
    margin-bottom: 25px;
    text-align: center;
    animation: fadeInZoom 1s ease-in-out;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);  /* Darker shadow for contrast */
    transition: all 0.4s ease-in-out;
    border: 1px solid #FFB500; /* Border same as background or darker */
}}

.custom-header-animated h1 {{
    font-size: 2.8rem;
    font-weight: 900;
    color: white; /* Black text for contrast */
    text-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    animation: fadeInZoom 1.2s ease-in-out;
    letter-spacing: 2px;
}}

.custom-header-animated h5 {{
    color: white;
    font-size: 1.2rem;
    font-weight: 500;
    animation: fadeInZoom 1.4s ease-in-out;
}}

.custom-header-animated span {{
    color: #4B2E2E; /* Dark Brown Accent */
    font-weight: 700;
    text-transform: uppercase;
    font-size: 1.1rem;
}}
</style>

<div class="custom-header-animated">
    <h1><strong>AURA</strong> - Automated Risk Analysis</h1>
</div>
""", unsafe_allow_html=True)



# Page Content
if st.session_state.active_page == "Home":
    # --- Main Content using Components.html ---
    # Inject Bootstrap, Font Awesome, AOS + Content
    components.html(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>AURA UI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- AOS Animation -->
    <link href="https://unpkg.com/aos@2.3.4/dist/aos.css" rel="stylesheet">

    <!-- Font Awesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">

    <style>
        /* Custom Color Palette */
        :root {{
            --aura-dark-blue: #0d1b2a;
            --aura-medium-blue: #1b263b;
            --aura-light-blue: #415a77;
            --aura-accent-gold: #ffd700;
            --aura-light-bg: #e6edf5; /* Lighter background for some cards */
            --aura-card-text: #333;
        }}

        body {{
            /* These styles will be overridden by Streamlit's body style, but good practice for embedded HTML */
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--aura-light-bg);
        }}

        .container {{
            max-width: 1200px; /* Max width for better readability on wide screens */
        }}

        .section-title {{
            font-size: 2.2rem;
            font-weight: 700;
            color: var(--aura-medium-blue);
            margin-top: 60px;
            margin-bottom: 40px;
            text-align: center;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
            position: relative;
        }}
        .section-title i {{
            color: var(--aura-light-blue);
            margin-right: 15px;
        }}
        .section-title::after {{
            content: '';
            display: block;
            width: 80px;
            height: 4px;
            background: linear-gradient(to right, var(--aura-light-blue), var(--aura-accent-gold));
            margin: 15px auto 0;
            border-radius: 2px;
        }}

        .card {{
            border-radius: 18px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            border: none; /* Remove default bootstrap border */
            overflow: hidden; /* Ensures border-radius is applied to content */
            color: var(--aura-card-text);
            padding: 25px; /* Increased padding inside cards */
        }}
        .card:hover {{
            transform: translateY(-10px); /* More pronounced lift effect */
            box-shadow: 0 16px 30px rgba(0,0,0,0.25); /* Stronger shadow on hover */
        }}
        .card-title {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--aura-medium-blue);
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }}
        .card-title i {{
            margin-right: 15px;
            color: var(--aura-accent-gold); /* Icons in card titles */
            font-size: 1.8rem;
        }}
        .card-body {{
            font-size: 1.05rem;
            line-height: 1.7;
            color: #555;
        }}
        .card-body ul {{
            padding-left: 25px;
            margin-bottom: 0;
        }}
        .card-body ul li {{
            margin-bottom: 8px;
            /* Custom bullet point */
            list-style: none; /* Remove default bullet */
        }}
        .card-body ul li:before {{
            content: "\\f058"; /* Font Awesome check-circle icon */
            font-family: "Font Awesome 5 Free"; /* Use Font Awesome Free */
            font-weight: 900; /* For solid icon */
            color: var(--aura-light-blue);
            margin-right: 10px;
        }}
        /* Specific card background colors */
        .card.bg-aura-primary {{
            background-color: var(--aura-light-bg) !important;
        }}
        .card.bg-aura-secondary {{
        background: linear-gradient(to right, #778da9, #415a77) !important; /* Gradient background */
        color: white;
        }}
        .card.bg-aura-secondary .card-title,
        .card.bg-aura-secondary .card-body,
        .card.bg-aura-secondary .card-title i {{
            color: white;
        }}
        .card.bg-aura-secondary .card-body ul li:before {{
            color: var(--aura-accent-gold); /* Ensure checkmark is visible */
        }}
        .card.bg-aura-info {{
            background: linear-gradient(to right, #cfe2f3, #9fc5e8) !important;
            color: #333;
        }}
        .card.bg-aura-success {{
            background: linear-gradient(to right, #d4edda, #a7e6b7) !important;
            color: #333;
        }}
        .card.bg-aura-dark {{
            background-color: var(--aura-medium-blue) !important;
            color: white;
        }}
        .card.bg-aura-dark .card-title, .card.bg-aura-dark .card-title i {{
            color: white;
        }}
        .highlight {{
            background: linear-gradient(45deg, var(--aura-accent-gold), #ffc107);
            padding: 10px 20px;
            border-radius: 25px; /* More rounded */
            font-weight: 600;
            color: var(--aura-dark-blue);
            display: inline-block; /* For proper padding and radius */
            font-size: 1.1rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }}
        .feature-list {{
            list-style: none;
            padding: 0;
            font-size: 1.1rem;
        }}
        .feature-list li {{
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
        }}
        .feature-list li i {{
            margin-right: 15px;
            color: var(--aura-light-blue);
            font-size: 1.5rem;
            flex-shrink: 0;
            padding-top: 3px; /* Align icon better with text */
        }}
    </style>
    </head>
    <body>
    <div class="container py-5">

        <!-- Highlighted Tag -->
        <div class="text-center mb-5" data-aos="fade-down" data-aos-delay="100">
            <span class="highlight"><i class="fas fa-tags"></i> Category: Customer Experience & Security</span>
        </div>

        <!-- Section 1: About AURA - Business Problem & Key Goals -->
        <h2 class="section-title" data-aos="fade-up"><i class="fas fa-info-circle"></i> About AURA</h2>
        <div class="row g-4 mb-5">
            <div class="col-md-6" data-aos="fade-right" data-aos-delay="200">
                <div class="card bg-aura-primary">
                    <h5 class="card-title"><i class="fas fa-lock"></i> Business Problem</h5>
                    <p class="card-body">
                        Organizations like UPS constantly seek ways to automate and improve fraud detection. Manual log analysis is time-consuming, resource-intensive, and prone to human error. Automating this process ensures faster response times, reduced financial losses, and enhanced security posture.
                    </p>
                </div>
            </div>
            <div class="col-md-6" data-aos="fade-left" data-aos-delay="300">
                <div class="card bg-aura-secondary">
                    <h5 class="card-title"><i class="fas fa-bullseye"></i> Key Goals</h5>
                    <ul class="card-body">
                        <li>Download and intelligently analyze app logs at scale.</li>
                        <li>Accurately detect rapid user actions (e.g., bot activity, account takeover attempts).</li>
                        <li>Identify and flag geolocation anomalies across user sessions.</li>
                        <li>Profile shippers & user behavior for deviations from normal patterns.</li>
                        <li>Proactively flag international activity and transaction risks.</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- Section 2: How AURA Works - AI Logic & Detection -->
        <h2 class="section-title" data-aos="fade-up"><i class="fas fa-cogs"></i> How AURA Works</h2>
        <div class="row g-4 mb-5 justify-content-center">
            <div class="col-md-8" data-aos="zoom-in" data-aos-delay="100">
                <div class="card bg-aura-info text-dark">
                    <h5 class="card-title"><i class="fas fa-brain"></i> AI Logic & Detection Principles</h5>
                    <p class="card-body">
                        AURA's intelligent system leverages advanced machine learning to learn from historical logs, identify baseline behaviors, and detect significant anomalies in real-time. It focuses on contextual patterns, not just isolated events.
                    </p>
                    <div class="card-body">
                        <ul class="feature-list">
                            <li><i class="fas fa-hourglass-half"></i> <strong>Velocity Checks:</strong> Flagsly high action rates within short timeframes (e.g., excessive login attempts, rapid address changes).</li>
                            <li><i class="fas fa-globe"></i> <strong>Geolocation Anomaly:</strong> Identifies impossible travel scenarios or activity originating from diverse geographic locations in quick succession.</li>
                            <li><i class="fas fa-chart-line"></i> <strong>Behavioral Profiling:</strong> Builds dynamic profiles of user and shipper behavior, alerting on sudden, uncharacteristic shifts (e.g., a domestic shipper suddenly sending packages internationally).</li>
                            <li><i class="fas fa-project-diagram"></i> <strong>Graph Analysis:</strong> Detects suspicious relationship networks or flows of funds/packages that deviate from established norms.</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <!-- Section 3: Key Benefits & Outcomes -->
        <h2 class="section-title" data-aos="fade-up"><i class="fas fa-star"></i> Key Benefits & Outcomes</h2>
        <div class="row g-4 mb-5">
            <div class="col-md-6" data-aos="fade-right" data-aos-delay="200">
                <div class="card bg-light text-dark">
                    <h5 class="card-title"><i class="fas fa-hand-holding-usd"></i> Protect Revenue</h5>
                    <p class="card-body">
                        AURA helps significantly reduce financial losses due to fraudulent activities by early detection and rapid response. Estimates suggest an 80% reduction in specific fraud types.
                    </p>
                </div>
            </div>
            <div class="col-md-6" data-aos="fade-left" data-aos-delay="300">
                <div class="card bg-aura-primary">
                    <h5 class="card-title"><i class="fas fa-tachometer-alt"></i> Boost Productivity</h5>
                    <p class="card-body">
                        Automating log analysis frees up fraud analysts from manual, repetitive tasks, allowing them to focus on complex investigations and strategic initiatives, increasing overall team productivity.
                    </p>
                </div>
            </div>
            <div class="col-md-6" data-aos="fade-right" data-aos-delay="400">
                <div class="card bg-aura-secondary">
                    <h5 class="card-title"><i class="fas fa-bell"></i> Real-time Alerting</h5>
                    <p class="card-body">
                        Provides instant, actionable alerts for suspicious activities, enabling real-time intervention and minimizing potential damage from ongoing fraudulent patterns.
                    </p>
                </div>
            </div>
            <div class="col-md-6" data-aos="fade-left" data-aos-delay="500">
                <div class="card bg-aura-dark">
                    <h5 class="card-title"><i class="fas fa-cube"></i> Adaptive Learning</h5>
                    <p class="card-body">
                        The AI models continuously learn from new data and feedback, adapting to evolving fraud tactics and ensuring the system remains effective against emerging threats.
                    </p>
                </div>
            </div>
        </div>

        <!-- Section 4: Technology Stack (Example) -->
        <h2 class="section-title" data-aos="fade-up"><i class="fas fa-layer-group"></i> Technology Stack</h2>
        <div class="row g-4 mb-5 justify-content-center">
            <div class="col-md-10" data-aos="zoom-in" data-aos-delay="100">
                <div class="card bg-light">
                    <h5 class="card-title"><i class="fas fa-code-branch"></i> Underlying Technologies</h5>
                    <p class="card-body">AURA is built on a robust and scalable architecture, designed for high-performance data processing and real-time anomaly detection.</p>
                    <div class="row pt-3">
                        <div class="col-md-4 text-center mb-4">
                            <i class="fab fa-python fa-3x text-info mb-3"></i>
                            <p class="h6">Python & Data Science Libraries</p>
                        </div>
                        <div class="col-md-4 text-center mb-4">
                            <i class="fas fa-database fa-3x text-success mb-3"></i>
                            <p class="h6">Scalable Databases (e.g., PostgreSQL, Snowflake)</p>
                        </div>
                        <div class="col-md-4 text-center mb-4">
                            <i class="fab fa-aws fa-3x text-warning mb-3"></i>
                            <p class="h6">Cloud Infrastructure (AWS/Azure)</p>
                        </div>
                        <div class="col-md-4 text-center mb-4">
                            <i class="fas fa-signal fa-3x text-danger mb-3"></i>
                            <p class="h6">Real-time Data Streaming (e.g., Kafka)</p>
                        </div>
                        <div class="col-md-4 text-center mb-4">
                            <i class="fas fa-chart-pie fa-3x text-primary mb-3"></i>
                            <p class="h6">Visualization Tools (Streamlit, Tableau)</p>
                        </div>
                        <div class="col-md-4 text-center mb-4">
                            <i class="fas fa-shield-alt fa-3x text-secondary mb-3"></i>
                            <p class="h6">Advanced ML Algorithms (Isolation Forest, Autoencoders)</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- AOS Animation Script -->
    <script src="https://unpkg.com/aos@2.3.4/dist/aos.js"></script>
    <script>
        AOS.init({{
            duration: 1000, /* animation duration */
            once: true /* run animations only once */
        }});
    </script>
    <!-- Bootstrap Bundle with Popper -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """, height=3000, scrolling=True) # Increased height to accommodate more content, or remove if scrolling handles all


        # --- Streamlit Native Interactive Section ---
        # --- Separator and Intro Section ---
    st.markdown("---")
    st.markdown("""
    <style>
    /* Entry animation */
    @keyframes fadeSlideIn {
        0% {
            opacity: 0;
            transform: translateY(40px) scale(0.96);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    /* Glowing gradient header */
    .aura-demo-title {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(90deg, #FFD700, #FF69B4, #00FFFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1.5px;
        text-shadow: 0 0 15px rgba(255,255,255,0.2);
        margin-bottom: 20px;
        animation: fadeSlideIn 1s ease-in-out;
    }

    /* Subtitle with higher contrast and spacing */
    .aura-demo-subtitle {
        font-size: 1.25rem;
        color: #f0f0f0;
        font-weight: 400;
        max-width: 800px;
        margin: 0 auto;
        line-height: 1.8;
        animation: fadeSlideIn 1.4s ease-in-out;
    }

    /* Wrapper with dark background and glow */
    .aura-demo-container {
        text-align: center;
        padding: 60px 30px 40px 60px;
        background: radial-gradient(circle at center, #111111, #000000);
        border-radius: 20px;
        box-shadow: 0 0 25px rgba(255, 215, 0, 0.2);
        margin-top: 30px;
    }
    </style>

    <div class="aura-demo-container">
        <div class="aura-demo-title">🚀 Try AURA Demo</div>
        <div class="aura-demo-subtitle">
            Experience the power of <strong>AURA</strong> by simulating real-time UPS fraud detection scenarios.<br>
            Test how transactions are evaluated using intelligent AI models tailored for logistics security.
        </div>
    </div>
    """, unsafe_allow_html=True)




    # --- Initialize Toggle State ---
    if "show_demo_form" not in st.session_state:
        st.session_state.show_demo_form = False

    # --- Toggle Button ---
    center_btn_col = st.columns([1, 2, 1])[1]
    with center_btn_col:
        st.markdown("""
        <div style="padding-top: 60px;">
        """, unsafe_allow_html=True)
        if st.button("🎯 Simulate a Transaction", use_container_width=True):
            st.session_state.show_demo_form = not st.session_state.show_demo_form

    # --- Simulated Fraud Detection Form with Border ---
    if st.session_state.show_demo_form:
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.subheader("🔎 Transaction Input")

                transaction_id = st.text_input("Transaction ID", "TFX789012")
                user_id = st.text_input("User ID", "UAX54321")
                amount = st.number_input("Amount ($)", 1.0, 100000.0, 150.75)
                country = st.selectbox("Originating Country", ["USA", "Canada", "UK", "Germany", "Nigeria", "China", "Brazil"])
                user_device = st.radio("User Device", ["Mobile", "Desktop", "Tablet"], horizontal=True)

                if st.button("🔍 Analyze Transaction"):
                    is_fraud = False
                    reason = "No activity detected."

                    # --- Simulated Fraud Detection Logic ---
                    if amount > 5000 and country != "USA":
                        is_fraud = True
                        reason = "High value transaction from an country."
                    elif user_device == "Mobile" and amount > 1000 and country == "Nigeria":
                        is_fraud = True
                        reason = "Suspicious high-value mobile transaction from high-risk country."
                    elif transaction_id == "FRAUD123":
                        is_fraud = True
                        reason = "Known suspicious transaction ID."
                    elif user_id == "BOT_USER":
                        is_fraud = True
                        reason = "Associated with known bot activity."

                    st.markdown("<br>", unsafe_allow_html=True)

                    if is_fraud:
                        st.error(f"🚨 **FRAUD ALERT!**\n\n**Reason:** {reason}")
                    else:
                        st.success(f"✅ **Transaction is Clean.**\n\n**Reason:** {reason}")

                    with st.expander("📄 View Simulated Log Data"):
                        st.json({
                            "timestamp": "2023-10-27T14:35:00Z",
                            "transaction_id": transaction_id,
                            "user_id": user_id,
                            "amount": amount,
                            "currency": "USD",
                            "ip_address": "192.168.1.100" if not is_fraud else "203.0.113.42",
                            "country": country,
                            "user_device": user_device,
                            "session_duration_s": 300,
                            "payment_method": "Credit Card",
                            "is_fraud_flag": is_fraud,
                            "detection_reason": reason
                        })

    # --- Close custom container ---
    st.markdown("</div>", unsafe_allow_html=True)


elif st.session_state.active_page == "About":

    
    # --- Page Config ---
    st.set_page_config(page_title="AURA - UPS Fraud Detection", layout="wide")

    # --- Custom CSS for Title ---
    st.markdown("""
        <style>
        .project {
            font-size: 2.2rem;
            font-weight: 800;
            text-align: center;
            color: #212529;
            margin-top: 20px;
            animation: fadeInUp 1s ease-in-out;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Project Header ---
    st.markdown('<div class="project">🚚 UPS Fraud Detection – Project Overview</div>', unsafe_allow_html=True)

    # --- Cards Section ---
    cards_html = """
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>
    .card-container {
        display: flex;
        flex-wrap: wrap;
        gap: 30px;
        justify-content: center;
        margin-top: 20px;
    }

    .card-custom {
        width: 340px;
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
        overflow: hidden;
        transition: transform 0.3s ease-in-out;
    }

    .card-custom:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 20px rgba(0, 0, 0, 0.15);
    }

    .card-img-top {
        width: 100%;
        height: 180px;
        object-fit: cover;
    }

    .card-body {
        padding: 20px;
    }

    .card-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #212529;
        margin-bottom: 10px;
    }

    .card-text {
        font-size: 0.95rem;
        color: #555;
        line-height: 1.6;
    }
    </style>

    <div class="card-container">

        <div class="card-custom">
            <img src="https://tse1.mm.bing.net/th/id/OIP.Hus7dYeIuEGhoPfBlmsZ5QHaE8?w=768&h=512&rs=1&pid=ImgDetMain&o=7&rm=3" class="card-img-top" alt="UPS Delivery">
            <div class="card-body">
                <div class="card-title">📌 Business Problem</div>
                <p class="card-text">
                    UPS seeks to automate fraud detection by analyzing logs intelligently. Manual review of user activity logs is time-consuming and costly.
                </p>
            </div>
        </div>

        <div class="card-custom">
            <img src="https://static.vecteezy.com/system/resources/previews/015/540/944/non_2x/free-express-home-or-fast-delivery-service-by-van-car-with-stack-of-parcels-and-smartphone-with-mobile-app-for-online-delivery-tracking-flat-style-illustration-vector.jpg" class="card-img-top" alt="UPS Automation">
            <div class="card-body">
                <div class="card-title">⚙️ Goal of the Project</div>
                <p class="card-text">
                    Automatically parse logs to detect patterns such as shipment timings, user/device anomalies, and identify potential fraud triggers.
                </p>
            </div>
        </div>

        <div class="card-custom">
            <img src="https://www.taxscan.in/wp-content/uploads/2023/08/CESTAT-CESTAT-Quashes-Demand-of-Customs-Duty-Demand-of-Customs-Duty-Customs-Duty-CESTAT-Quashes-Demand-of-Customs-Duty-Imposed-for-Import-of-Car-Electronic-Goods-tascsan.jpg" class="card-img-top" alt="UPS Data">
            <div class="card-body">
                <div class="card-title">📊 Key Considerations</div>
                <p class="card-text">
                    Download logs, apply AI parsing, detect abnormal activity like too many actions in a short window or suspicious geolocations.
                </p>
            </div>
        </div>

        <div class="card-custom">
            <img src="https://tse4.mm.bing.net/th/id/OIP.FAxnxvBLNE3WPEMBq7R5AAHaFi?w=702&h=525&rs=1&pid=ImgDetMain&o=7&rm=3" class="card-img-top" alt="UPS Global">
            <div class="card-body">
                <div class="card-title">🌍 Shipper Behavior Profiling</div>
                <p class="card-text">
                    Build shipper profiles to spot changes — e.g., a domestic-only shipper suddenly initiating international shipments triggers a flag.
                </p>
            </div>
        </div>

    </div>
    """

    components.html(cards_html, height=400, scrolling=True)

    # --- Spacer Between Cards & Accordion ---
    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)

    # --- Accordion Section ---
    with st.container():
        st.markdown("### 🔍 Learn More About AURA", unsafe_allow_html=True)

        accordion_html = """ 
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">

        <style>
            .accordion-wrapper {
                padding: 40px 20px;
                background: linear-gradient(to right, #fdfbfb, #ebedee);
                border-radius: 16px;
                max-width: 960px;
                margin: auto;
                box-shadow: 0 6px 24px rgba(0, 0, 0, 0.08);
                font-family: 'Segoe UI', sans-serif;
                font-size: 18px;
                animation: fadeInSlide 1s ease;
            }

            @keyframes fadeInSlide {
                0% { opacity: 0; transform: translateY(40px); }
                100% { opacity: 1; transform: translateY(0); }
            }

            .accordion-button {
                font-size: 20px;
                font-weight: bold;
            }

            .accordion-body {
                font-size: 18px;
                line-height: 1.75;
                padding-top: 10px;
            }
        </style>

        <div class="accordion-wrapper">
            <div class="accordion" id="auraAccordion">

                <div class="accordion-item">
                    <h2 class="accordion-header" id="headingOne">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                            data-bs-target="#collapseOne" aria-expanded="false" aria-controls="collapseOne">
                            <i class="bi bi-shield-lock-fill me-2 text-primary"></i> Business Problem
                        </button>
                    </h2>
                    <div id="collapseOne" class="accordion-collapse collapse" aria-labelledby="headingOne"
                        data-bs-parent="#auraAccordion">
                        <div class="accordion-body">
                            UPS seeks to reduce manual effort in log analysis for fraud detection. Manual scanning of logs is time-consuming, error-prone, and inefficient.
                            Automating this process could save thousands of analyst hours annually, and enable real-time alerts.
                            AI-based solutions can look for anomalies in user activity patterns and flag them immediately.
                            The goal is to create a smart, scalable fraud detection system.
                            This ensures safer logistics and higher trust in global shipping operations.
                        </div>
                    </div>
                </div>

                <div class="accordion-item">
                    <h2 class="accordion-header" id="headingTwo">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                            data-bs-target="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">
                            <i class="bi bi-gear-fill me-2 text-success"></i> Project Goals
                        </button>
                    </h2>
                    <div id="collapseTwo" class="accordion-collapse collapse" aria-labelledby="headingTwo"
                        data-bs-parent="#auraAccordion">
                        <div class="accordion-body">
                            The AURA project aims to automate fraud detection by analyzing UPS application logs.
                            It will extract signals such as geolocation mismatches, high-frequency interactions, or known risky users.
                            The system will also learn normal user behavior patterns and alert when deviations occur.
                            Alerts will be ranked by risk and explained using human-readable reasoning.
                            This results in faster investigations and fewer missed fraudulent cases.
                        </div>
                    </div>
                </div>

                <div class="accordion-item">
                    <h2 class="accordion-header" id="headingThree">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                            data-bs-target="#collapseThree" aria-expanded="false" aria-controls="collapseThree">
                            <i class="bi bi-binoculars-fill me-2 text-danger"></i> Key Considerations
                        </button>
                    </h2>
                    <div id="collapseThree" class="accordion-collapse collapse" aria-labelledby="headingThree"
                        data-bs-parent="#auraAccordion">
                        <div class="accordion-body">
                            <ul>
                                <li>Support log file parsing in `.txt` or `.log` format</li>
                                <li>Detect anomalies like device/IP mismatch or burst activity</li>
                                <li>Model typical user behavior and compare in real time</li>
                                <li>Generate alerts with risk scores and detailed reasoning</li>
                                <li>Dashboard for viewing flagged cases and reviewing logs</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="accordion-item">
                    <h2 class="accordion-header" id="headingFour">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                            data-bs-target="#collapseFour" aria-expanded="false" aria-controls="collapseFour">
                            <i class="bi bi-person-lines-fill me-2 text-warning"></i> Shipper Behavior Profiling
                        </button>
                    </h2>
                    <div id="collapseFour" class="accordion-collapse collapse" aria-labelledby="headingFour"
                        data-bs-parent="#auraAccordion">
                        <div class="accordion-body">
                            Each shipper will be assigned a unique profile capturing their normal shipping activity.
                            The AI engine will monitor frequency, destination zones, package volume, and timing.
                            Activity like international shipments by domestic-only shippers gets flagged.
                            The shipper profile grows smarter over time using historical data.
                            This profiling helps reduce false positives and increases fraud accuracy.
                        </div>
                    </div>
                </div>

            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        """

        components.html(accordion_html, height=950, scrolling=True)


elif st.session_state.active_page == "Policy":
   


    # --- GCP Config ---
    GCP_PROJECT_ID = "sqwiklabs-gcp-04-991e2d63cfb0"
    GCS_BUCKET_NAME = "automated_risk_analysis"

    # --- SweetAlert Function ---
    def sweet_alert(message, icon="success"):
        components.html(f"""
            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
            <script>
                Swal.fire({{
                    icon: '{icon}',
                    title: `{message}`,
                    confirmButtonColor: '#3085d6',
                    confirmButtonText: 'OK'
                }})
            </script>
        """, height=0)


    # --- GCS Helper Functions ---
    def check_file_exists(bucket_name, file_name):
        client = storage.Client(project=GCP_PROJECT_ID)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        try:
            blob.reload()
            return True
        except NotFound:
            return False

    def upload_file_to_gcs(bucket_name, file_name, file_content):
        client = storage.Client(project=GCP_PROJECT_ID)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.upload_from_string(file_content)
        return True


    # --- Initialize Session State ---
    if "upload_result" not in st.session_state:
        st.session_state.upload_result = None

    if "button_disabled" not in st.session_state:
        st.session_state.button_disabled = False


    # --- Page Title & Header ---
    st.markdown("""
    <style>
    .project-header {
        font-size: 2.2rem;
        font-weight: 800;
        text-align: center;
        color: #212529;
        margin-top: 20px;
        animation: fadeInUp 1s ease-in-out;
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)

    # st.markdown('<div class="project-header">🚚 Rego Policy Generator </div>', unsafe_allow_html=True)


    # --- Upload Section Card ---
    st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <div class="card shadow-sm border-warning mb-4" style="width: 100%; border-radius: 10px;">
        <div class="card-header bg-warning text-dark fw-bold fs-4" style="padding: 20px;">
            🛡️ Rego Policy Generator
        </div>
        <div class="card-body" style="padding: 25px; font-size: 1rem; color: #333;">
            <p>When you upload a log file here, it kicks off a <strong>smart chain of actions</strong>:</p>
            <ul>
                <li>🧠 <strong>Agent REGEN</strong> scans your logs for suspicious patterns and <strong>auto-generates Rego policies</strong>.</li>
                <li>🛡️ <strong>Agent REVA</strong> applies these policies to monitor all future logs you upload.</li>
                <li>🔁 The more logs you upload, the <strong>smarter and stricter</strong> the system becomes!</li>
            </ul>
            <p class="fw-bold mt-3">Ready to expose the fraud? <br> <strong>Drop your log file now!</strong></p>
        </div>
    </div>
    """, unsafe_allow_html=True)


    
        

        
    SERVICE_ACCOUNT_JSON = "qwiklabs-gcp-04-991e2d63cfb0-424e0d2468ef.json"
    GCS_BUCKET_NAME = "automated_risk_analysis"
    GCS_UPLOAD_PATH = "automated_risk_analysis/api_responses/logs-to-refer/"
    API_URL = "https://agent-regen-748112393466.us-central1.run.app"

    # --- Create GCS Client ---
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_JSON)
    client = storage.Client(credentials=credentials, project=credentials.project_id)

    def upload_json_to_gcs(bucket_name, blob_name, json_data):
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(json.dumps(json_data), content_type="application/json")
        return blob.public_url



    if st.button("🔄 Fetch API & Upload to GCS"):
        with st.spinner("⏳ Fetching data and uploading to GCS... Please wait"):
            try:
                response = requests.get(API_URL)
                if response.status_code == 200:
                    st.success("✅ API Request Successful!")

                    api_data = response.json()

                    # Generate timestamped filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    blob_name = f"{GCS_UPLOAD_PATH}api_response_{timestamp}.json"

                    public_url = upload_json_to_gcs(GCS_BUCKET_NAME, blob_name, api_data)

                    st.success("✅ JSON Uploaded Successfully to the following source:")
                    st.code(f"gs://{GCS_BUCKET_NAME}/{blob_name}")

                else:
                    st.error(f"❌ API Request Failed. Status Code: {response.status_code}")
            except Exception as e:
                st.error(f"❗ Error: {e}")

   
    




elif st.session_state.active_page == "Logic":
    st.markdown("## 📦 UPS Business Logic")
    st.markdown("""
    - Detect sudden international shipments from domestic-only users.
    - Monitor routing deviations.
    - Packages unexpectedly rerouted mid-transit or delivered to unlisted addresses.
    - Routing that deviates from optimized courier paths without justification.
    """)
    st.markdown("---")

    st.markdown("""
    <style>
    @keyframes fadeSlideUp {
    0% {
        opacity: 0;
        transform: translateY(20px);
    }
    100% {
        opacity: 1;
        transform: translateY(0px);
    }
    }

    .card-section {
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 16px 24px;
        margin-bottom: 20px;
        background-color: #fdfdfd;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        animation: fadeSlideUp 0.6s ease-in-out;
    }
    .card-section h4 {
        margin-top: 0;
        margin-bottom: 12px;
        color: #2c3e50;
        font-size: 20px;
    }
    .card-section ul {
        padding-left: 20px;
    }
    .card-section li {
        margin-bottom: 6px;
        font-size: 15px;
        line-height: 1.5;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Card function ---
    def card_section(title, bullets):
        bullet_list = "".join(f"<li>{b}</li>" for b in bullets)
        st.markdown(f"""
        <div class="card-section">
            <h4>{title}</h4>
            <ul>{bullet_list}</ul>
        </div>
        """, unsafe_allow_html=True)

    # --- UPS Business Logic Sections ---
    card_section("🌍 Geographic & Location-Based", [
        "📍 Detect sudden international shipments from previously domestic-only users.",
        "🌐 Monitor routing deviations or detours from expected delivery paths.",
        "📌 Flag orders originating far from prior delivery history (geo-anomalies).",
        "✈️ Detect same-day logins from distant cities (impossible travel patterns)."
    ])

    card_section("🚚 Logistics & Package Behavior", [
        "🚚 Alert on rapid address changes after payment confirmation.",
        "🧭 Identify repeated usage of pickup/drop locations with known fraud history.",
        "🕒 Track manipulation of delivery windows (delay or force reroute behavior).",
        "🎁 Watch forly high declared values for small/lightweight packages."
    ])

    card_section("📱 Device & Access Patterns", [
        "📲 Detect rapid device changes mid-session (e.g., iOS → Android).",
        "🌐 Monitor IP address switching within a session or between logins.",
        "🕵️‍♂️ Identify logins from Tor, VPNs, or flagged anonymized networks.",
        "📱 Detect same device being used across multiple accounts."
    ])

    card_section("💳 Payments & Transactions", [
        "💳 Monitor excessive payment failures or retries with different cards.",
        "🎟️ Detect patterns of gift card fraud or disposable payment methods.",
        "🧾 Identify refunds initiated before delivery attempt.",
        "🏠 Flag mismatched billing and delivery addresses."
    ])

    card_section("👤 Account Behavior & Trust Signals", [
        "📈 Alert on sudden order spikes after long inactivity.",
        "🕒 Detect behavior inconsistent with profile age (e.g., new account with bulk orders).",
        "📧 Watch for repeated sign-up attempts using email variations (e.g., john1, john2).",
        "🔑 Detect frequent password resets and login attempts outside normal hours."
    ])

    card_section("🔁 Return & Refund Exploits", [
        "🔄 Flag accounts with excessive return rates across categories.",
        "📦 Detect repeat returners using \"item not received\" claims.",
        "💱 Identify patterns of item-swapping with lower value items during returns."
    ])

    card_section("🔄 Operational Misuse & Insider Activity", [
        "🚨 Monitor courier rerouting to third-party delivery providers.",
        "🧑‍💼 Flag excessive manual overrides by internal users (insider fraud).",
        "🔁 Detect same-day return attempts without delivery scans."
    ])

    # --- Image URLs for Business Logic Visuals ---
    image_urls = [
        "https://static.vecteezy.com/system/resources/previews/035/879/159/non_2x/delivery-service-concept-moving-house-family-moving-concept-happy-cartoon-couple-carries-things-out-of-the-truck-man-holding-box-relocate-to-new-home-or-office-illustration-in-flat-style-vector.jpg",
        "https://cdn.prod.website-files.com/660e658d0cfb31720d8934d0/670946a824f2fe2baa3ffc5e_66bc6b078f4e6db2ecb6ba8a_UPS-Overnight-guide.png",
        "https://www.ups.com/in/en/shipping/media_1f460855f5f3d170a2e678c351e57b4b35b6eb19b.webp?width=750&format=webp&optimize=medium",
        "https://img.freepik.com/premium-vector/customer-using-mobile-app-tracking-order-delivery-vector-illustration_327176-57.jpg",
        "https://img.freepik.com/premium-vector/warehouse-workers-loading-stacking-goods-with-electric-lifters-delivery-car-forklift-truck-with-driver-electric-uploader-industrial-logistics-delivery-service-merchandising-business_458444-1586.jpg"
    ]

    # --- Initialize Session State for Index ---
    if "img_index" not in st.session_state:
        st.session_state.img_index = 0

    # --- Navigation Buttons ---
    st.markdown("<div style='margin-top: 20px;'>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


    # --- Display Selected Image ---
    # st.image(image_urls[st.session_state.img_index], use_column_width=True, caption=f"Slide {st.session_state.img_index + 1} of {len(image_urls)}")
    st.image(image_urls[st.session_state.img_index], use_container_width=True, caption=f"Slide {st.session_state.img_index + 1} of {len(image_urls)}")
    
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("⬅️ Previous", use_container_width=True):
            st.session_state.img_index = (st.session_state.img_index - 1) % len(image_urls)

    with col3:
        if st.button("Next ➡️", use_container_width=True):
            st.session_state.img_index = (st.session_state.img_index + 1) % len(image_urls)
    # --- Horizontal Scrollable Business Logic Cards ---
    st.markdown("### 🧠 Core UPS Fraud Scenarios")

    st.markdown("""
    <style>
    .card-container {
        display: flex;
        overflow-x: auto;
        gap: 1.5rem;
        padding: 1rem 0;
    }
    .card {
        flex: 0 0 auto;
        width: 320px;
        background-color: #f9f9f9;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 1rem;
    }
    .card img {
        width: 100%;
        border-radius: 8px;
    }
    .card h4 {
        margin-top: 0.5rem;
        color: #333333;
    }
    .card p {
        font-size: 0.92rem;
        color: #555555;
    }
    </style>

    <div class="card-container">

    <div class="card">
        <img src="https://hostmerchantservices.com/wp-content/uploads/2024/04/3-22-1024x493.jpg" />
        <h4>Velocity-Based Fraud</h4>
        <p>High volume of orders in short intervals, often by new or untrusted accounts.</p>
    </div>

    <div class="card">
        <img src="https://cdn.prod.website-files.com/64a6f67b79a80fd9ff31ca7a/6620f4759794469d353769e9_retail%20digital%20transformation.png" />
        <h4>Geographic Anomalies</h4>
        <p>Orders from regions inconsistent with customer history or too far apart in short times.</p>
    </div>

    <div class="card">
        <img src="https://images.purevpn-tools.com/public/images/Unplug-your-modem-to-change-your-IP-address-purevpn-vpn.png" />
        <h4>Device/IP Inconsistencies</h4>
        <p>Multiple IPs or devices used in a single session may indicate account misuse.</p>
    </div>

    <div class="card">
        <img src="https://chargebacks911.com/wp-content/uploads/2025/06/Sub-Account-Takeover-Ch5.jpg" />
        <h4>Delivery Address Tampering</h4>
        <p>Address changes that redirect packages unexpectedly or repeatedly raise risk flags.</p>
    </div>

    <div class="card">
        <img src="https://en.sangritimes.com/uploads/images/202505/image_1600x_68368cc59010f.webp" />
        <h4>Payment Method Abuse</h4>
        <p>Frequent failed transactions, excessive card switching or flagged payment instruments.</p>
    </div>

    <div class="card">
        <img src="https://www.idstrong.com/img/v4/topical/account_takeover_01.jpg" />
        <h4>Account Takeover</h4>
        <p>Unauthorized access through leaked credentials, social engineering or brute force attempts.</p>
    </div>

    <div class="card">
        <img src="https://cdn.mos.cms.futurecdn.net/biAxWbVb6Ft4qg3Z5ygH8C.jpg" />
        <h4>Behavioral Anomalies</h4>
        <p>Unusual navigation, excessive API calls or irregular ordering behavior detected.</p>
    </div>

    <div class="card">
        <img src="https://disk.com/wp-content/uploads/2023/10/1698350976.jpg" />
        <h4>Delivery Logistics Misuse</h4>
        <p>Changing routes, unauthorized handovers or policy exploitation in shipping routines.</p>
    </div>

    <div class="card">
        <img src="https://theretailtimes.co.in/wp-content/uploads/2021/09/Unicommerce-unveils-new-version-of-its-returns-management-solution.jpg" />
        <h4>Refund/Return Exploits</h4>
        <p>Unusually high return rates, refund claims or mismatch between item value and returns.</p>
    </div>

    </div>
    """, unsafe_allow_html=True)

elif st.session_state.active_page == "Customer":
    
    # Global Fraud Watch Header with Soft Background
    st.markdown("""
    <div style="
        background: #fffbe6;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #ffd700;
        text-align: center;
        margin-bottom: 20px;
    ">

    <h2 style="
        font-size: 28px;
        font-weight: 900;
        color: rgb(51, 0, 0);
        margin-bottom: 10px;
    ">
    🌐 Global Fraud Watch
    </h2>

    <p style="
        font-size: 16px;
        color: rgb(51, 0, 0);
        font-weight: 500;
    ">
    Keeping you ahead of emerging fraud trends across regions and sectors.<br><br>
    <b>Stay Vigilant. Stay Ahead.</b>
    </p>

    <p style="
        font-size: 16px;
        color: rgb(51, 0, 0);
        font-weight: 500;
    ">
    
    </p>

    </div>
    """, unsafe_allow_html=True)

 # Global Button Styling for UPS Theme with Click Effect
    st.markdown("""
    <style>
    div.stButton > button {
        background-color: rgba(51, 0, 0, 1);
        color: white;
        padding: 10px 25px;
        font-size: 16px;
        border: 2px solid #ffd700;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: 0.3s;
    }

    /* Hover effect */
    div.stButton > button:hover {
        background-color: #ffd700;
        color: black;
    }

    /* Active (Click) effect */
    div.stButton > button:active {
        background-color: white;
        color: rgba(51, 0, 0, 1);
        border: 2px solid rgba(51, 0, 0, 1);
    }
    </style>
    """, unsafe_allow_html=True)

    # Centered Button
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        if st.button("🔎 Get Global Frauds", key="get_fraud_regions"):
            SERVICE_ACCOUNT_JSON = "qwiklabs-gcp-04-991e2d63cfb0-424e0d2468ef.json"
            GCS_BUCKET_NAME = "automated_risk_analysis"
            GCS_UPLOAD_PATH = "automated_risk_analysis/api_responses/logistic_frauds/"
            API_URL = "https://agent-reva-748112393466.us-central1.run.app"

            # --- GCS Client ---
            credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_JSON)
            client = storage.Client(credentials=credentials, project=credentials.project_id)

            def upload_json_to_gcs(bucket_name, blob_name, json_data):
                bucket = client.bucket(bucket_name)
                blob = bucket.blob(blob_name)
                blob.upload_from_string(json.dumps(json_data), content_type="application/json")
                return blob.public_url

            with st.spinner("⏳ Fetching data and uploading to GCS... Please wait"):
                try:
                    response = requests.get(API_URL)
                    if response.status_code == 200:
                        st.success("✅ API Request Successful!")

                        api_data = response.json()

                        # Generate timestamped filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        blob_name = f"{GCS_UPLOAD_PATH}fraud_{timestamp}.json"

                        public_url = upload_json_to_gcs(GCS_BUCKET_NAME, blob_name, api_data)

                        st.success("✅ JSON Uploaded Successfully to the following source:")
                        st.code(f"gs://{GCS_BUCKET_NAME}/{blob_name}")

                    else:
                        st.error(f"❌ API Request Failed. Status Code: {response.status_code}")
                except Exception as e:
                    st.error(f"❗ Error: {e}")
                    st.success("Fetching fraud-prone regions... ✅ (Placeholder action)")

    


elif st.session_state.active_page == "Analytics":
    # st.markdown("## 📊 Analytics")
    

    # --- Upload Section ---
    st.header("📁 Upload Logs")
    log_file = st.file_uploader("Upload fraud_detection_logs file (.txt or .json)", type=["txt", "json"])

    # --- Clean & Extract JSON ---
    def extract_valid_json(raw_text):
        try:
            start_idx = raw_text.find('{')
            end_idx = raw_text.rfind('}') + 1
            trimmed_text = raw_text[start_idx:end_idx]
            while end_idx > start_idx:
                try:
                    return json.loads(trimmed_text)
                except json.JSONDecodeError:
                    end_idx -= 1
                    trimmed_text = raw_text[start_idx:end_idx]
        except Exception as e:
            st.error(f"❌ Could not extract JSON: {e}")
        return None

    # --- Parse Data into DataFrames ---
    def parse_logs(data):
        user_records = []
        session_records = []
        event_records = []

        for user in data["fraud_detection_logs"]["users"]:
            profile = user["user_profile"]
            user_records.append({
                "uid": user["uid"],
                "email": profile["email"],
                "account_age_days": profile["account_age_days"],
                "total_orders": profile["total_orders"],
                "risk_score": user["risk_score"],
                "fraud_scenario": user["fraud_scenario"]
            })

            for session in user["sessions"]:
                session_records.append({
                    "uid": user["uid"],
                    "session_id": session["session_id"],
                    "start_time": session["start_time"],
                    "end_time": session["end_time"],
                    "duration_minutes": session["duration_minutes"],
                    "city": session["network_info"]["location"]["city"]
                })

                for event in session["events"]:
                    event_records.append({
                        "uid": user["uid"],
                        "session_id": session["session_id"],
                        "timestamp": event["timestamp"],
                        "event_type": event["event_type"],
                        "order_value": event.get("details", {}).get("declared_value", 0)
                    })

        return pd.DataFrame(user_records), pd.DataFrame(session_records), pd.DataFrame(event_records)

    # --- Main Execution ---
    if log_file:
        raw_text = log_file.read().decode('utf-8')
        parsed_data = extract_valid_json(raw_text)

        if parsed_data:
            df_users, df_sessions, df_events = parse_logs(parsed_data)

            # --- Metrics ---
            st.header("🔍 Overview Metrics")
            col1, col2, col3 = st.columns(3)
            col1.metric("👥 Total Users", len(df_users))
            col2.metric("⚠️ Avg Risk Score", round(df_users["risk_score"].mean(), 2))
            col3.metric("📦 Total Orders", df_users["total_orders"].sum())

            # --- Risk Score Box Plot ---
            st.subheader("📊 Risk Score Distribution by Fraud Scenario")
            fig1 = px.box(df_users, x="fraud_scenario", y="risk_score", color="fraud_scenario")
            st.plotly_chart(fig1, use_container_width=True)

            # --- Session Duration Histogram ---
            st.subheader("⏱️ Session Duration by City")
            fig2 = px.histogram(df_sessions, x="city", y="duration_minutes", color="uid", barmode="group")
            st.plotly_chart(fig2, use_container_width=True)

            # --- Order Timeline ---
            st.subheader("📦 Order Value Timeline")
            df_events['timestamp'] = pd.to_datetime(df_events['timestamp'])
            order_events = df_events[df_events["event_type"] == "order_create"]
            fig3 = px.line(order_events.sort_values("timestamp"), x="timestamp", y="order_value", color="uid", markers=True)
            st.plotly_chart(fig3, use_container_width=True)

            # --- Users Table ---
            st.subheader("🧾 Users by Risk Score")
            st.dataframe(df_users.sort_values("risk_score", ascending=False))

            # --- High Value Orders Table ---
            st.subheader("🔎 Suspicious High-Value Orders (₹40K+)")
            high_value = order_events[order_events["order_value"] > 40000]
            st.dataframe(high_value.sort_values("order_value", ascending=False))

            # --- Scatter Plot: Account Age vs Risk Score ---
            st.subheader("📈 Scatter: Account Age vs Risk Score")
            fig4 = px.scatter(df_users, x="account_age_days", y="risk_score", color="fraud_scenario",
                            size="total_orders", hover_name="uid", title="Account Age vs Risk Score")
            st.plotly_chart(fig4, use_container_width=True)

            # --- Histogram: Declared Order Values ---
            st.subheader("📊 Declared Order Values Histogram")
            fig5 = px.histogram(order_events, x="order_value", nbins=30, title="Histogram of Order Values",
                                color="uid")
            st.plotly_chart(fig5, use_container_width=True)

            # --- Count Plot: Event Types ---
            st.subheader("📌 Event Type Frequency")
            fig6 = px.histogram(df_events, x="event_type", color="uid", title="Event Type Distribution",
                                barmode="group")
            st.plotly_chart(fig6, use_container_width=True)

        else:
            st.error("❌ Could not extract valid JSON from the file.")
    else:
        st.info("👈 Upload your `.txt` or `.json` file with fraud logs to get started.")




elif st.session_state.active_page == "Upload":
    

    st.markdown("""
    ## 📁 **Upload Logs**  
    """)
    st.warning("🛠️ *Coming Soon — Beta Preview Available*")

    uploaded = st.file_uploader("📤 **Upload a Log File** _(Supported: .txt, .log)_", type=["txt", "log"])

    if uploaded:
        st.success("✅ **File Uploaded Successfully! Preview Below:**")

        content = uploaded.read().decode("utf-8")

        with st.spinner("⏳ Processing data for detecting the fraud... Please wait"):
            time.sleep(10)  # Simulate 10-second delay
            st.text_area("📃 **Log File Preview (First 500 characters)**", value=content[:500], height=150)

        st.markdown("---")

        try:
            data = json.loads(content)
            users = data['fraud_detection_logs']['users']

            fraud_users = []
            legit_users = []

            for user in users:
                entry = {
                    "User ID": user['uid'],
                    "Scenario": user['fraud_scenario'],
                    "Risk Score": user['risk_score']
                }
                if user['fraud_scenario'] == "normal_behavior":
                    legit_users.append(entry)
                else:
                    fraud_users.append(entry)

            st.markdown("### 🚨 **Fraudulent Users Detected**")
            if fraud_users:
                st.dataframe(fraud_users, use_container_width=True)
            else:
                st.success("✅ No Fraudulent Users Detected.")

            st.markdown("### ✅ **Legitimate Users**")
            if legit_users:
                st.dataframe(legit_users, use_container_width=True)
            else:
                st.info("ℹ️ No Legitimate Users Found.")

        except Exception as e:
            st.error(f"❌ **Failed to parse log file.** Please ensure it is a valid JSON format.\n\n**Error:** {e}")

    else:
        st.info("📥 *Please upload a valid log file to begin analysis.*")

    
# Footer
st.markdown("""
<br><hr>
<div style="text-align:center; color:#555; font-size:0.85rem;">
    &copy; 2025 AURA. Powered by Streamlit & AI. | <a href="#" style="color:#888;">Privacy</a> | <a href="#" style="color:#888;">Terms</a>
</div>
""", unsafe_allow_html=True)
