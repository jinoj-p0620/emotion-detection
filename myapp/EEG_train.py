import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier  # For feature selection
import joblib

# Load data
df = pd.read_csv(r'emotions.csv') #EEG Dataset fro emotion from EEG


def preprocess_with_feature_selection(df, num_features=100):
    df = df.copy()

    # 1. Encode Labels
    label_encoder = LabelEncoder()
    df['label'] = label_encoder.fit_transform(df['label'])

    y = df['label']
    X = df.drop('label', axis=1)

    # 2. Feature Selection using Random Forest
    print(f"Selecting top {num_features} essential features...")
    selector = RandomForestClassifier(n_estimators=50, random_state=42)
    selector.fit(X, y)

    # Get importance scores and sort them
    importances = selector.feature_importances_
    indices = np.argsort(importances)[::-1][:num_features]

    # Identify essential features
    essential_feature_names = X.columns[indices].tolist()
    X_essential = X[essential_feature_names]

    print(f"\nTop 10 Essential Features: {essential_feature_names[:10]}")

    # 3. Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(X_essential, y, train_size=0.8, random_state=42)

    # 4. Scaling
    scaler = StandardScaler()
    X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X_essential.columns)
    X_test = pd.DataFrame(scaler.transform(X_test), columns=X_essential.columns)

    return X_train, X_test, y_train, y_test, label_encoder, scaler, essential_feature_names


# Select top 50 features instead of all
X_train, X_test, y_train, y_test, label_encoder, scaler, selected_features = preprocess_with_feature_selection(df,
                                                                                                               num_features=50)

# Save the list of selected features (CRITICAL for prediction)
joblib.dump(selected_features, 'selected_features.gz')

# 3. Build the Model (Input shape is now 50)
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(X_train.shape[1],)),
    tf.keras.layers.Dense(128, activation='relu'),  # Smaller network for fewer features
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(3, activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# 4. Train
model.fit(X_train, y_train, validation_split=0.2, batch_size=32, epochs=50,
          callbacks=[tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True)])

# 5. Save
model.save('eeg_emotion_model.h5')
joblib.dump(scaler, 'scaler.gz')
joblib.dump(label_encoder, 'label_encoder.gz')


# Top 10 Essential Features: ['min_q_5_b', 'min_q_10_b', 'covmat_104_b', 'min_q_15_a', 'min_q_5_a', 'min_q_15_b', 'stddev_0_a', 'min_q_18_a', 'mean_d_15_b', 'covmat_8_b']