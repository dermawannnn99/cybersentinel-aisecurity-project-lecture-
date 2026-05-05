import { ScanWorkbench } from "@/components/scan-workbench";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function HomePage() {
  return (
    <main className="relative overflow-hidden">
      <div className="absolute inset-0 bg-hero-grid bg-[size:56px_56px] opacity-30" />
      <div className="relative mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-10 px-6 py-8 lg:px-10 lg:py-10">
        <section className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
          <div className="space-y-6">
            <p className="inline-flex rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs uppercase tracking-[0.28em] text-signal">
              Analyst Dashboard v1
            </p>
            <div className="space-y-4">
              <h1 className="max-w-4xl text-4xl font-semibold leading-tight text-white sm:text-5xl lg:text-6xl">
                Scan traffic, surface threats, and ship findings without leaving the browser.
              </h1>
              <p className="max-w-2xl text-base leading-7 text-mist/80 sm:text-lg">
                CyberSentinel AI now runs as a web-first analyst console backed by the same Python
                engine you already use in the CLI.
              </p>
            </div>
          </div>

          <div className="grid gap-4 rounded-[28px] border border-white/10 bg-white/5 p-5 shadow-panel backdrop-blur">
            <div>
              <p className="text-xs uppercase tracking-[0.24em] text-cobalt">Stack Alignment</p>
              <p className="mt-2 text-2xl font-semibold text-white">Next.js + FastAPI</p>
            </div>
            <div className="grid gap-3 text-sm text-mist/80 sm:grid-cols-3">
              <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
                <p className="font-medium text-white">Server-first UI</p>
                <p className="mt-1">No boot-time data waterfall.</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
                <p className="font-medium text-white">Single scan flow</p>
                <p className="mt-1">Demo or upload, then review threats.</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
                <p className="font-medium text-white">Ephemeral export</p>
                <p className="mt-1">CSV stays available for the active session.</p>
              </div>
            </div>
          </div>
        </section>

        <ScanWorkbench apiBaseUrl={apiBaseUrl} />
      </div>
    </main>
  );
}
