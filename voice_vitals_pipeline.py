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
if __name__ == "__main__":
    engine = VoiceVitalsFusionEngine()

    mock_baseline = {
        "fatigue_mean": 0.20, "fatigue_std": 0.05,
        "hypoxia_mean": 0.10, "hypoxia_std": 0.02,
        "mood_mean": 0.75, "mood_std": 0.15
    }

    try:
        print("\nProcessing 'test_audio.wav'...")
        result_json = engine.process_daily_log("test_audio.wav", mock_baseline)
        print("\n--- Output JSON Payload for Dashboard ---")
        print(result_json)
    except Exception as e:
        print(f"\nERROR: Could not process audio. Did you place 'test_audio.wav' in the folder? \nDetails: {e}")