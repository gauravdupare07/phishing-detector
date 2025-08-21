# infer.py
import joblib
import pandas as pd
from features import extract_features

ARTIFACT = 'model/phishdetector_v1.pkl'

class Detector:
    def __init__(self, path=ARTIFACT):
        obj = joblib.load(path)
        self.pipeline = obj['pipeline']
        self.feature_columns = obj['feature_columns']
        self.threshold = obj.get('threshold', 0.5)

    def prepare_df(self, url):
        feats = extract_features(url)
        df = pd.DataFrame([feats])
        # ensure all expected columns exist
        for c in self.feature_columns:
            if c not in df.columns:
                df[c] = 0
        df = df[self.feature_columns]
        return df

    def predict_one(self, url):
        df = self.prepare_df(url)
        proba = float(self.pipeline.predict_proba(df)[:,1][0])
        label = int(proba >= self.threshold)
        return {'url': url, 'label': label, 'proba': proba, 'prediction': 'Phishing' if label==1 else 'Legitimate'}

if __name__ == "__main__":
    d = Detector()
    tests = [
        "http://secure-paypal.com.login.verify-account.xyz/Confirm?user=test@example.com",
        "https://www.google.com/"
    ]
    for t in tests:
        print(d.predict_one(t))
