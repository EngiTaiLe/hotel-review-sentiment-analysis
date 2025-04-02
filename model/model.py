import pickle
import string
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import pandas as pd
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

class Model:
    with open('/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/model/tokenizer.pkl', 'rb') as file:
        tokenizer = pickle.load(file)
    model = tf.keras.models.load_model('/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/model/dl_model.h5')
    # with open('/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/model/ml_model.pkl', 'rb') as file:
    #     log = pickle.load(file)
    def cleaning(self, text):
        # remove punctuations and uppercase
        clean_text = text.translate(str.maketrans('', '', string.punctuation)).lower()

        # remove stopwords
        clean_text = [word for word in clean_text.split() if word not in stopwords.words('english')]

        # lemmatize the word
        sentence = []
        for word in clean_text:
            lemmatizer = WordNetLemmatizer()
            sentence.append(lemmatizer.lemmatize(word, 'v'))

        return ' '.join(sentence)

    def prepare_data(self, data):
        X = data['review_content'].apply(self.cleaning)
        test_seq = self.tokenizer.texts_to_sequences(X)
        test_padded = pad_sequences(test_seq)
        return test_padded

    def dl_predict(self, data):
        test_padded = self.prepare_data(data)
        pred = self.model.predict(test_padded)
        pred_labels = (pred > 0.5).astype(int)
        return pred_labels

    # def ml_predict(self,text):
    #     clean_text = self.cleaning(text)
    #     tfid_matrix = self.tfid.transform([clean_text])
    #     pred = self.log.predict(tfid_matrix)[0]
    #     return pred

