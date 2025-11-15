import streamlit as st
from PIL import Image
import tempfile

# # --- PAGE SETUP ---
# st.set_page_config(page_title="Multimodal Object Detection", layout="centered")
# st.title("🎥 Multimodal Object Detection Demo")

# # --- FILE UPLOADER ---
# uploaded_file = st.file_uploader(
#     "Upload an image or video file",
#     type=["jpg", "jpeg", "png", "mp4", "mov", "avi"],
# )

# # --- PLACEHOLDER for output ---
# output_placeholder = st.empty()

# # --- MAIN LOGIC ---
# if uploaded_file is not None:
#     # Identify file type by MIME
#     mime_type = uploaded_file.type

#     # Temporary save file (so OpenCV / YOLO can use it later)
#     with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#         temp_file.write(uploaded_file.read())
#         temp_path = temp_file.name

#     # IMAGE HANDLING
#     if mime_type.startswith("image"):
#         st.subheader("🖼️ Uploaded Image")

#         # --- INPUT (display uploaded) ---
#         image = Image.open(temp_path)
#         st.image(image, caption="Original Upload", use_container_width=True)

#         # --- PROCESSING PLACEHOLDER ---
#         # result_image = run_object_detection(image)
#         # st.image(result_image, caption="Processed Output", use_container_width=True)

#     # VIDEO HANDLING
#     elif mime_type.startswith("video"):
#         st.subheader("🎬 Uploaded Video")

#         # --- INPUT (display uploaded) ---
#         st.video(temp_path)

#         # --- PROCESSING PLACEHOLDER ---
#         # result_video_path = run_video_detection(temp_path)
#         # st.video(result_video_path)

#     else:
#         st.error("Unsupported file type. Please upload an image or video.")


# import time
# from PIL import Image
# import streamlit as st

# st.title("Local pseudo-live stream")

# placeholder = st.image([])

# while True:
#     frame = Image.open("live_feed/latest.jpg")
#     placeholder.image(frame, use_container_width=True)
#     time.sleep(1)
