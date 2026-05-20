# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# import numpy as np
# import pickle
# from tensorflow.keras.models import load_model
# from collections import deque, Counter
# import time

# app = FastAPI()

# # إعداد CORS للسماح للـ frontend بالاتصال
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ==============================
# #       تحميل النموذج
# # ==============================
# print("📦 جاري تحميل النموذج...")
# model = None
# try:
#     model = load_model('sign_language_mlp_rnn_model.h5')
#     print("✅ النموذج تم تحميله بنجاح")
#     print(f"📐 Expected input shape: {model.input_shape}")
# except Exception as e:
#     print(f"❌ خطأ في تحميل النموذج: {e}")
#     model = None

# # ==============================
# #       تحميل التسميات
# # ==============================
# print("📖 جاري تحميل التسميات...")
# try:
#     with open('labels_dict.pickle', 'rb') as f:
#         labels_dict = pickle.load(f)

#     class_names = list(labels_dict.keys())
#     print(f"✅ تم تحميل {len(class_names)} تسمية")
#     print(f"📝 أول 5 تسميات (بعد الترتيب): {class_names[:5]}")
# except Exception as e:
#     print(f"❌ خطأ في تحميل التسميات: {e}")
#     labels_dict = {}
#     class_names = []

# # ==============================
# #   Buffer لتثبيت النتيجة
# # ==============================
# prediction_buffer = deque(maxlen=10)

# # ==============================
# #       نقاط الفحص
# # ==============================
# @app.get("/")
# def home():
#     return {
#         "message": "API شغال 🚀",
#         "model_ready": model is not None,
#         "labels_count": len(class_names),
#     }

# @app.get("/health")
# def health_check():
#     return {
#         "status": "healthy" if model is not None else "model_load_failed",
#         "model_loaded": model is not None,
#         "labels_loaded": len(class_names) > 0,
#         "timestamp": time.time()
#     }

# # ==============================
# #          التنبؤ
# # ==============================
# @app.post("/predict")
# def predict(data: dict):
#     if model is None:
#         return {"error": "Model not loaded. تحقق من رسالة الخطأ في تشغيل السيرفر."}

#     try:
#         if "features" not in data:
#             return {"error": "المدخلات يجب أن تحتوي على المفتاح 'features'"}

#         # تحويل القائم�� إلى np.array
#         features = np.array(data["features"], dtype=np.float32)

#         # 🟢 التعديل هنا: التأكد من أن إجمالي عدد العناصر 225
#         if features.size != 225:
#             return {"error": f"حجم البيانات يجب أن يكون 225، الحجم الحالي: {features.size}"}

#         # 🟢 التعديل هنا: إعادة التشكيل لتصبح ثلاثية الأبعاد (1, 1, 225) للموديلات التسلسلية (LSTM/RNN)
#         features = features.reshape(1, 1, 225)

#         # تنبؤ
#         pred = model.predict(features, verbose=0)
#         idx = int(np.argmax(pred))
#         confidence = float(np.max(pred)) * 100

#         # حماية من تجاوز عدد الـ labels
#         if idx >= len(class_names):
#             print(f"⚠️ Warning: Predicted index {idx} out of range (max={len(class_names)-1})")
#             stabilized_label = "غير معروف"
#         else:
#             raw_label = class_names[idx]                  
#             stabilized_label = labels_dict.get(raw_label, "غير معروف")  

#         # تثبيت النتيجة باستخدام buffer
#         prediction_buffer.append(stabilized_label)
#         final_label = Counter(prediction_buffer).most_common(1)[0][0]

#         print(f"Raw idx: {idx} | Raw: {stabilized_label} | Final: {final_label} | Conf: {confidence:.1f}%")

#         return {
#             "predicted_text": final_label,
#             "confidence": round(confidence, 2)
#         }

#     except Exception as e:
#         print(f"❌ Prediction error: {e}")
#         return {"error": str(e)}



# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# import numpy as np
# import pickle
# from tensorflow.keras.models import load_model
# from collections import deque, Counter

# app = FastAPI()

# # CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # تحميل الموديل
# model = load_model('sign_language_mlp_rnn_model.h5')

# # تحميل labels
# with open('labels_dict.pickle', 'rb') as f:
#     labels_dict = pickle.load(f)

# class_names = list(labels_dict.keys())

# # buffers
# SEQUENCE_LENGTH = 30
# sequence_buffer = deque(maxlen=SEQUENCE_LENGTH)
# prediction_buffer = deque(maxlen=10)


# @app.get("/")
# def home():
#     return {
#         "message": "Sign Language API شغال 🚀",
#         "model_loaded": model is not None,
#         "num_classes": len(class_names)
#     }


# @app.post("/predict")
# def predict(data: dict):
#     try:
#         features = np.array(data["features"], dtype=np.float32)

#         # تصحيح الشكل (مهم جدًا)
#         if len(features.shape) == 1:
#             features = features.reshape(1, -1)
#         elif len(features.shape) == 3 and features.shape[1] == 1:
#             features = features.reshape(1, -1)

#         if features.shape[1] != 225:
#             return {"error": f"Expected 225 features, got {features.shape[1]}"}

#         # التنبؤ
#         pred = model.predict(features, verbose=0)
#         idx = np.argmax(pred)
#         confidence = float(np.max(pred)) * 100

#         if idx >= len(class_names):
#             label = "غير معروف"
#         else:
#             raw_label = class_names[idx]
#             label = labels_dict.get(raw_label, "غير معروف")

#         # تثبيت النتيجة
#         prediction_buffer.append(label)
#         final_label = Counter(prediction_buffer).most_common(1)[0][0]

#         return {
#             "predicted_text": final_label,
#             "confidence": round(confidence, 2)
#         }

#     except Exception as e:
#         return {"error": str(e)}




# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# import numpy as np
# import pickle
# from tensorflow.keras.models import load_model
# from collections import deque, Counter

# app = FastAPI(title="Sign Language Translator")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # تحميل الموديل
# try:
#     model = load_model('sign_language_mlp_rnn_model.h5')
#     print("✅ Model loaded successfully")
# except Exception as e:
#     print(f"❌ Model loading failed: {e}")
#     model = None

# # تحميل labels
# with open('labels_dict.pickle', 'rb') as f:
#     labels_dict = pickle.load(f)

# class_names = list(labels_dict.keys())

# prediction_buffer = deque(maxlen=10)

# @app.get("/")
# def home():
#     return {"message": "Sign Language API شغال 🚀", "model_ready": model is not None}

# @app.post("/predict")
# async def predict(data: dict):
#     if model is None:
#         raise HTTPException(status_code=500, detail="Model not loaded")

#     try:
#         features = np.array(data.get("features", []), dtype=np.float32)

#         # 🟢 التأكد من أن إجمالي عدد العناصر هو 225
#         if features.size != 225:
#             print(f"Shape error: expected 225, got {features.size}")
#             return {"error": f"Expected 225 features, got {features.size}"}

#         # 🟢 الحل السحري: إعادة التشكيل لتصبح (1, 1, 225) لتناسب الـ LSTM
#         features = features.reshape(1, 1, 225)

#         # التنبؤ
#         pred = model.predict(features, verbose=0)
#         idx = np.argmax(pred)
#         confidence = float(np.max(pred)) * 100

#         if idx >= len(class_names):
#             label = "غير معروف"
#         else:
#             raw_label = class_names[idx]
#             label = labels_dict.get(raw_label, "غير معروف")

#         prediction_buffer.append(label)
#         final_label = Counter(prediction_buffer).most_common(1)[0][0]

#         print(f"Prediction: {final_label} | Confidence: {confidence:.1f}%")

#         return {
#             "predicted_text": final_label,
#             "confidence": round(confidence, 2)
#         }

#     except Exception as e:
#         print(f"❌ Prediction error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import pickle
from tensorflow.keras.models import load_model
from collections import deque, Counter

app = FastAPI(title="Sign Language Translator")

# CORS (اختياري لو هتستدعيه من المتصفح مباشرة، لكن مش ضروري لو .NET هو اللي بيكلمه)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Load model =====
try:
    model = load_model("sign_language_mlp_rnn_model.h5")
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Model loading failed: {e}")
    model = None

# ===== Load labels =====
try:
    with open("labels_dict.pickle", "rb") as f:
        labels_dict = pickle.load(f)
    class_names = list(labels_dict.keys())
    print(f"✅ Labels loaded: {len(class_names)}")
except Exception as e:
    print(f"❌ Labels loading failed: {e}")
    labels_dict = {}
    class_names = []

prediction_buffer = deque(maxlen=10)

@app.get("/")
def home():
    return {
        "message": "API running",
        "model_ready": model is not None,
        "labels_count": len(class_names),
    }

@app.post("/predict")
async def predict(data: dict):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        features = np.array(data.get("features", []), dtype=np.float32)

        # لازم 225 رقم
        if features.size != 225:
            return {"error": f"Expected 225 features, got {features.size}"}

        # مناسب لـ RNN/LSTM
        features = features.reshape(1, 1, 225)

        pred = model.predict(features, verbose=0)
        idx = int(np.argmax(pred))

        # confidence من 0..1
        confidence = float(np.max(pred))

        if idx >= len(class_names):
            label = "غير معروف"
        else:
            raw_label = class_names[idx]
            label = labels_dict.get(raw_label, "غير معروف")

        prediction_buffer.append(label)
        final_label = Counter(prediction_buffer).most_common(1)[0][0]

        return {
            "text": final_label,
            "confidence": round(confidence, 4),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))