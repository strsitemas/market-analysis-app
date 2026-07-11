export default function CarregandoHome() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <div className="animate-pulse space-y-4">
        <div className="h-8 w-64 rounded bg-slate-200" />
        <div className="h-4 w-full max-w-md rounded bg-slate-100" />
        <div className="mt-8 grid grid-cols-1 gap-3 sm:grid-cols-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-16 rounded-lg border border-slate-200 bg-slate-50" />
          ))}
        </div>
      </div>
      <p className="mt-6 text-sm text-slate-400">
        Carregando ativos... A primeira consulta do dia pode levar ate 30s.
      </p>
    </main>
  );
}