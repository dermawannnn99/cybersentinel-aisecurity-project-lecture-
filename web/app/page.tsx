import { ScanWorkbench } from "@/components/scan-workbench";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function HomePage() {
  return (
    <main className="relative overflow-hidden">
      <div className="absolute inset-0 bg-hero-grid bg-[size:56px_56px] opacity-30" />
      <div className="relative mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-10 px-6 py-8 lg:px-10 lg:py-10">
        <section className="max-w-5xl space-y-5">
          <p className="inline-flex rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs uppercase tracking-[0.28em] text-signal">
            Analyst Dashboard v1
          </p>
          <div className="space-y-4">
            <h1 className="max-w-4xl text-4xl font-semibold leading-tight text-white sm:text-5xl lg:text-6xl">
              Scan traffic and find threats directly in your browser.
            </h1>
            <p className="max-w-2xl text-base leading-7 text-mist/80 sm:text-lg">
              CyberSentinel AI brings the same Python scanning engine into a simple web dashboard.
            </p>
          </div>
        </section>

        <ScanWorkbench apiBaseUrl={apiBaseUrl} />
      </div>
    </main>
  );
}
