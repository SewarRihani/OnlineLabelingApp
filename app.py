import streamlit as st
import pandas as pd
import os
import glob
import zipfile
import tempfile

# === CONFIG ===
ZIP_PATH = "data/DvC.zip"
AUDIO_DIR = "audio"
OUTPUT_FOLDER = "labels"
SUPPORTED_FORMATS = (".wav", ".mp3")

# === SETUP ===
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Extract ZIP if needed ===
if not os.path.exists(AUDIO_DIR):
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(AUDIO_DIR)

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
st.title("🎧 Online Labeling App")
st.subheader("Label cat and dog sounds as Positive, Negative, or Unknown.")

# === User Input for Name (only once) ===
if not st.session_state.username:
    st.session_state.username = st.text_input("Enter your name to start:")
    st.stop()

# === Resume from Existing File ===
user_file = os.path.join(OUTPUT_FOLDER, f"{st.session_state.username}.csv")
labeled_files = []
if os.path.exists(user_file):
    labeled_df = pd.read_csv(user_file)
    labeled_files = labeled_df['file'].tolist()
    st.session_state.labels = labeled_df.to_dict('records')

# === Filter Remaining Files ===
audio_files = [f for f in audio_files if os.path.basename(f) not in labeled_files]
total_remaining = len(audio_files)

# === End App if Done ===
if st.session_state.index >= total_remaining:
    st.success("✅ All files labeled! Thank you.")
    df = pd.DataFrame(st.session_state.labels)
    df.to_csv(user_file, index=False)
    st.stop()

# === CURRENT FILE ===
file_path = audio_files[st.session_state.index]
file_name = os.path.basename(file_path)
species = "CAT" if "cat" in file_path.lower() else "DOG"

st.markdown(f"### {species.upper()} • {file_name}")
st.markdown(f"**{st.session_state.index+1} / {total_remaining} files**")

# === Audio Preview ===
try:
    audio_bytes = open(file_path, 'rb').read()
    st.audio(audio_bytes)
except Exception as e:
    st.warning(f"Error playing audio: {e}")

# === LABELING BUTTONS ===
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("😊 Positive"):
        st.session_state.labels.append({"file": file_name, "species": species, "label": "positive"})
        st.session_state.index += 1
        st.experimental_rerun()
with col2:
    if st.button("😠 Negative"):
        st.session_state.labels.append({"file": file_name, "species": species, "label": "negative"})
        st.session_state.index += 1
        st.experimental_rerun()
with col3:
    if st.button("❓ Unknown"):
        st.session_state.labels.append({"file": file_name, "species": species, "label": "unknown"})
        st.session_state.index += 1
        st.experimental_rerun()
