# app_streamlit.py
import streamlit as st
from infer import Detector
from features import extract_features

st.set_page_config(page_title="Phishing URL Detector", page_icon="🛡️")
st.title("🛡️ Phishing URL Detector (Demo)")
det = Detector()

url = st.text_input("Enter URL to analyze:", value="http://secure-paypal.com.login.verify-account.xyz/Confirm?user=test@example.com")
if st.button("Analyze"):
    if not url:
        st.warning("Please enter a URL.")
    else:
        res = det.predict_one(url)
        st.subheader(f"Prediction: {res['prediction']}")
        st.metric("Phishing probability", f"{res['proba']:.3f}")
        with st.expander("Show extracted features"):
            st.json(extract_features(url))
        st.caption("This model uses URL lexical features only — it does not fetch remote webpages.")
