// ===== Config =====
const API_BASE = "http://localhost:5298";

// const API_BASE = "https://lair-budget-sureness.ngrok-free.dev";

// ===== Scene Setup =====
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xeeeeee);

const camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
camera.position.set(0, 2, 3);
camera.lookAt(0, 1.5, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(400, 400);
document.getElementById("avatar-container").appendChild(renderer.domElement);

// ===== Lights =====
scene.add(new THREE.AmbientLight(0xffffff, 2));

const dirLight = new THREE.DirectionalLight(0xffffff, 2);
dirLight.position.set(5, 10, 5);
scene.add(dirLight);

// ===== Loader =====
const loader = new THREE.GLTFLoader();
let currentModel = null;
let mixer = null;
const clock = new THREE.Clock();
let idleRotation = 0;

// ===== UI Elements =====
const translateBtn = document.getElementById("translateBtn");
const textInput = document.getElementById("textInput");
const loaderSpinner = document.getElementById("loader");
const statusMessage = document.getElementById("statusMessage");

// ===== Load Gesture (with fetch + parse) =====
async function loadGesture(modelUrl) {
  console.log("loadGesture called with (raw):", modelUrl);

  loaderSpinner.classList.remove("hidden");
  statusMessage.textContent = "جاري تحميل الحركة...";
  translateBtn.disabled = true;

  // لو راجع path نسبي /Animations/d.glb
  if (modelUrl.startsWith("/")) {
    modelUrl = API_BASE + modelUrl;
  }

  // ❌ شيل الجزء بتاع http -> https
  // if (modelUrl.startsWith("http://")) {
  //   modelUrl = modelUrl.replace("http://", "https://");
  // }

  console.log("loadGesture using (fixed):", modelUrl);

  try {
    const res = await fetch(modelUrl);

    console.log("GLB STATUS:", res.status, "CONTENT-TYPE:", res.headers.get("content-type"));

    if (!res.ok) {
      throw new Error("فشل تحميل ملف الحركة من السيرفر");
    }

    const contentType = res.headers.get("content-type") || "";

    if (contentType.includes("text/html")) {
      const text = await res.text();
      console.error("Expected GLB but got HTML. First 200 chars:\n", text.slice(0, 200));
      statusMessage.textContent = "السيرفر رجّع صفحة HTML بدل ملف الحركة ❌";
      return;
    }

    const arrayBuffer = await res.arrayBuffer();

    await new Promise((resolve, reject) => {
      loader.parse(
        arrayBuffer,
        "",
        function (gltf) {
          if (currentModel) scene.remove(currentModel);
          if (mixer) {
            mixer.stopAllAction();
            mixer = null;
          }

          const model = gltf.scene;

          const box = new THREE.Box3().setFromObject(model);
          const size = new THREE.Vector3();
          box.getSize(size);
          const maxDim = Math.max(size.x, size.y, size.z);
          const scale = 11 / maxDim;
          model.scale.set(scale, scale, scale);

          const center = new THREE.Vector3();
          box.getCenter(center);
          model.position.sub(center);

          scene.add(model);
          currentModel = model;

          if (gltf.animations && gltf.animations.length > 0) {
            mixer = new THREE.AnimationMixer(model);
            const action = mixer.clipAction(gltf.animations[0]);
            action.reset().play();
          }

          resolve();
        },
        function (error) {
          reject(error);
        }
      );
    });

    statusMessage.textContent = "";

  } catch (error) {
    console.error("GLB ERROR:", error);
    statusMessage.textContent = "حدث خطأ في تحميل الحركة ❌";
  } finally {
    loaderSpinner.classList.add("hidden");
    translateBtn.disabled = false;
  }
}
// ===== API Call (الحل النهائي المحلي) =====
translateBtn.addEventListener("click", async () => {
  const text = textInput.value.trim();
  if (!text) return;

  try {
    statusMessage.textContent = "جاري الترجمة...";
    translateBtn.disabled = true;

    // 🟢 التعديل: إرسال الطلب كـ GET وتمرير النص في الرابط
    const response = await fetch(`${API_BASE}/api/Avatar?word=${encodeURIComponent(text)}`, {
      method: "GET",
      headers: {
        "Accept": "application/json"
      }
    });

    if (!response.ok) {
      throw new Error("الكلمة غير موجودة");
    }

    const data = await response.json();
    console.log("API RESPONSE:", data);

    // البحث عن المسار سواء اسمه url أو animationPath
    let modelUrl = data.url || data.animationPath; 

    if (!modelUrl) {
      statusMessage.textContent = "الـ API مش راجعة لينك حركة صالح ❌";
      translateBtn.disabled = false;
      return;
    }

    console.log("MODEL URL FROM API:", modelUrl);
    await loadGesture(modelUrl);

  } catch (error) {
    console.error("API ERROR:", error);
    statusMessage.textContent = "خطأ: الكلمة غير موجودة في قاعدة البيانات ❌";
    translateBtn.disabled = false;
  }
});

// ===== Render Loop =====
function animate() {
  requestAnimationFrame(animate);

  if (mixer) {
    mixer.update(clock.getDelta());
  } else if (currentModel) {
    idleRotation += 0.003;
    currentModel.rotation.y = idleRotation;
  }

  renderer.render(scene, camera);
}

function animate() {
  requestAnimationFrame(animate);

  if (mixer) {
    mixer.update(clock.getDelta());
  } else if (currentModel) {
    idleRotation += 0.003;
    currentModel.rotation.y = idleRotation;
  }

  renderer.render(scene, camera);
}

animate();