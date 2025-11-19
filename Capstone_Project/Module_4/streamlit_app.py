import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import tempfile
import model_inference as model


# --- MAIN STREAMLIT APP ---

# --- PAGE SETUP ---
st.set_page_config(page_title="Multimodal Object Detection", layout="centered")
st.title("🎥 Multimodal Object Detection Demo")

# File uploader
uploaded_file = st.file_uploader(
    "Upload an image or video file",
    type=["jpg", "jpeg", "png", "mp4", "mov", "avi"],
)

# Placeholder for output
output_placeholder = st.empty()

# --- MAIN LOGIC ---
if uploaded_file is not None:
    # Identify file type by MIME
    mime_type = uploaded_file.type

    # Temporary save file (so it can be passed to model_inference)
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_path = temp_file.name

    # --- IMAGE HANDLING ---
    if mime_type.startswith("image"):
        st.subheader("🖼️ Uploaded Image")

        # Processing uploaded image using model_inference
        image = Image.open(temp_path)
        result_image = model.image_inference(image)
        st.image(result_image, caption="Processed Output", use_container_width=True)


    # --- VIDEO HANDLING ---
    elif mime_type.startswith("video"):
        st.subheader("🎬 Uploaded Video")

        # Processing uploaded video using model_inference
        result_video_path, timeline_counts = model.video_inference(temp_path)
        st.video(result_video_path)


        #  Get data for plotting
        times = [row["t"] for row in timeline_counts] # Each row is a frame's worth of data
        cars  = [row["car"] for row in timeline_counts]
        buses = [row["bus"] for row in timeline_counts]
        vans  = [row["van"] for row in timeline_counts]


        # Total detections per class (over entire video)
        total_cars  = sum(cars)
        total_buses = sum(buses)
        total_vans  = sum(vans)

        # Cumulative detections per class (over entire video)
        cum_cars  = np.cumsum(cars)
        cum_buses = np.cumsum(buses)
        cum_vans  = np.cumsum(vans)

        # Cumulative chart over time
        fig, ax = plt.subplots()

        ax.plot(times, cum_cars,  label="Cars (cumulative)")
        ax.plot(times, cum_buses, label="Buses (cumulative)")
        ax.plot(times, cum_vans,  label="Vans (cumulative)")

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Cumulative detections")
        ax.legend()

        st.pyplot(fig)

        st.write(f"Total car detections: {total_cars}")
        st.write(f"Total bus detections: {total_buses}")
        st.write(f"Total van detections: {total_vans}")

    else:
        st.error("Unsupported file type. Please upload an image or video.")


# --- LOCAL PSEUDO-LIVE STREAM (UNCOMMENT TO ENABLE) ---
# import time

# st.title("Local pseudo-live stream")
# placeholder = st.empty()

# # Simulate live feed by repeatedly loading the latest image
# while True:
#     frame = Image.open(r"Capstone_Project\Module_4\live_feed\latest.jpg")
#     result_image = model.image_inference(frame)
#     placeholder.image(result_image, caption="Processed Output", use_container_width=True)
#     time.sleep(1)
