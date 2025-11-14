import streamlit as st
import pandas as pd
import os
import glob

# === CONFIG ===
AUDIO_DIR = "data"
OUTPUT_FOLDER = "labels"
SUPPORTED_FORMATS = (".wav", ".mp3")

# === SETUP ===
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Get Audio Files ===
audio_files = sorted(glob.glob(f"{AUDIO_DIR}/**/*", recursive=True))
audio_files = [f for f in audio_files if f.endswith(SUPPORTED_FORMATS)]
total_files = len(audio_files)

# === SESSION STATE ===
if 'index' not in st.session_state:
    st.session_state.index = 0
if 'labels' not in st.session_state:
    st.session_state.labels = []
if 'username' not in st.session_state:
    st.session_state.username = ""

# === UI ===
st.title("🎿 Online Labeling App")
st.subheader("Label cat and dog sounds as Positive, Negative, or Unknown.")

# === User Input for Name ===
if not st.session_state.username:
    name = st.text_input("Enter your name to start:", key="username_input")
    if name:
        st.session_state.username = name.strip()
        st.rerun()
    else:
        st.stop()

# === File uploader for previous CSV ===
st.markdown("---")
uploaded_file = st.file_uploader("📂 Upload your previous label file to continue (optional):", type="csv")

# === If CSV is uploaded, reset session and resume from that file
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    labeled_files = df['file'].tolist()
    st.session_state.labels = df.to_dict('records')
    st.session_state.index = 0
    audio_files = [f for f in audio_files if os.path.basename(f) not in labeled_files]
    st.rerun()

# === Local fallback if no file uploaded
user_file = os.path.join(OUTPUT_FOLDER, f"{st.session_state.username}.csv")
labeled_files = []
if not st.session_state.labels and os.path.exists(user_file):
    df = pd.read_csv(user_file)
    labeled_files = df['file'].tolist()
    st.session_state.labels = df.to_dict('records')

# === Filter Remaining Files ===
audio_files = [f for f in audio_files if os.path.basename(f) not in labeled_files]
total_remaining = len(audio_files)

# === End App if Done ===
if st.session_state.index >= total_remaining:
    st.success("✅ All files labeled! Thank you.")
    final_df = pd.DataFrame(st.session_state.labels)
    final_df.to_csv(user_file, index=False)
    st.download_button("📥 Download your full labels", final_df.to_csv(index=False), file_name=f"{st.session_state.username}_labels.csv")
    st.stop()

# === CURRENT FILE ===
file_path = audio_files[st.session_state.index]
file_name = os.path.basename(file_path)
species = "CAT" if "cat" in file_path.lower() else "DOG"

st.markdown(f"### {species.upper()} • {file_name}")
st.markdown(f"**{st.session_state.index+1} / {total_remaining} files**")
st.progress(st.session_state.index / total_remaining)

# === Audio Preview ===
try:
    audio_bytes = open(file_path, 'rb').read()
    st.audio(audio_bytes)
except Exception as e:
    st.warning(f"Error playing audio: {e}")

# === Save Progress Immediately
def save_csv():
    pd.DataFrame(st.session_state.labels).to_csv(user_file, index=False)

# === Save & Next
def save_and_next(label):
    st.session_state.labels.append({
        "file": file_name,
        "species": species,
        "label": label
    })
    save_csv()
    st.session_state.index += 1
    st.rerun()

# === Go Back
def go_back():
    if st.session_state.index > 0:
        st.session_state.index -= 1
        st.session_state.labels.pop()
        save_csv()
        st.rerun()

# === LABELING BUTTONS ===
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("😊 Positive"):
        save_and_next("positive")
with col2:
    if st.button("😠 Negative"):
        save_and_next("negative")
with col3:
    if st.button("❓ Unknown"):
        save_and_next("unknown")

# === GO BACK BUTTON ===
if st.session_state.index > 0:
    st.markdown("### ")
    if st.button("🔙 Go Back (Fix Previous Label)"):
        go_back()

# === PROGRESS DOWNLOAD BUTTON (ALWAYS SHOW)
if st.session_state.labels:
    st.download_button(
        "📥 Download progress CSV",
        pd.DataFrame(st.session_state.labels).to_csv(index=False),
        file_name=f"{st.session_state.username}_progress.csv"
    )
