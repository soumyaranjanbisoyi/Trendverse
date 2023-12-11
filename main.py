import streamlit as st
import openai
from openai import OpenAI
from streamlit import secrets
# from io import BytesIO
import pandas as pd
# from pytrends.request import TrendReq
import time
from datetime import datetime, timedelta
# from streamlit_extras.switch_page_button import switch_page
# import requests
from newsapi import NewsApiClient

client = OpenAI(api_key = "sk-")



# Load your API key from an environment variable or secret management service
# openai.api_key = st.secrets["openai"]["api_key"]

# Replace 'YOUR_API_KEY' with your actual NewsAPI key
newsapi = NewsApiClient(api_key='17005fa31a744afe8107afc27a4f9e5a')



def set_page_title(title):
    st.sidebar.markdown(unsafe_allow_html=True, body=f"""
        <iframe height=0 srcdoc="<script>
            const title = window.parent.document.querySelector('title') \
                
            const oldObserver = window.parent.titleObserver
            if (oldObserver) {{
                oldObserver.disconnect()
            }} \

            const newObserver = new MutationObserver(function(mutations) {{
                const target = mutations[0].target
                if (target.text !== '{title}') {{
                    target.text = '{title}'
                }}
            }}) \

            newObserver.observe(title, {{ childList: true }})
            window.parent.titleObserver = newObserver \

            title.text = '{title}'
        </script>" />
    """)

# client = OpenAI()

def generate_image(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        quality="standard",
        n=1,
        size="1024x1024"
    )
    image_url = response.data[0].url
    return image_url

def generate_content(topic, language, country, industry, creativity, audience, tone, words, platform):
    prompt = f"Imagine you are a world-renowned content writer crafting engaging and informative content for {platform}. Your task is to create a well-rounded and unbiased article centered around the headline: '{topic}'."


    if industry:
        prompt += f" Tailor your writing to the {industry} industry, seamlessly incorporating it."

    if language:
        prompt += f" Express your thoughts in {language}, striking a balance between creativity and authenticity. Aim for a {creativity}% creativity level."

        if creativity > "55":
            prompt += " This will result in a more imaginative and fictional content based on the specified percentage."
        else:
            prompt += " Your content will be grounded in reality and facts. If something is unknown, it won't be mentioned."

    if country:
        prompt += f" Imagine you're speaking directly to readers from {country}, taking their interests into account."

    if audience:
        prompt += f" Your content should be targeted to {audience} readers."

    if tone:
        prompt += f" Write with a {tone} and captivating tone."

    prompt += f" Ensure that the content does not exceed {words} words, providing thought-provoking and delightful insights."

    # Convert words to an integer
    words_int = int(words)

    if words_int < 100:
        prompt += " Keep the content concise and impactful."
    elif 100 <= words_int <= 500:
        prompt += " Include summaries and creative bullet points that engage the reader."
    else:
        prompt += " Feel free to write in-depth and explore the topic thoroughly."

    prompt += f" Remember, the goal is to create valuable content that resonates with the readers on {platform}."

    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    content = response.choices[0].message.content
    return content

def generate_hashtags(topic):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant that generates hashtags."},
                  {"role": "user", "content": f"Generate relevant hashtags for the topic: {topic}"}],
        max_tokens=30
    )
    hashtags = response.choices[0].message.content.strip()
    return hashtags

def main():

    st.set_page_config(page_title="TrendVerse",page_icon="logo2.png",layout="wide")  # Set the page layout to wide by default
    # st.image("image6.png")

    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # Create a wide layout with three columns
    col1, col2 = st.columns(2)

    # Fetch related keywords for the input keyword
    with col1:
        st.subheader("Latest topics")

        # Input text area to enter the query
        query_input = st.text_input("Enter the topic", "Saudi Arabia", help="Please enter a keyword for which you want the trending headlines")

        # Fetch recent AI-related news articles based on the entered query
        ai_news = newsapi.get_everything(q=query_input, sort_by='relevancy', language='en', from_param='2023-12-07', to='2023-12-08')
        

        # Extract relevant information from the news response
        news_articles = ai_news['articles']

        def format_newsletter(articles):
            ls = []
            newsletter_content = "<h1>Trending topics</h1>"
            for article in articles:
                title = article['title']
                newsletter_content += f"<p>{title}</p>"
                ls.append(title)
            return ls[:20]

        formatted_titles = format_newsletter(news_articles)

        st.table(pd.DataFrame(formatted_titles, columns=['News Title']))

    with col2:
        st.subheader("AI Content Generator")

        col4, col5, col6, col99 = st.columns(4)

        language = col4.selectbox("Target Language",["English", "Hindi", "Arabic", "Hinglish"])
        industry = col5.selectbox("Target Industry", ["", "Retail", "Hospitality", "Healthcare"])
        country = col6.selectbox("Target Country", ["","Saudi Arabia", "United States of America", "India"])
        platform = col99.selectbox("Target Platform", ["", "LinkedIn", "Twitter", "Instagram", "Facebook"])

        col7, col8, col9, col10 = st.columns(4)

        creativity = col7.text_input("creativity %", "50%")
        audience = col8.selectbox("Target audience", ["","Adults", "Teens", "Kids", "Old Age"])
        tone = col9.selectbox("Tone", ["","Formal", "Casual", "Professional", "Funny", "Serious"])
        words = col10.text_input("word count", "500")

        topic_name = st.text_input("Enter a topic", "", help="Enter the topic name")


        filename = ""

        col25, col26 = st.columns(2)

        # col26.subheader("Generated Image")

        image_url = None

        if image_url:
            col26.image(image_url, caption='Generated Image', use_column_width=True)
        else:
            col26.text("")

        if col25.button("Generate Content"):
            if topic_name.strip():
                generated_content = generate_content(topic_name, language, country, industry, creativity, audience, tone, words, platform)
                col25.text_area("Generated Content", generated_content, height=300)

                generated_hashtags = generate_hashtags(generated_content)
                col25.text_area("Generated Hashtags", generated_hashtags, height=100)
                
                # Generate the image after the content is generated
                image_url = generate_image(f"Create an image that portrays the essence of the topic '{topic_name}' in a compelling way. You have the creative freedom to either depict real personalities or craft hypothetical scenarios. Your image should capture attention, convey emotions, and spark imagination. Utilize colors, composition, and details to make the image visually captivating and thought-provoking. Imagine this image as a powerful visual representation that resonates with the audience.")
                col26.image(image_url, caption='Generated Image', use_column_width=True)

if __name__ == "__main__":
    main()
