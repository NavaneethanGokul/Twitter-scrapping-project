import snscrape.modules.twitter as scrapetwit
import pandas as pd
from pymongo import MongoClient
import streamlit as st


#Default settings of the webpage
st.set_page_config(
    page_title="Twitter scraping App",
    layout="centered",
    initial_sidebar_state="expanded",
)

#Title 
st.title("Welcome to Twitter scrapper app!")

st.image("https://coolwallpapers.me/picsup/6033073-birds-family-sing-twitter.jpg")

# Connect to local mongo client
mongo_client = MongoClient()
# Connect to db
db = mongo_client["d254"]

# Labels for different input elements
label1 = "Search criteria"
label2 = "No. of tweets to scrape"
label3 = "Since"
label4 = "Until"
label5 = "Search"
label6 = "Upload data"
label7 = "Download csv file"
label8 = "Download json file"
flag = True

# Function to scrape tweets with user inputs
def scrape_tweets(query, no_of_tweets, since_date, until_date):
    tweet_list = []
    for i, url in enumerate(
        scrapetwit.TwitterSearchScraper(
            "{} since:{} until:{}".format(query, since_date, until_date)
        ).get_items()
    ):
        if i > no_of_tweets:
            break
        tweet_list.append(
            [
                url.date,
                url.id,
                url.rawContent,
                url.user.username,
                url.replyCount,
                url.retweetCount,
                url.lang,
                url.source,
                url.likeCount,
                url.hashtags,
            ]
        )
       
#Dataframe creation from the scraped list        
    df_tweet_list = pd.DataFrame(
        tweet_list,
        columns=[
            "Date",
            "ID",
            "Content",
            "Username",
            "Reply Count",
            "Retweet Count",
            "Language",
            "Source",
            "Like Count",
            "Hashtags",
        ],
    )
    # date, id, url, tweet content, user,reply count, retweet count,language, source, like count

    return df_tweet_list


# Function to upload data to database
def upload_data(df_tweet_list):
    # Convert dataframe to dictionary
    df_tweet_list.reset_index()
    dict_tweet_list = df_tweet_list.to_dict("records")
    # Store data in the db
    db.tweet2.insert_many(dict_tweet_list)
    st.success(">Data successfully uploaded to the Database! :blue_heart:")
    return None


#Sidebar for entering criteria for searching tweets
with st.sidebar:
    # Getting different user input criteria(Keyword, no. of tweets to scrape, data filter)
    query = st.text_input(
        label1,
        type="default",
        placeholder="Enter keywords or hashtags to search",
        disabled=False,
        label_visibility="visible",
    )

    no_of_tweets = st.number_input(
        label2,
        min_value=1,
        max_value=50,
        step=5,
        disabled=False,
        label_visibility="visible",
    )

    since_date = st.date_input(label3, disabled=False, label_visibility="visible")

    until_date = st.date_input(label4, disabled=False, label_visibility="visible")

    # Button to initiate scraping
    click_state = st.button(label5, help="Click to search results", type="primary")

if click_state:
    df_tweet_list = scrape_tweets(query, no_of_tweets, since_date, until_date)
    st.write(df_tweet_list)
    st.balloons()
    flag = False
else:
    pass

click_upload = st.button(
    label6, help="Click to upload the results", type="secondary", disabled=flag
)
if click_upload:
    upload_data(scrape_tweets(query, no_of_tweets, since_date, until_date))
else:
    pass


def convert_df_csv(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


def convert_df_json(df):
    return df.to_json(orient="records")


#Expander layout for download options
with st.expander("Download options", expanded=False):

    if query != "":
        csv_data = convert_df_csv(
            scrape_tweets(query, no_of_tweets, since_date, until_date)
        )

        st.download_button(
            label=label7,
            data=csv_data,
            file_name="Twitter.csv",
            mime="text/csv",
            disabled=flag,
        )

        json_data = convert_df_json(
            scrape_tweets(query, no_of_tweets, since_date, until_date)
        )

        st.download_button(
            label=label8,
            data=json_data,
            file_name="Twitter.json",
            mime="application/json",
            disabled=flag,
        )
    else:
        pass