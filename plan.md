# Plan Build UI, API, dan Deployment CyberSentinel AI

## Summary
- Bangun UI web v1 sebagai **dashboard analyst** berbasis **Next.js App Router + TypeScript**, dengan backend terpisah **FastAPI** yang membungkus engine Python yang sekarang.
- Pertahankan **CLI existing** sebagai jalur offline/debug, lalu ekstrak alur analisis agar bisa dipakai ulang oleh CLI dan API tanpa duplikasi logika.
- Target deployment v1: **frontend di Vercel**, **backend Python di Railway**, dengan mode pemrosesan **interactive small-medium files**; dataset besar tetap diarahkan ke CLI/offline.
- UI stack disesuaikan dengan skill `vercel-react-best-practices`: **server-first rendering**, minim client components, hindari fetch waterfalls, pakai `SWR` hanya saat benar-benar perlu, dan defer komponen/chart berat via dynamic import.

## Implementation Changes
- Tambahkan app frontend baru di `web/` memakai **Next.js 15 App Router**, **React 19**, **TypeScript**, **Tailwind CSS**, dan komponen UI ringan yang tidak memaksa seluruh halaman menjadi client component.
- Tambahkan service backend baru di `api/` memakai **FastAPI**, sementara engine Python saat ini di root tetap dipakai sebagai domain layer sampai ekstraksi reusable service selesai.
- Refactor alur Python menjadi fungsi reusable: `load dataset -> run rules -> run isolation forest -> score -> shape response`, lalu pakai alur yang sama dari CLI dan API.
- UI v1 terdiri dari satu flow utama: pilih `Demo` atau `Upload Dataset`, jalankan scan, tampilkan summary risiko, top threats, distribusi level, tabel hasil, dan tombol export CSV.
- Halaman hasil memakai **server components untuk shell dan config**, sedangkan uploader, filter tabel, dan chart interaktif menjadi client components terisolasi.
- Untuk performa sesuai skill Vercel:
  - initial page jangan fetch data yang belum dibutuhkan
  - upload/scan request tetap satu arah ke backend, tanpa waterfall antar endpoint
  - komponen chart di-load dengan dynamic import
  - pencarian/filter tabel memakai `startTransition` dan `useDeferredValue`
  - hindari barrel imports dan shared mutable module state
- Backend v1 diproses **sinkron** dengan batas file kecil-menengah; hasil scan bersifat **ephemeral**, cukup untuk satu sesi analisis tanpa histori multi-user.
- Tambahkan dokumentasi dev/deploy di root README: cara jalanin FE, BE, env vars, local integration, dan alur deploy Vercel + Railway.

## Public APIs and Interfaces
- Tambahkan `POST /api/v1/scans/demo`
  - body: `{ rows?: number, showSafe?: boolean, maxDisplay?: number }`
  - return: `ScanResponse`
- Tambahkan `POST /api/v1/scans/upload`
  - multipart: `file`, `showSafe?`, `maxDisplay?`
  - return: `ScanResponse`
- Tambahkan `GET /api/v1/exports/{token}`
  - stream CSV hasil scan dari sesi aktif
- Tambahkan `GET /api/v1/health`
  - return status readiness untuk Railway dan smoke check
- Bentuk `ScanResponse` distandarkan:
  - `meta`: mode, filename, rowCount, processingTimeMs
  - `summary`: total, critical, high, medium, low, safe, anomalyCount
  - `topThreats`: array `{ name, count }`
  - `distribution`: array `{ level, count }`
  - `rows`: array hasil analisis dengan field utama `src_ip`, `dst_ip`, `protocol`, `dst_port`, `if_anomaly`, `threats`, `risk_score`, `risk_label`
  - `exportToken`: token sementara untuk download CSV
  - `warnings`: info file limit, label unknown, atau normalisasi kolom
- Frontend mengonsumsi kontrak API dari OpenAPI FastAPI; type TS digenerate dari schema agar web dan API tetap sinkron.

## Test Plan
- Backend unit tests:
  - loader untuk format custom, CICIDS 2017, dan NSL-KDD
  - rules engine dan scorer tetap menghasilkan label/risk score yang konsisten
  - API demo scan menghasilkan `ScanResponse` valid
  - upload file valid, invalid, dan missing columns ditangani dengan error yang jelas
  - file di atas limit ditolak dengan status dan pesan yang konsisten
- Frontend tests:
  - render dashboard tanpa scan
  - submit demo scan dan tampil summary + tabel
  - upload dataset lalu tampil hasil dan export button
  - filter/search tabel tetap responsif saat data besar
  - error state backend, timeout, dan invalid file tampil ramah
- End-to-end checks:
  - local FE ke local BE
  - Vercel preview ke Railway staging
  - export CSV sesuai hasil yang ditampilkan
  - health endpoint dan CORS benar untuk domain frontend
- CI minimum:
  - backend `pytest`
  - frontend `lint`, `typecheck`, `build`
  - optional Playwright smoke test untuk flow demo scan

## Assumptions and Defaults
- UI v1 adalah **dashboard analyst**, bukan product multi-user; **tidak ada auth** di fase ini.
- Deployment dikunci ke **Vercel untuk FE** dan **Railway untuk BE**; backend tidak dijalankan di Vercel serverless karena dependency ML dan workload file upload lebih cocok di service Python terpisah.
- CLI `cybersentinel.py` tetap dipertahankan dan dianggap jalur resmi untuk dataset besar/offline batch.
- V1 hanya mendukung **interactive small-medium processing**; mulai dengan hard cap upload sekitar **25 MB** dan hasil scan tidak dipersistenkan lintas restart/deploy.
- Frontend base URL backend diatur via env `NEXT_PUBLIC_API_BASE_URL`; backend membatasi CORS ke domain Vercel yang diizinkan.
- Jika nantinya perlu dataset besar, histori scan, atau multi-user, ekspansi berikutnya adalah job queue + object storage + database, tetapi itu di luar scope plan v1 ini.
