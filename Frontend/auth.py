import base64
import json
from urllib.parse import urlencode

import requests
import streamlit as st


ADMIN_EMAILS = ["kadiogluu@mef.edu.tr"]
TEACHER_EMAILS = ["bekmezcii@mef.edu.tr","dincelh@mef.edu.tr"]


def _decode_email_from_id_token(id_token: str) -> str | None:
    try:
        parts = id_token.split(".")
        if len(parts) != 3:
            return None
        payload_b64 = parts[1]
        padding = "=" * (-len(payload_b64) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
        payload = json.loads(payload_bytes.decode("utf-8"))
        return payload.get("email")
    except Exception:
        return None


def _role_for_email(email: str) -> str | None:
    if not email or not email.endswith("@mef.edu.tr"):
        return None
    if email in ADMIN_EMAILS:
        return "admin"
    if email in TEACHER_EMAILS:
        return "teacher"
    return "student"


def ensure_authenticated():
    if "user_email" in st.session_state and "user_role" in st.session_state:
        return st.session_state["user_email"], st.session_state["user_role"]

    cfg = st.secrets["google_oauth"]
    client_id = cfg["client_id"]
    client_secret = cfg["client_secret"]
    redirect_uri = cfg["redirect_uri"]
    auth_uri = cfg.get("auth_uri", "https://accounts.google.com/o/oauth2/v2/auth")
    token_uri = cfg.get("token_uri", "https://oauth2.googleapis.com/token")

    params = st.query_params

    if "code" in params and not st.session_state.get("token_exchanged", False):
        code = params["code"]

        data = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        resp = requests.post(token_uri, data=data)

        if not resp.ok:
            st.error("Google ile giriş sırasında hata oluştu.")
            st.stop()

        tokens = resp.json()
        email = _decode_email_from_id_token(tokens.get("id_token", ""))

        role = _role_for_email(email)
        if role is None:
            st.error("Sadece @mef.edu.tr öğretmen/öğrenci hesapları giriş yapabilir.")
            st.stop()

        st.session_state["user_email"] = email
        st.session_state["user_role"] = role
        st.session_state["token_exchanged"] = True
        st.query_params.clear()
        st.rerun()

    st.title("Rapor Değerlendirme Girişi")
    st.write("Lütfen MEF mail adresinizle Google üzerinden giriş yapın.")

    auth_params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "include_granted_scopes": "true",
        "prompt": "select_account",
    }
    auth_url = f"{auth_uri}?{urlencode(auth_params)}"

    st.markdown(
        f"""
        <a href="{auth_url}"
           style="
             display:inline-block;
             padding:0.6rem 1.4rem;
             background-color:#2563eb;
             color:white;
             border-radius:0.5rem;
             text-decoration:none;
             font-weight:600;
           ">
           Google ile Giriş Yap
        </a>
        """,
        unsafe_allow_html=True,
    )

    st.stop()
