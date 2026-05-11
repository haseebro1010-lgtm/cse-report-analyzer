import streamlit as st
import pdfplumber
import google.generativeai as genai

# App එකේ මාතෘකාව සහ සැකසුම්
st.set_page_config(page_title="Stock Market Report Analyzer", layout="wide")
st.title("📊 Quarterly Report Analyzer (CSE)")
st.write("සමාගමේ Quarterly Reports 3 මෙහි Upload කරන්න. AI මගින් එය විශ්ලේෂණය කර සරල සිංහලෙන් වාර්තාවක් ලබා දෙනු ඇත.")
st.markdown("---")
st.caption("Developed by **[H.S Hewavidana]** 💻")
st.markdown("---")

# Sidebar එකේ API Key එක ලබා දීම
st.sidebar.header("සැකසුම් (Settings)")
api_key = st.sidebar.text_input("ඔබගේ Gemini API Key එක මෙහි ඇතුලත් කරන්න:", type="password")

if api_key:
    genai.configure(api_key=api_key)

# PDF Files Upload කිරීම
uploaded_files = st.file_uploader("Quarterly Reports 3ක් තෝරන්න (PDF)", accept_multiple_files=True, type=["pdf"])

# PDF එකෙන් අකුරු කියවීමේ Function එක
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text

if st.button("විශ්ලේෂණය ආරම්භ කරන්න (Analyze)"):
    if not api_key:
        st.error("කරුණාකර වම් පසින් ඔබගේ Gemini API Key එක ඇතුලත් කරන්න!")
    elif len(uploaded_files) != 3:
        st.warning("කරුණාකර නිවැරදිව PDF වාර්තා 3ක් Upload කරන්න.")
    else:
        with st.spinner("වාර්තා කියවමින් පවතී... කරුණාකර රැඳී සිටින්න..."):
            all_text = ""
            for i, file in enumerate(uploaded_files):
                all_text += f"\n--- Report {i+1} ---\n"
                all_text += extract_text_from_pdf(file)
            
            # AI එකට ලබා දෙන උපදෙස් (Prompt)
            prompt = f"""
            පහත දැක්වෙන්නේ ශ්‍රී ලංකාවේ සමාගමක කාර්තුවික මූල්‍ය වාර්තා (Quarterly Reports) 3කින් උපුටා ගත් දත්තයන්ය.
            මෙම දත්ත විශ්ලේෂණය කර පහත කරුණු ඇතුළත් කරමින් සරල සිංහල භාෂාවෙන් පිළිතුරක් සපයන්න:

            1. EPS, NAV, PE Ratio, PBV, Beta, DE Ratio සහ Dividend Yield යන දර්ශකයන් හරියටම මෙම පිළිවෙලට ගෙනහැර දක්වමින්, එම අගයන් මාස 3 ඇතුළත වෙනස් වී ඇති ආකාරය සසඳන්න.
            2. මෙහි PBV (Price-to-Book Value) යනු කුමක්දැයි අනිවාර්යයෙන්ම සරලව විස්තර කරන්න.
            3. මෙම වෙනස්වීම් සමාගමට බලපා ඇත්තේ හොඳ විදිහටද, නරක විදිහටද යන්න පැහැදිලි කරන්න.
            4. සමාගමේ වර්තමාන තත්ත්වය කුමක්ද සහ ඉදිරියට කුමක් විය හැකිද?
            5. ආයෝජකයෙකු ලෙස මෙම සමාගමේ ආයෝජනය කිරීම සුදුසුද යන වග සරලව පැහැදිලි කරන්න.

            වාර්තා දත්ත:
            {all_text[:30000]} # Limit text length to avoid token limits
            """

            try:
                # ඔබගේ API Key එකට සහය දක්වන Models ස්වයංක්‍රීයව සොයාගැනීම
                valid_models = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        valid_models.append(m.name)
                
                if not valid_models:
                    st.error("ඔබගේ API Key එක සඳහා කිසිදු AI Model එකක් ක්‍රියාත්මක නොවේ. කරුණාකර Google AI Studio වෙතින් අලුත් API Key එකක් සාදා ගන්න.")
                else:
                    # වැඩ කරන පළමු Model එක ස්වයංක්‍රීයව තෝරාගැනීම
                    # 'models/gemini-1.5-flash' වැනි නමකින් 'models/' කොටස ඉවත් කිරීම
                    best_model_name = valid_models[0].replace("models/", "")
                    
                    st.info(f"💡 ස්වයංක්‍රීයව තෝරාගත් AI Model එක: {best_model_name}")
                    
                    model = genai.GenerativeModel(best_model_name)
                    response = model.generate_content(prompt)
                    
                    st.success("විශ්ලේෂණය සාර්ථකයි!")
                    st.markdown("### 📈 මූල්‍ය විශ්ලේෂණ වාර්තාව")
                    st.write(response.text)
                
            except Exception as e:
                st.error(f"දෝෂයක් මතු විය: {e}")
