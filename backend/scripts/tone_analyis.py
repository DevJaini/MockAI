# tone_analysis.py

import os
import numpy as np
import librosa
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, LSTM, Dense, Dropout, Input, Bidirectional
from tensorflow.keras.optimizers import Adam
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

# --------------------
# Configuration
# --------------------
DATA_DIR = "/Users/kp/capstone/backend/scripts/static"         # Directory containing audio files
LABELS_CSV = "data/labels.csv"  # CSV file with columns: filename, accuracy_score
SR = 16000                      # Sampling rate
N_MFCC = 13                     # Number of MFCC features to extract
MAX_LEN = 100                   # Maximum time steps (pad or truncate MFCC sequence)

# --------------------
# Feature Extraction
# --------------------
def extract_mfcc(audio_path, sr=SR, n_mfcc=N_MFCC, max_len=MAX_LEN):
    """
    Load an audio file, extract MFCC features and pad/truncate to a fixed length.
    
    Parameters:
      audio_path (str): Path to the audio file.
      sr (int): Sampling rate.
      n_mfcc (int): Number of MFCC coefficients.
      max_len (int): Maximum number of time steps.
      
    Returns:
      np.array: Array of shape (max_len, n_mfcc) representing the MFCC features.
    """
    audio, _ = librosa.load(audio_path, sr=sr)
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)
    mfcc = mfcc.T  # Transpose so that shape is (time, n_mfcc)
    
    # Pad or truncate to max_len time steps
    if mfcc.shape[0] < max_len:
        pad_width = max_len - mfcc.shape[0]
        mfcc = np.pad(mfcc, ((0, pad_width), (0, 0)), mode='constant')
    else:
        mfcc = mfcc[:max_len, :]
    return mfcc

# --------------------
# Dataset Loading
# --------------------
def load_dataset(data_dir=DATA_DIR, labels_csv=LABELS_CSV):
    """
    Loads the dataset from a CSV file and extracts MFCC features for each audio file.
    
    Returns:
      X: np.array of shape (num_samples, MAX_LEN, N_MFCC)
      y: np.array of shape (num_samples,) with normalized accuracy scores (0-1)
    """
    df = pd.read_csv(labels_csv)
    X, y = [], []
    for idx, row in df.iterrows():
        filename = row["filename"]
        label = row["accuracy_score"]
        audio_path = os.path.join(data_dir, filename)
        if os.path.exists(audio_path):
            mfcc = extract_mfcc(audio_path)
            X.append(mfcc)
            y.append(label)
        else:
            print(f"Warning: {audio_path} not found!")
    X = np.array(X)
    y = np.array(y) / 100.0  # Normalize scores to 0-1 range
    return X, y

# --------------------
# Model Building
# --------------------
def build_model(input_shape):
    """
    Build a CNN + Bidirectional LSTM model for pronunciation evaluation.
    
    Parameters:
      input_shape (tuple): Shape of the input features (MAX_LEN, N_MFCC).
      
    Returns:
      A compiled Keras model.
    """
    model = Sequential([
        Input(shape=input_shape),
        Conv1D(filters=32, kernel_size=3, activation='relu'),
        Dropout(0.3),
        Bidirectional(LSTM(64, return_sequences=True)),
        Bidirectional(LSTM(32)),
        Dense(64, activation='relu'),
        Dense(1, activation='sigmoid')  # Output normalized score (0-1)
    ])
    model.compile(optimizer=Adam(learning_rate=1e-3), 
                  loss='mean_squared_error', 
                  metrics=['mae'])
    return model

def plot_history(history):
    """
    Plot training and validation loss and MAE.
    """
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.legend()
    plt.title("Loss")
    plt.subplot(1, 2, 2)
    plt.plot(history.history['mae'], label='Training MAE')
    plt.plot(history.history['val_mae'], label='Validation MAE')
    plt.legend()
    plt.title("Mean Absolute Error")
    plt.show()

# --------------------
# Main Training Pipeline
# --------------------
def main():
    print("Loading dataset...")
    X, y = load_dataset()
    print(f"Loaded {X.shape[0]} samples.")
    
    # Split the data into training and validation sets
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    
    input_shape = X_train.shape[1:]  # (MAX_LEN, N_MFCC)
    model = build_model(input_shape)
    model.summary()
    
    # Train the model
    history = model.fit(X_train, y_train, epochs=20, batch_size=16, validation_data=(X_val, y_val))
    plot_history(history)
    
    # Evaluate model
    val_loss, val_mae = model.evaluate(X_val, y_val)
    print(f"Validation Loss: {val_loss:.4f}, MAE: {val_mae:.4f}")
    
    # Save the trained model
    model.save("pronunciation_model.h5")
    print("Model saved as pronunciation_model.h5")

if __name__ == "__main__":
    main()
