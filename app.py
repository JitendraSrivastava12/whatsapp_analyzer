import streamlit as st
import matplotlib.pyplot as plt
import preprocess
import helper
import pandas as pd

st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")
st.sidebar.title("WhatsApp Chat Analyzer")

# Allow both .zip and .txt
uploaded_file = st.sidebar.file_uploader("Upload your WhatsApp chat (.zip or .txt)", type=["zip", "txt"])

if uploaded_file is not None:
    # Handle ZIP
    if uploaded_file.type == "application/zip":
        with open("temp_chat.zip", "wb") as f:
            f.write(uploaded_file.read())
        df = preprocess.get_data(zip_path="temp_chat.zip")

    # Handle TXT
    elif uploaded_file.type == "text/plain":
        df = preprocess.get_data(txt_file=uploaded_file)

    user_list = df['Sender'].unique().tolist()
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show Analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):
        num_messages, total_words, media_count, link_count = helper.fetch_stats(selected_user, df)

        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Messages", num_messages)
        with col2:
            st.metric("Total Words", total_words)
        with col3:
            st.metric("Media Shared", media_count)
        with col4:
            st.metric("Links Shared", link_count)

        # Monthly Timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['Message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Daily Timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['Date'], daily_timeline['Message'], color='pink')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Activity Maps
        col1, col2 = st.columns(2)
        with col1:
            st.title("Weekday Timeline")
            day_timeline = helper.day_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(day_timeline['Weekday'], day_timeline['Message'], color='blue')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.title("Month Timeline")
            month_timeline = helper.month_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(month_timeline['month'], month_timeline['Message'], color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # Most Busy Users
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            col1, col2 = st.columns(2)
            with col1:
                x, dfs = helper.most_busy_users(df)
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.bar(x.index, x.values, color='red')
                ax.set_title("Participant Activity")
                ax.set_xlabel("Users")
                ax.set_ylabel("Messages")
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(dfs)

        # Word Cloud
        st.title("Word Cloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.imshow(df_wc, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)

        # Most Common Words
        st.title("Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(most_common_df['Word'], most_common_df['Count'], color='skyblue')
        ax.set_xlabel("Frequency")
        ax.set_title("Top 20 Most Common Words")
        fig.tight_layout()
        st.pyplot(fig)

        #Average seniment of group
        st.title('Sentiment of Users')
        col1, col2 = st.columns(2)


        with col1:
            avg, sentiment_text = helper.avg_sentiment(selected_user, df)
            st.metric("Sentiment", sentiment_text)
            st.metric("Confidence Score", f"{avg:.2f}")

        with col2:
            st.subheader("Each User's Overall Sentiment")
            dft=helper.sentiment_of_group(selected_user,df)
            st.dataframe(dft)

        st.title("Monthly Sentiment Analysis")

        monthly_timeline = helper.sentiment_with_time(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(monthly_timeline['month'], monthly_timeline['Sentiment'], color='purple')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)








