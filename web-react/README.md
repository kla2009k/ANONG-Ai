# DermaTrace AI — Frontend (React + Vite + Tailwind + shadcn-style)

ฟรอนต์เอนด์ React สำหรับ DermaTrace AI ออกแบบธีม **dark clinical** (charcoal + teal/violet)
เรียก Python FastAPI backend เดิม (REST) ไม่มี login — เปิดใช้ได้ทันที

ต้นแบบ pattern/UX มาจากเว็บ DermaVision (Manus) แต่ปรับเป็น stack เบา ไม่ผูก platform:
- ❌ ไม่มี OAuth / tRPC / MySQL / forge proxy (ของ Manus)
- ✅ React 19 + Vite 7 + Tailwind 4 + shadcn-style components (Radix) + lucide icons

## โครงสร้าง
```
web-react/
├── src/
│   ├── App.tsx              # หน้าเดียว: header + hero + uploader + results
│   ├── index.css            # ธีม dark clinical (oklch tokens)
│   ├── lib/api.ts           # fetch /api/health, /api/analyze + types
│   ├── lib/utils.ts         # cn()
│   └── components/
│       ├── Uploader.tsx     # drag-drop อัปโหลดภาพ
│       ├── ResultView.tsx   # advisory + tabs (ภาพรวม/ภาพวิเคราะห์) + 7-class bars
│       └── ui/              # button, card, badge, tabs (shadcn-style)
└── vite.config.ts           # build → ../web  ·  dev proxy /api → :8002
```

## พัฒนา (dev)
```bash
# terminal 1 — backend
cd ../server && py -m uvicorn app:app --port 8002
# terminal 2 — frontend (hot reload, proxy /api → 8002)
cd web-react && npm run dev    # เปิด http://localhost:5173
```

## Build (โปรดักชัน — FastAPI เสิร์ฟเอง)
```bash
cd web-react && npm run build  # output → ../web
cd ../server && py -m uvicorn app:app --port 8002
# เปิด http://localhost:8002
```
> `npm run build` เขียนทับโฟลเดอร์ `../web` (เวอร์ชัน vanilla เดิม backup ไว้ที่ `web-vanilla-backup/`)

## API ที่เรียก
- `GET /api/health` → `{ ok, segmentation, classification, classes, gemini }`
- `POST /api/analyze { image: dataURL }` → `{ segmentation{overlay,heatmap,area_pct,found}, classification[], top, advisory, classification_mode, disclaimer }`
- `POST /api/report { image, analysis }` → รายงาน AI จาก **Gemini (multimodal)** วิเคราะห์ภาพจริง
  → `{ status: "ok"|"no_key"|"quota"|"error", report?{findings,impression,recommendation,risk}(2 ภาษา), message? }`

## Gemini AI Report (ฟีเจอร์ใหม่ — ดีกว่า AMRG ของ DermaVision)
- ส่ง **ภาพจริง** ให้ Gemini ดู (multimodal) → รายงาน 4 ส่วน ไทย/อังกฤษ — เป็น LLM-vision จริง ไม่ใช่อ่านแค่ text
- key อยู่ `server/.env` (`GEMINI_API_KEY`, `GEMINI_MODEL=gemini-2.5-flash`) — **ไม่ commit** (ใน .gitignore)
- รายงานมีหัวข้อ **MODEL VIEW** (โมเดลเห็นอะไร/เพราะอะไร) — ส่ง Grad-CAM + ผล 7 คลาส ให้ Gemini grounded
- โควต้าแยกตาม model: ถ้า model ไหน 429 ลองเปลี่ยน `GEMINI_MODEL` (2.5-flash / 2.0-flash / flash-lite)
- ⚠️ รัน server แบบ **persistent** (ไม่ใช่ detached ที่ตายเมื่อ shell ปิด) ไม่งั้นเว็บจะ "Failed to fetch"
- จัดการ error ครบ: ไม่มี key → `no_key` · โควต้าหมด (429) → `quota` · อื่นๆ → `error` (UI แสดงข้อความ ไม่ crash)
- ⚠️ ถ้า key เคยแชร์ในแชท/log → **rotate ใหม่**; ถ้าเจอ `quota` ต้องเปิด billing หรือรอ quota รายวัน reset

ป้ายกำกับตรงตามจริยธรรมโปรเจกต์: segmentation = "CV จริง", classification = "เดโม"
จนกว่าจะเสียบ ResNet จริง (`classification_mode === "model"` → ป้ายเปลี่ยนเป็น "โมเดลจริง")
