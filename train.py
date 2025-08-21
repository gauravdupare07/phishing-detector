# train.py
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, classification_report, confusion_matrix
from sklearn.model_selection import GroupShuffleSplit
from features import featurize_dataframe
try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except Exception:
    HAS_XGB = False

RANDOM_STATE = 42
os.makedirs('model', exist_ok=True)

def get_models(pos_weight):
    models = {
        'logreg': LogisticRegression(solver='saga', max_iter=5000, class_weight='balanced', n_jobs=-1, random_state=RANDOM_STATE),
        'rf': RandomForestClassifier(n_estimators=200, class_weight='balanced_subsample', n_jobs=-1, random_state=RANDOM_STATE)
    }
    if HAS_XGB:
        models['xgb'] = XGBClassifier(
            n_estimators=300, learning_rate=0.05,
            objective='binary:logistic', eval_metric='aucpr',
            use_label_encoder=False, random_state=RANDOM_STATE,
            n_jobs=-1, scale_pos_weight=pos_weight
        )
    return models

if __name__ == "__main__":
    df = pd.read_csv('data/urls_clean.csv')  # columns: url,label
    print("Loaded", len(df), "rows")
    X_raw = featurize_dataframe(df)
    y = df['label'].values
    groups = X_raw['group_e2ld'].fillna('NA').values

    # drop grouping columns for feature set
    X = X_raw.drop(columns=['group_e2ld','sld'])  # sld has huge cardinality
    # determine numeric and categorical cols
    categorical_cols = ['scheme','tld']
    numeric_cols = [c for c in X.columns if c not in categorical_cols]

    preprocessor = ColumnTransformer([
        ('num', StandardScaler(), numeric_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols)
    ], remainder='drop')

    # group-aware split
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=RANDOM_STATE)
    train_idx, test_idx = next(gss.split(X, y, groups=groups))
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    # compute pos weight for XGBoost if used
    pos_weight = (len(y_train) - y_train.sum()) / max(1, y_train.sum())

    models = get_models(pos_weight)
    results = []
    for name, clf in models.items():
        pipe = Pipeline([('pre', preprocessor), ('clf', clf)])
        pipe.fit(X_train, y_train)
        proba = pipe.predict_proba(X_test)[:,1]
        preds = (proba >= 0.5).astype(int)
        roc = roc_auc_score(y_test, proba)
        pr = average_precision_score(y_test, proba)
        print(f"\n=== {name} ===")
        print(f"ROC-AUC: {roc:.4f} | PR-AUC: {pr:.4f}")
        print(classification_report(y_test, preds, digits=4))
        print("Confusion matrix:\n", confusion_matrix(y_test, preds))
        results.append({'name':name, 'pipeline':pipe, 'roc':roc, 'pr':pr})

    best = max(results, key=lambda r: r['pr'])
    print(f"\nBest model: {best['name']} with PR-AUC {best['pr']:.4f}")
    artifact = {
        'pipeline': best['pipeline'],
        'feature_columns': X.columns.tolist(),
        'model_name': best['name'],
        'threshold': 0.5
    }
    joblib.dump(artifact, 'model/phishdetector_v1.pkl')
    print("Saved model to model/phishdetector_v1.pkl")

