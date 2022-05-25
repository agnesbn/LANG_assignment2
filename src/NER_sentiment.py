"""
Sentiment and NER
"""
""" Import relevant packages """
 # data analysis
import os
import pandas as pd
from collections import Counter
from tqdm import tqdm
from collections import defaultdict
import numpy as np
 # NLP
import spacy
nlp = spacy.load("en_core_web_sm")
 # sentiment analysis VADER
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
 # visualisations
import matplotlib.pyplot as plt

""" Basic functions """
# Get VADER scores
def vader_scores(df):
    # shorter name
    analyzer = SentimentIntensityAnalyzer()
    # list of scores
    vader_scores = []
    # for every post
    for headline in df["title"]:
        # get polarity scores
        score = analyzer.polarity_scores(headline)
        # append scores to list
        vader_scores.append(score)
    # return list of VADER scores
    return vader_scores

# Get overall evaluation from compound score
def evaluate_scores(df):
    evaluation = []
    for x in df["compound"]:
        if x >= 0.05:
            evaluation.append('positive')
        elif x <= - 0.05:
            evaluation.append('negative')
        else:
            evaluation.append('neutral')
    return evaluation

# Run a dataframe though an NLP pipeline and get GPEs
def nlp_pipeline(df, batch_size):
    # list of geopolitical entities and the text_id of the text they occur in
    ents = []
    # list of all geopolitical entities mentioned
    gpes = []
    # iterate over every text, run posts through NLP pipeline and get the text_id
    for post, num in zip(tqdm(nlp.pipe(df["title"], batch_size=batch_size)), df["text_id"]):
        # for every entity in the posts
        for entity in post.ents:
            # if that entity is a geopolitical entity
            if entity.label_ == "GPE":
                # append the text_id and the geopolitical entity to one list
                ents.append((num, entity.text))
                # and simply append the geopolitical entity to another text
                gpes.append(entity.text)
    # return both lists
    return ents, gpes

# Convert a list to a dictionary
def list_to_dict(entity_list):
    # initialise dictionary 
    d = defaultdict(list)
    # iterate over tuples in list
    for tup in entity_list:
        # tuple[0] is the key and tuple[1] is the value
        d[tup[0]].append(tup[1])
    # return the dictionary
    return d

# Function to save a bar plot
def save_bar_plot(top_list, colour, title, plot_name):
    plt.bar(range(len(top_list)), [val[1] for val in top_list], align='center', color = colour)
    plt.xticks(range(len(top_list)), [val[0] for val in top_list])
    plt.xticks(rotation=70)
    plt.title(title)
    plt.savefig(os.path.join("out", "plots", f"{plot_name}.png"), dpi=400)  
    plt.close()


""" Fake/Real news analysis """
def real_fake_GPES():
    # define filepath
    filepath = os.path.join("in", "fake_or_real_news.csv")
    # load the data
    data = pd.read_csv(filepath)
    # define batch sizes for the real and fake data
    v_counts = data["label"].value_counts()
    r_batch_size = int(v_counts[0])
    f_batch_size = int(v_counts[1])
    # delete unnamed column
    del data["Unnamed: 0"]
    # create a text ID column
    data["text_id"] = data.index + 1
    # split the data
    real_news_df = data[data["label"] == "REAL"]
    fake_news_df = data[data["label"] == "FAKE"]
    # reset the index for each new dataframe
    real_news_df = real_news_df.reset_index()
    fake_news_df = fake_news_df.reset_index()
    # calculate VADER scores for both dataframes
    real_vader_scores = vader_scores(real_news_df)
    fake_vader_scores = vader_scores(fake_news_df)
    # create dataframes from the sentiment scores
    r_vader_df = pd.DataFrame(real_vader_scores)
    f_vader_df = pd.DataFrame(fake_vader_scores)
    # get evaluations
    r_vader_df["evaluation"] = evaluate_scores(r_vader_df)
    f_vader_df["evaluation"] = evaluate_scores(f_vader_df)
    # print distribution of evaluations
    print("Real news - Distribution of VADER scores")
    print(r_vader_df['evaluation'].value_counts(normalize=True) * 100)
    print("Fake news - Distribution of VADER scores")
    print(f_vader_df['evaluation'].value_counts(normalize=True) * 100)
    # run the dataframes through an nlp pipeline
    print("[INFO] Running real news though NLP pipeline ...")
    r_ents, r_gpes = nlp_pipeline(real_news_df, r_batch_size)
    print("[INFO] Running fake news though NLP pipeline ...")
    f_ents, f_gpes = nlp_pipeline(fake_news_df, f_batch_size)
    # convert entity list to dictionary
    r_dict = list_to_dict(r_ents)
    f_dict = list_to_dict(f_ents)
    # make dataframes from the dictionaries
    rGPE_df = pd.DataFrame(list(r_dict.items()), columns = ["text_id", "GPEs"])
    fGPE_df = pd.DataFrame(list(f_dict.items()), columns = ["text_id", "GPEs"])
    # merge the GPE dataframes with the original (separated) dataframes
    r_df = pd.merge_ordered(real_news_df, rGPE_df, left_by = "text_id", fill_method = "ffill")
    f_df = pd.merge_ordered(fake_news_df, fGPE_df, left_by = "text_id", fill_method = "ffill")
    # create output dataframes with the VADER scores
    r_output = r_vader_df
    f_output = f_vader_df
    # add the text ID and the GPEs to the output dataframes
    r_output.insert(0, "text_id", real_news_df["text_id"])
    f_output.insert(0, 'text_id', fake_news_df["text_id"])
    r_output.insert(1, "GPEs", r_df["GPEs"])
    f_output.insert(1, "GPEs", f_df["GPEs"])
    # save as CSV
    r_output.to_csv(os.path.join("out", "tables", "real_news.csv"), index=False)
    f_output.to_csv(os.path.join("out", "tables", "fake_news.csv"), index=False)
    # count the unique entities in the list of all GPEs
    joined_gpes = r_gpes + f_gpes
    gpe_counts = Counter(joined_gpes)
    rGpe_counts = Counter(r_gpes)
    fGpe_counts = Counter(f_gpes)
    # create list of the 20 most frequent GPEs (in general and for each kind of news)
    top20 = gpe_counts.most_common(20)
    r_top20 = rGpe_counts.most_common(20)
    f_top20 = fGpe_counts.most_common(20)
    # save bar plots for the top 20 in general, and the top 20 for real and fake news respectively
    save_bar_plot(top20, "lightblue", "Geopolitical entities – All news", "GPE_all_news")
    save_bar_plot(r_top20, "lightgreen", "Geopolitical entities – Real news", "GPE_real_news")
    save_bar_plot(f_top20, "pink", "Geopolitical entities – Fake news", "GPE_fake_news")

""" Main function """
def main():
    # simply run the news analysis function
    real_fake_GPES()

    
if __name__=="__main__":
    main()