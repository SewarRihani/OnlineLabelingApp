import streamlit as st
import pandas as pd
import os
import glob

# === CONFIG ===
AUDIO_DIR = "data"
SUPPORTED_FORMATS = (".wav", ".mp3")

# === Get All Audio Files ===
audio_files = sorted(glob.glob(f"{AUDIO_DIR}/**/*", recursive=True))
audio_files = [f for f in audio_files if f.endswith(SUPPORTED_FORMATS)]

# === SESSION STATE INIT ===
if 'index' not in st.session_state:
    st.session_state.index = 0
if 'labels' not in st.session_state:
    st.session_state.labels = []
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

# === UI ===
st.title("🎧 Online Labeling App")
st.subheader("Label cat and dog sounds as Positive, Negative, or Unknown.")
st.markdown("---")

# === Upload CSV (optional)
uploaded_file = st.file_uploader("📂 Upload your previous label file to continue (optional):", type="csv")
if uploaded_file and uploaded_file.name not in st.session_state.uploaded_files:
    df = pd.read_csv(uploaded_file)
    st.session_state.labels = df.to_dict('records')
    st.session_state.uploaded_files.append(uploaded_file.name)
    st.session_state.index = 0
    st.success(f"✅ Progress file loaded: {len(df)} files already labeled.")
    st.info("Continuing where you left off — previously labeled files will be skipped.")

# === Filter labeled
labeled_files = {entry['file'] for entry in st.session_state.labels}
audio_files = [f for f in audio_files if os.path.basename(f) not in labeled_files]
total_remaining = len(audio_files)

# === Done?
if st.session_state.index >= total_remaining:
    st.success("✅ All files labeled! Download your final CSV below.")
    final_df = pd.DataFrame(st.session_state.labels)
    st.download_button(
        label="📁 Download final CSV",
        data=final_df.to_csv(index=False),
        file_name="labels_progress.csv",
        mime="text/csv"
    )
    st.stop()

# === Current file
file_path = audio_files[st.session_state.index]
file_name = os.path.basename(file_path)
species = "CAT" if "cat" in file_path.lower() else "DOG"

st.markdown(f"### {species.upper()} • {file_name}")
st.markdown(f"**{st.session_state.index + 1} / {total_remaining} files**")
st.progress(st.session_state.index / total_remaining)

try:
    with open(file_path, 'rb') as f:
        st.audio(f.read())
except Exception as e:
    st.warning(f"⚠️ Couldn't load audio: {e}")

# === Save Function
def label_and_continue(label):
    st.session_state.labels.append({
        "file": file_name,
        "species": species,
        "label": label
    })
    st.session_state.index += 1
    st.rerun()

# === Buttons
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("😊 Positive"):
        label_and_continue("positive")
with col2:
    if st.button("😠 Negative"):
        label_and_continue("negative")
with col3:
    if st.button("❓ Unknown"):
        label_and_continue("unknown")

# === Download progress at any time
if st.session_state.labels:
    st.markdown("---")
    st.download_button(
        label="💾 Download progress CSV",
        data=pd.DataFrame(st.session_state.labels).to_csv(index=False),
        file_name="labels_progress.csv",
        mime="text/csv"
    )
