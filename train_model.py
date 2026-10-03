import pickle

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

# ---------- 1. โหลดข้อมูลที่ทำความสะอาดแล้ว ----------
df = pd.read_csv('training_data_cleaned.csv')

target = 'Depression'
features = [c for c in df.columns if c != target]   # ลำดับเหมือนเดิมทุกประการ

# ---------- 2. แปลงข้อความเป็นตัวเลข ----------
cat_cols = ['Gender', 'Sleep Duration', 'Dietary Habits', 'Family History of Mental Illness']
encoders = {}
for col in cat_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

# ---------- 3. แบ่ง train/test ----------
X = df[features]
y = df[target]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print("จำนวนข้อมูล train:", len(X_train), "/ test:", len(X_test))

# ---------- 4. หาค่า k ที่เหมาะสมของ kNN ----------
print("\nทดลองค่า k ของ kNN:")
for k in [3, 5, 7, 11, 15, 21, 31, 41]:
    knn_try = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=k))
    knn_try.fit(X_train, y_train)
    acc = accuracy_score(y_test, knn_try.predict(X_test))
    print(f"  k = {k:2d} -> accuracy = {acc:.4f}")

# ---------- 5. เทรนทุกโมเดลแล้วเทียบกัน ----------
models = {
    'DecisionTree': DecisionTreeClassifier(max_depth=6, random_state=42),
    'RandomForest': RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42),
    'kNN': make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=31)),
    'ANN_MLP': MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=500, random_state=42),
}

results = {}
trained_models = {}
for name, model in models.items():
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    results[name] = accuracy_score(y_test, pred)
    trained_models[name] = model
    print(f"\n=== {name} ===")
    print("Accuracy:", round(results[name], 4))
    print(classification_report(y_test, pred))

print("\nสรุปผลทุกโมเดล:")
for name, acc in results.items():
    print(f"  {name:13s} {acc:.4f}")

# ---------- 6. เลือกโมเดลที่ดีที่สุด ----------
best_name = max(results, key=results.get)
print(f"\nโมเดลที่ดีที่สุดคือ: {best_name} (accuracy = {results[best_name]:.4f})")

# ---------- 7. บันทึกไฟล์ ----------
with open('model.pkl', 'wb') as f:
    pickle.dump(trained_models[best_name], f)
with open('encoders.pkl', 'wb') as f:
    pickle.dump(encoders, f)
with open('feature_list.pkl', 'wb') as f:
    pickle.dump(features, f)

print("บันทึก model.pkl, encoders.pkl, feature_list.pkl เรียบร้อยแล้ว")