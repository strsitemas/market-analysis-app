export default function CarregandoAnalise() {
  return (
    <main className="mx-auto max-w-6xl px-4 py-8">
      <div className="animate-pulse space-y-4">
        <div className="h-7 w-72 rounded bg-slate-200" />
        <div className="h-4 w-96 rounded bg-slate-100" />
        <div className="mt-6 flex gap-3">
          <div className="h-9 w-48 rounded bg-slate-100" />
          <div className="h-9 w-40 rounded bg-slate-100" />
        </div>
        <div className="mt-4 h-80 rounded-lg border border-slate-200 bg-slate-50" />
      </div>
      <p className="mt-4 text-sm text-slate-400">
        Carregando tabela comparativa... A primeira consulta do dia pode levar ate 30s.
      </p>
    </main>
  );
}