export default function CarregandoAtivo() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <div className="animate-pulse space-y-4">
        <div className="h-6 w-32 rounded bg-slate-200" />
        <div className="h-9 w-48 rounded bg-slate-200" />
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="h-20 rounded-lg border border-slate-200 bg-slate-50" />
          ))}
        </div>
        <div className="h-72 rounded-lg border border-slate-200 bg-slate-50" />
      </div>
      <p className="mt-4 text-sm text-slate-400">
        Carregando analise do ativo... A primeira consulta do dia pode levar ate 30s.
      </p>
    </main>
  );
}