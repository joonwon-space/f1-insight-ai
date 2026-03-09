export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center gap-8 py-16">
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight">
          Welcome to <span className="text-f1-red">F1 Insight AI</span>
        </h1>
        <p className="mt-3 text-lg text-neutral-400">
          F1 news aggregation, LLM-powered summarization & Korean translation
        </p>
        <p className="mt-1 text-sm text-neutral-500">
          F1 뉴스 수집, AI 요약 및 한국어 번역 서비스
        </p>
      </div>

      <div className="grid w-full max-w-2xl gap-4 sm:grid-cols-3">
        <FeatureCard
          title="News"
          description="Auto-collected F1 news and interviews from multiple sources."
          descriptionKr="다양한 소스에서 자동 수집된 F1 뉴스 및 인터뷰"
        />
        <FeatureCard
          title="AI Summary"
          description="LLM-powered article summarization for quick insights."
          descriptionKr="빠른 인사이트를 위한 AI 기반 기사 요약"
        />
        <FeatureCard
          title="Translation"
          description="Automatic Korean translation of English F1 content."
          descriptionKr="영문 F1 콘텐츠의 자동 한국어 번역"
        />
      </div>

      <div className="rounded-lg border border-neutral-800 bg-neutral-900 px-6 py-4 text-center">
        <p className="text-sm text-neutral-500">
          Data ingestion and AI summarization pipelines are being built.
          <br />
          Check back soon for live content.
        </p>
      </div>
    </div>
  );
}

function FeatureCard({
  title,
  description,
  descriptionKr,
}: Readonly<{
  title: string;
  description: string;
  descriptionKr: string;
}>) {
  return (
    <div className="rounded-lg border border-neutral-800 bg-neutral-900 p-4 transition-colors hover:border-f1-red/40">
      <h2 className="mb-2 text-sm font-semibold text-white">{title}</h2>
      <p className="text-xs leading-relaxed text-neutral-400">{description}</p>
      <p className="mt-1 text-xs leading-relaxed text-neutral-500">
        {descriptionKr}
      </p>
    </div>
  );
}
