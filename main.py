import streamlit as st
import json
import os
from parse import parse_with_ollama, summarize_with_mistral, extract_features
from scrape import scrape_website, extract_body_content, clean_body_content, split_dom_content

st.set_page_config(page_title="AI Web Scraper", layout="wide")

USER_FILE = "users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as file:
            json.dump({}, file)
    with open(USER_FILE, "r") as file:
        return json.load(file)

def save_users(users):
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)

def authenticate(username, password):
    users = load_users()
    return users.get(username) == password

def register_user(username, password):
    users = load_users()
    if username in users:
        return False  # Username already exists
    users[username] = password
    save_users(users)
    return True  # Registration successful

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None

st.sidebar.title("🔐 Authentication")

if not st.session_state.authenticated:
    auth_option = st.sidebar.radio("Select Option", ["Login", "Register"])

    if auth_option == "Login":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        login_button = st.sidebar.button("Login")

        if login_button:
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success(f"✅ Welcome, {username}!")
                st.rerun()
            else:
                st.sidebar.error("❌ Invalid username or password")

    elif auth_option == "Register":
        new_username = st.sidebar.text_input("New Username")
        new_password = st.sidebar.text_input("New Password", type="password")
        register_button = st.sidebar.button("Register")

        if register_button:
            if register_user(new_username, new_password):
                st.sidebar.success("✅ Registration successful! Please log in.")
            else:
                st.sidebar.error("❌ Username already exists. Try another.")

else:
    st.sidebar.write(f"👤 Logged in as: **{st.session_state.username}**")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

    st.title("🔍 AI-Powered Web Scraper")

    url = st.text_input("🌐 Enter Website URL", placeholder="https://example.com")

    if st.button("🚀 Scrape Website"):
        if url:
            st.write("🔄 Scraping the website... Please wait.")

            dom_content = scrape_website(url)

            if dom_content:
                body_content = extract_body_content(dom_content)
                cleaned_content = clean_body_content(body_content)

                st.session_state.dom_content = cleaned_content

                with st.expander("📜 View Extracted Website Content"):
                    st.text_area("DOM Content", cleaned_content, height=300)
            else:
                st.error("❌ Failed to scrape the website. Please check the URL or try again.")

    if "dom_content" in st.session_state:
        parse_description = st.text_area(
            "✏️ Describe what you want to extract",
            placeholder="Describe the information you want to extract from the page",
        )

        if st.button("🔎 Parse Content"):
            if parse_description:
                st.write("🧠 AI is extracting relevant information...")

                dom_chunks = split_dom_content(st.session_state.dom_content)

                parsed_result = parse_with_ollama(dom_chunks, parse_description).strip()

                if parsed_result:
                    st.success("✅ Extraction Successful!")
                    st.write(parsed_result)
                    st.session_state.parsed_result = parsed_result  # Store parsed result for feature extraction
                else:
                    st.warning("⚠️ No matching content found.")

        # ✅ New Separate "Extract Features" Button
        if "parsed_result" in st.session_state and st.button("🔍 Extract Features"):
            extracted_features = extract_features(st.session_state.parsed_result)
            st.subheader("🔍 Extracted Features")
            if extracted_features:
                st.write(extracted_features)
            else:
                st.warning("⚠️ No features extracted.")

        # ✅ AI Summary Button
        if st.button("📄 Summarize Content"):
            summary = summarize_with_mistral(st.session_state.dom_content)
            st.subheader("📌 Summary")
            if summary:
                st.write(summary)
            else:
                st.warning("⚠️ No summary generated.")
