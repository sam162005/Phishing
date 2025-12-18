import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score
import pickle
import re

# ------------------- LOAD DATA -------------------
print("📥 Loading dataset...")
df = pd.read_csv("Preprocessed Fake Reviews Detection Dataset.csv")

print("\n🧾 Dataset columns found:")
print(df.columns)
print("\n📊 First few rows:")
print(df.head())

# Use the correct column names
df = df[['text_', 'label']].dropna()

# ------------------- CREATE LABELS -------------------
# Map original labels: CG (Computer Generated) -> 1 (fake), OR (Original) -> 0 (real)
df['label'] = df['label'].map({'CG': 1, 'OR': 0})

# ------------------- SPLIT DATA -------------------
X_train, X_test, y_train, y_test = train_test_split(
    df['text_'], df['label'], test_size=0.2, random_state=42, stratify=df['label']
)

# ------------------- TF-IDF + MODEL -------------------
vectorizer = TfidfVectorizer(stop_words='english', max_features=10000, ngram_range=(1,3))
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_tfidf, y_train)

# ------------------- EVALUATION -------------------
y_pred = model.predict(X_test_tfidf)
print("\n✅ Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# ------------------- SAVE MODEL -------------------
with open("fake_review_model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)
print("\n💾 Model and vectorizer saved successfully!")
