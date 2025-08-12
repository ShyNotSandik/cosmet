from google.cloud import vision
import os
import re
import streamlit as st
from dotenv import load_dotenv
import openai
import pandas as pd
import base64
import json
from google.oauth2 import service_account


load_dotenv()
# Decoding json_keys.json
encoded_key = st.secrets["gcp"]["json_keys"]
service_account_info = json.loads(base64.b64decode(encoded_key))





# Setting an OpenAI API
client = openai.OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
)
# Setting a background image
page_bg_img = '''
<style>
[data-testid="stAppViewContainer"] {
background-image: url("https://4kwallpapers.com/images/wallpapers/your-name-shooting-5120x2880-14938.jpg");
background-size: cover;
}
</style>
'''

div_bg_color = """
<style>
[data-testid='stHorizontalBlock'] {
     background-color: #101010;
     padding: 20px;
     height:140px;
     opacity: 0.9;
     border-radius:15px;
     background-size: cover;
}
</style>


"""

hide_header = """
<style>
[data-testid='stHeader'] {
     display:none;

}

</style>

"""
st.markdown(hide_header, unsafe_allow_html=True)
st.markdown(div_bg_color, unsafe_allow_html= True)
st.markdown(page_bg_img, unsafe_allow_html=True)



# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "json_keys.json"

def main():
    
   
    st.title("We will estimate all  :green[ingredients] in :rainbow[cosmetics] and give it to you in a simple table 📊")
    st.caption("We will give back full detailed data about it")
    st.divider()
    # Get a file from user
    upload = st.file_uploader("Choose a file", type=["jpeg", "jpg", "png"])
    st.divider()

    if upload is not None:
      text = detect_text(upload) # return text from ORC
      match = re.search(r"(?:INGREDIENTS(?:.*?)?): ?(.+)\. ?(?:\n)?", text, re.IGNORECASE | re.S)
      if text and match:
          word_array = match.group(1).split(",")
          st.badge("Text is detected, wait few seconds", color="green", width="stretch", icon=":material/check:")
          with st.spinner("Wait until data return", show_time=True):
               res = get_output(word_array)
               try:
                    ingridients = eval(res.to_dict()["output"][0]["content"][0]["text"].strip().replace("```", ""))
                    print(f"Recieved and convert dict from ChatGPT: {ingridients}")
                    for key, value in ingridients.items():
                        col1, col2 = st.columns(spec = [0.8, 0.2])
                        with st.container(border = None):
                         with col1:
                                   st.write(f"**{key}**")
                                   st.text(value["Benefits"])
                         with col2:
                              st.badge(value["Rating"], color=match_color(value["Rating"]))

                    
               except SyntaxError:
                   st.write("Sorry, your text has been recognised but not decoded, try again")
               
               
      else:
           st.badge("Text wasn't detected, try again", color="red", width=1000)

               
    
  
# Detects text using Google Cloud Vision API

def detect_text(image_file):
    # Setting up Google Cloud Vison credentials 
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    client = vision.ImageAnnotatorClient(credentials=credentials)
    content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    print("Text was detecting. Parsing it to ChatGPT...")

    return texts[0].description

# Prompt to chatgpt and return answear
def get_output(list):
     try:
        response = client.responses.create(
        model="gpt-4o",
        instructions="You are a medical expretes that can explain which ingredient in cosmetic is used for",
        input=f"""Look for all ingredient in {list} then return dictionary, no markdown formatting with the following field, if there is some text which is not ingredients, ignore it:
        - Name of the ingredient which will contain two keys:
          - Rating ( based on quality and benefits of product or unhealthiness , it can be 'Great', 'Good', 'Moderate', 'Under average' , 'Bad' )
          - Benefits (why is it good or bad for health)
          """,
        )

     except openai.APIError as e:
        st.write(f"OpenAI API returned an API Error: {e}")
     except openai.APIConnectionError as e:
        st.write(f"Failed to connect to OpenAI API: {e}")
        
     except openai.RateLimitError as e:
        st.write(f"OpenAI API request exceeded rate limit: {e}")
        
     print("Answear is recieved from ChatGPT")
     return response

def match_color(rating):
     if rating == "Great" or rating == "Good":
          return "green"
     if rating == "Moderate" :
          return "orange"
     if rating == "Bad" or rating == "Under average":
          return "red"
     

main()