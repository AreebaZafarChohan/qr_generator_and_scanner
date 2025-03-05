import streamlit as st
import qrcode
import qrcode.image.svg
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
import tempfile

# Function to generate QR code
def generate_qr(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    return img

# Function to generate SVG QR Code
def generate_svg_qr(data):
    factory = qrcode.image.svg.SvgImage
    qr = qrcode.make(data, image_factory=factory)
    return qr

# Function to scan QR code from an image file
def scan_qr_code(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(uploaded_file.getvalue())
        temp_path = temp.name
    
    # Read the image properly
    image = cv2.imdecode(np.fromfile(temp_path, np.uint8), cv2.IMREAD_COLOR)

    if image is None:
        return "Error: Unable to read image. Please upload a valid QR Code image."

    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(image)

    return data if data else "No valid QR Code found."


# Streamlit UI
st.title("🔗 QR Code Generator & Scanner")
st.write("Enter a link below to generate a QR Code!")

# User Input
link = st.text_input("Enter the URL:")

if link:
    qr_img = generate_qr(link)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)
    st.image(buffer, caption="Generated QR Code", use_column_width=True)
    
    # Download Options
    st.subheader("📥 Save QR Code")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.download_button("Download PNG", buffer.getvalue(), file_name="qr_code.png", mime="image/png")
    with col2:
        svg_qr = generate_svg_qr(link)
        buffer_svg = BytesIO()
        svg_qr.save(buffer_svg)
        buffer_svg.seek(0)
        st.download_button("Download SVG", buffer_svg.getvalue(), file_name="qr_code.svg", mime="image/svg+xml")
    with col3:
        buffer_jpeg = BytesIO()
        qr_img.save(buffer_jpeg, format="JPEG")
        buffer_jpeg.seek(0)
        st.download_button("Download JPEG", buffer_jpeg.getvalue(), file_name="qr_code.jpeg", mime="image/jpeg")
    with col4:
        buffer_pdf = BytesIO()
        qr_img.save(buffer_pdf, format="PNG")  # Save PNG format for PDF
        buffer_pdf.seek(0)
        st.download_button("Download PDF", buffer_pdf.getvalue(), file_name="qr_code.pdf", mime="application/pdf")

# QR Code Scanner
st.subheader("📷 QR Code Scanner")
uploaded_file = st.file_uploader("Upload a QR Code image (PNG, JPEG, SVG, PDF):", type=["png", "jpg", "jpeg", "svg", "pdf"])

if uploaded_file is not None:
    result = scan_qr_code(uploaded_file)
    if result:
        st.success(f"🔍 Scanned QR Code Data: {result}")
    else:
        st.error("No valid QR Code found in the uploaded image.")

# Sidebar Feedback Section
st.sidebar.title("💬 Feedback & Rating")
if "feedback_list" not in st.session_state:
    st.session_state.feedback_list = []

username = st.sidebar.text_input("Your Name:")
feedback = st.sidebar.text_area("Leave your feedback:")
rating = st.sidebar.slider("Rate this app:", 1, 5, 5)
if st.sidebar.button("Submit Feedback"):
    if username and feedback:
        st.session_state.feedback_list.append({"name": username, "feedback": feedback, "rating": rating})
        st.sidebar.success("Thank you for your feedback!")
    else:
        st.sidebar.error("Please enter your name and feedback before submitting.")

# Display Feedbacks in Sidebar
st.sidebar.subheader("📜 Feedback History")
if st.session_state.feedback_list:
    for fb in reversed(st.session_state.feedback_list):
        st.sidebar.write(f"**{fb['name']}** ⭐ {fb['rating']}/5")
        st.sidebar.write(f"_\"{fb['feedback']}\"_")
        st.sidebar.write("---")
    
    # Clear Feedback History Button
    if st.sidebar.button("Clear Feedback History"):
        st.session_state.feedback_list = []
        st.sidebar.success("Feedback history cleared!")
else:
    st.sidebar.write("No feedback yet. Be the first to share your thoughts!")

# Footer
st.markdown("---")
st.markdown("""
    <p style='text-align: center; color: gray;'>© 2025 QR Code Generator | Developed with ❤️ by Areeba Zafar</p>
""", unsafe_allow_html=True)
