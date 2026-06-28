import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load Dataset
df = pd.read_csv("laboratory__data.csv")

# Select Required Columns
df = df[['Glucose', 'Hemoglobin', 'Cholestrol', 'Disease ']]

# Remove Missing Values
df = df.dropna()

# Features and Target
X = df[['Glucose', 'Hemoglobin', 'Cholestrol']]
y = df['Disease ']

# Split Dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Train Model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Test Accuracy
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("Model Accuracy:", accuracy)

# Save Model
joblib.dump(model, "health_model.pkl")

print("Model Saved Successfully!")