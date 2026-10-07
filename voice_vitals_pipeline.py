import librosa
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import whisper
from transformers import pipeline
import json
import warnings

warnings.filterwarnings("ignore")  # Hides unnecessary PyTorch/HuggingFace warnings


# 1. AUDIO CNN ARCHITECTURE
class MFCC_CNN(nn.Module):
    def __init__(self):
        super(MFCC_CNN, self).__init__()
        self.conv1 = nn.Conv1d(in_channels=13, out_channels=32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(in_channels=32, out_channels=64, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(64, 32)
        self.fc2 = nn.Linear(32, 2)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool1d(x, 2)
        x = F.relu(self.conv2(x))
        x = F.adaptive_avg_pool1d(x, 1).squeeze(2)
        x = F.relu(self.fc1(x))
        x = torch.sigmoid(self.fc2(x))
        return x


# 2. MAIN FUSION ENGINE
class VoiceVitalsFusionEngine:
    def __init__(self, sample_rate=16000):
        self.sr = sample_rate
        print("Loading local models (this takes a moment on the first run)...")

        self.stt_model = whisper.load_model("tiny.en")
        self.sentiment_model = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

        self.acoustic_cnn = MFCC_CNN()
        self.acoustic_cnn.eval()

    def analyze_acoustics(self, audio_path: str) -> dict:
        y, sr = librosa.load(audio_path, sr=self.sr)
        y_trimmed, _ = librosa.effects.trim(y, top_db=25)

        mfcc = librosa.feature.mfcc(y=y_trimmed, sr=sr, n_mfcc=13)
        mfcc_tensor = torch.tensor(mfcc).unsqueeze(0).float()

        with torch.no_grad():
            cnn_outputs = self.acoustic_cnn(mfcc_tensor)
            fatigue_cnn_score = cnn_outputs[0][0].item()
            hypoxia_cnn_score = cnn_outputs[0][1].item()

        return {
            "acoustic_fatigue_score": round(fatigue_cnn_score, 3),
            "acoustic_hypoxia_score": round(hypoxia_cnn_score, 3)
        }

    def analyze_sentiment(self, audio_path: str) -> dict:
        result = self.stt_model.transcribe(audio_path)
        transcript = result["text"].strip()
        sentiment_out = self.sentiment_model(transcript)[0]

        score = sentiment_out["score"]
        valence = score if sentiment_out["label"] == "POSITIVE" else -score

        return {"transcript": transcript, "mood_valence": round(valence, 3)}

    def evaluate_against_baseline(self, current: dict, baseline: dict) -> dict:
        fatigue_drift = (current["acoustic_fatigue_score"] - baseline["fatigue_mean"]) / (
                    baseline["fatigue_std"] + 1e-6)
        hypoxia_drift = (current["acoustic_hypoxia_score"] - baseline["hypoxia_mean"]) / (
                    baseline["hypoxia_std"] + 1e-6)
        mood_drift = (baseline["mood_mean"] - current["mood_valence"]) / (baseline["mood_std"] + 1e-6)

        return {
            "fatigue_alert": bool(fatigue_drift > 2.0),
            "hypoxia_alert": bool(hypoxia_drift > 2.5),
            "isolation_stress_alert": bool(mood_drift > 1.5),
            "z_scores": {
                "fatigue_sigma": round(fatigue_drift, 2),
                "hypoxia_sigma": round(hypoxia_drift, 2),
                "mood_sigma": round(mood_drift, 2)
            }
        }

    def process_daily_log(self, audio_path: str, astro_baseline: dict) -> str:
        acoustics = self.analyze_acoustics(audio_path)
        nlp_data = self.analyze_sentiment(audio_path)

        current_state = {**acoustics, **nlp_data}
        anomalies = self.evaluate_against_baseline(current_state, astro_baseline)

        payload = {
            "pillar": "2. Passive Biometrics (Voice Vitals)",
            "telemetry": current_state,
            "anomalies": anomalies
        }
        return json.dumps(payload, indent=2)


# 3. EXECUTION BLOCK
        import os

        def load_astronaut_baseline(crew_id: str, db_path="astronaut_profiles.json") -> dict:
            """Simulates a database fetch for the astronaut's historical baseline."""
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"Database {db_path} not found.")

            with open(db_path, "r") as db_file:
                profiles = json.load(db_file)

            if crew_id not in profiles:
                raise ValueError(f"Crew ID {crew_id} not found in database.")

            return profiles[crew_id]

        # ==========================================
        # 3. EXECUTION BLOCK
        # ==========================================
        if __name__ == "__main__":
            engine = VoiceVitalsFusionEngine()
            current_user_id = "ASTRO-01"

            try:
                print(f"\nFetching medical baseline for {current_user_id}...")
                user_baseline = load_astronaut_baseline(current_user_id)

                # 1. Prompt the user to type the exact filename
                print("\nAvailable files in folder: ", [f for f in os.listdir() if f.endswith('.wav')])
                target_file = input("Enter the exact name of the .wav file to process (e.g., test_audio.wav): ")

                # 2. Check if the file they typed actually exists
                if not os.path.exists(target_file):
                    print(f"\nERROR: Could not find '{target_file}' in this folder. Check your spelling!")
                else:
                    # 3. Process only that specific file
                    print(f"\nProcessing {target_file}...")
                    result_json = engine.process_daily_log(target_file, user_baseline)

                    print("\n--- Output JSON Payload for Dashboard ---")
                    print(result_json)

            except Exception as e:
                print(f"\nERROR: {e}")