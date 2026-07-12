# CervicalAI — NotebookLM Podcast Script (2 Voices, 8-12 นาที)

> สำหรับ NotebookLM หรือ AI podcast generator
> 2 voices: Host A (อธิบายปัญหา + impact), Host B (อธิบายเทคนิค + solution)
> ภาษาไทยผสมอังกฤษ (technical term ใช้ EN)

**2026-06-26 UPDATE**: Full 5+ long scripts (research summary, pitch, deploy plan, regulatory, roadmap + bonus) now in artifacts/PODCAST_SCRIPTS.md bundle + 7 dedicated podcast_*.md files. All heavy generated from DEEP_RESEARCH, ROADMAP, DEPLOY_PLAN, REGULATORY, proposal, etc. See artifacts/ for complete text artifacts ready for audio gen.


---

## [INTRO — 30 วินาที]

**Host A**: สวัสดีครับ วันนี้เราจะพูดถึงปัญหาที่หลายคนอาจไม่เคยได้ยิน — "มะเร็งปากมดลูก" กับ "การคัดกรองที่หายไป"

**Host B**: ทุกปีในไทย มีผู้หญิงเกือบครึ่งที่ผลคัดกรองผิดปกติ... หายไป 41% ไม่กลับมารักษา

**Host A**: 41%... นั่นคือเกือบ 2 ใน 5 คน

**Host B**: ระหว่างรอผล 1-2 สัปดาห์... มะเร็งดำเนินต่อ เจอช้า รักษาช้า เสียชีวิตเพิ่ม

**Host A**: วันนี้เราจะคุยเรื่อง "CerviCo-Pilot" — AI ที่อาจช่วยแก้ปัญหานี้ได้

---

## [PROBLEM — 2 นาที]

**Host A**: เริ่มจากตัวเลขก่อน — coverage การคัดกรองปากมดลูกในไทยตกจาก 77.5% เป็น 53.9% ขณะที่ WHO ต้องการ 70% ภายใน 2030

**Host B**: นั่นคือเรากำลังถอยหลัง ขณะที่โลกกำลังเดินหน้า

**Host A**: แล้วทำไมคนถึงหาย?

**Host B**: สาเหตุหลัก 3 ข้อ:
1. ไม่เข้าใจจดหมายแจ้งผล — 35.6% บอกว่าไม่รู้ว่าต้องทำอะไรต่อ
2. เดินทางไกล — รพ.ชุมชนส่งสไลด์ไป รพ.ใหญ่ รอ 1-2 สัปดาห์
3. ไม่มีพยาธิแพทย์ในรพ.เล็ก — ต้องส่งต่อ

**Host A**: แล้วระหว่างรอ... มะเร็งกำลังโต

**Host B**: ถูกต้อง — นี่คือ "loss-to-follow-up" ที่ฆ่าคน

**Host A**: WHO ตั้งเป้า "90-70-90" ภายใน 2030:
- 90% ของเด็กหญิงได้วัคซีน HPV
- 70% ของผู้หญิงได้คัดกรองคุณภาพสูง 2 ครั้ง
- 90% ของผู้ป่วยได้รับการรักษา

**Host B**: เราตกที่ข้อ 2 — coverage ต่ำ + คนหาย 41%

---

## [SOLUTION — 3 นาที]

**Host A**: แล้ว CerviCo-Pilot แก้ยังไง?

**Host B**: หลักการง่ายมาก: "AI ให้ผลทันที + รายงานเข้าใจง่าย"

**Host A**: ลองเล่า flow ให้ฟังหน่อย

**Host B**: ภาพ Pap หรือ ThinPrep → เข้า AI → ได้ 5 อย่างพร้อมกัน:

1. ระดับ Bethesda: NILM, LSIL, HSIL, SCC
2. Koilocyte flag: ร่องรอยการติด HPV
3. Heatmap: Grad-CAM แสดงจุดที่ AI โฟกัส
4. Uncertainty: MC Dropout บอกว่า "ฉันไม่มั่นใจ 100%"
5. รายงาน 2 ชั้น

**Host A**: รายงาน 2 ชั้นคืออะไร?

**Host B**: ชั้น 1 สำหรับแพทย์ — ศัพท์เทคนิค + triage rule เช่น "ส่ง Colposcopy ด่วน"

ชั้น 2 สำหรับผู้ป่วย — ภาษาไทยง่าย เช่น "พบเซลล์ผิดปกติระดับสูง ควรพบแพทย์โดยเร็ว"

**Host A**: แล้วแพทย์ยังต้องยืนยันไหม?

**Host B**: ต้อง! ทุกผลต้องแพทย์ลงนามก่อนปล่อย — AI เป็น "co-pilot" ไม่ใช่ "autopilot"

**Host A**: แล้วเทคโนโลยีที่ใช้คืออะไร?

**Host B**: EfficientNet-B0 — โมเดลเบา ใช้ transfer learning จาก ImageNet ฝึกด้วย public dataset ฟรี 3 ชุด: SIPaKMeD, RepoMedUNM, Mendeley LBC

**Host A**: ราคาแพงไหม?

**Host B**: นี่คือจุดต่าง — ใช้ smartphone + adapter ราคา 2,000-5,000 บาท ไม่ต้อง scanner แพงเหมือน Hologic

---

## [EVIDENCE — 1.5 นาที]

**Host A**: มีหลักฐานไหมว่าแบบนี้ใช้ได้จริง?

**Host B**: มีครับ:
- Hologic Genius FDA-cleared กุมภาพันธ์ 2024 — พิสูจน์ตลาดมีจริง
- Nature Communications 2025 — AI + compact microscope ใน LMIC ทำได้จริง AUC 0.85-0.89
- การศึกษาหนึ่งพบว่า AI-assisted cytopathologist มี sensitivity สูงขึ้น 13.3%

**Host A**: แล้ว HPV ในไทยต่างจากตะวันตกไหม?

**Host B**: ต่างครับ — HPV 52 และ 58 เด่นในไทย ไม่ใช่ 16/18 แบบตะวันตก → จึงต้องมีโมเดลที่ fine-tune กับข้อมูลไทย

---

## [DIFFERENTIATOR — 1 นาที]

**Host A**: แล้วต่างจากเจ้าใหญ่ยังไง?

**Host B**: ตารางเปรียบเทียบสั้นๆ:

| เจ้าใหญ่ | CerviCo-Pilot |
|----------|---------------|
| แพงมาก | ราคาถูก (2-5k บาท) |
| Black-box | XAI + Uncertainty ครบ |
| ไม่มีรายงานชาวบ้าน | รายงาน 2 ชั้น |
| ต้อง scanner เฉพาะ | ใช้กล้องที่มีได้ |

**Host A**: เราอยู่ในช่องว่างราคา

**Host B**: ถูกต้อง — Hologic พิสูจน์ตลาด แต่ราคายืนยันช่องว่าง

---

## [IMPACT — 1 นาที]

**Host A**: Impact คืออะไร?

**Host B**: 
- ตรง WHO 90-70-90
- แก้ loss-to-follow-up 41% โดยตรง
- ต้นแบบ CLMV (low-resource setting)
- Cost per screen ใกล้ 0 หลังลงทุน

**Host A**: ถ้าแก้ loss-to-follow-up จาก 41% เป็น 20% ในรพ.ชุมชน 100 แห่ง...

**Host B**: คนที่กลับมารักษาเพิ่ม ~10,500 คนต่อปี — และอาจช่วยชีวิตได้หลายร้อยคน

---

## [ROADMAP — 45 วินาที]

**Host A**: แล้วแผนคืออะไร?

**Host B**: 
- Phase 1 (ตอนนี้): POC 2D + XAI + Web demo + Public data
- Phase 2: Thai fine-tune + Z-stack 2.5D + SAM2 editable + Edge
- Phase 3: Reader study + Pilot รพ.ชุมชน + Thai FDA pathway

**Host A**: Phase 1 ทำเสร็จแล้วเหรอ?

**Host B**: ครับ — มีโมเดล 16 MB, 15 heatmaps, web demo เปิดได้, pitch deck 17 สไลด์

---

## [Q&A — 1 นาที]

**Host A**: มีคำถามที่พบบ่อยไหม?

**Host B**: คำถามที่ 1: ทำไมไม่ใช้ foundation model? คำตอบ: ดี แต่หนัก + pretrain ส่วนใหญ่ histology Phase 1 ใช้ EfficientNet ก่อน

คำถามที่ 2: มี Thai data จริงไหม? คำตอบ: ยังไม่มี public → Phase 1 ใช้ public + ระบุ limitation

คำถามที่ 3: Pseudokoilocyte จะ false+ ไหม? คำตอบ: เป็นไปได้ → flag เป็น limitation

**Host A**: สรุปสั้นๆ?

**Host B**: "เราไม่ใช่คนแรกที่ทำ AI cytology แต่เราเป็นคนแรกที่ออกแบบเพื่อ รพ.ชุมชนไทย + แก้ loss-to-follow-up ด้วยรายงานชาวบ้าน + XAI ที่หมอเชื่อถือได้"

---

## [OUTRO — 15 วินาที]

**Host A**: CerviCo-Pilot — AI co-pilot สำหรับคัดกรองมะเร็งปากมดลูก

**Host B**: สำหรับ รพ.ชุมชนไทย... ที่คนไม่ควรหาย

**Host A**: ขอบคุณที่รับฟัง

**Host B**: หากสนใจ ดูได้ที่ GitHub หรือติดต่อทีม

---

## [END]

**Duration**: ~8-12 นาที (ขึ้นกับความเร็วพูด + หยุด)
**Tone**: จริงจัง + หวัง + มืออาชีพ
**Music**: Soft piano / ambient (ถ้ามี)

---

*Script สำหรับ NotebookLM หรือ AI podcast generator — ปรับได้ตามความต้องการ*
