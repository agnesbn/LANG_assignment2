# Assignment 2 - Sentiment and NER


For this assignment, you will write a small Python program to perform NER and sentiment analysis using the techniques you saw in class. You have the choice of one of two different tasks:

1. Using the corpus of English novels, write some code which does the following tasks

   - For every novel in the corpus
     - ~~Get the sentiment of the first sentence.~~
     - Get the sentiment of the final sentence.
     - Plot the results over time, with one visualisation showing sentiment of opening sentences over time and one of closing sentences over time.
     - Find the 20 most common geopolitical entities mentioned across the whole corpus - plot the result as a bar chart.

**OR**

2. Using the corpus of Fake vs Real news, write some code which does the following

   - Split the data into two datasets - one of Fake news and one of Real news
   - For every headline
     - Get the sentiment scores
     - Find all mentions of geopolitical entites
     - Save a CSV which shows the text ID, the sentiment scores, and column showing all GPEs in that text
   - Find the 20 most common geopolitical entities mentioned across each dataset - plot the results as a bar charts
