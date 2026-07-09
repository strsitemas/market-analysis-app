import { ResumoMercado } from "@/components/ResumoMercado";

export default function PaginaDashboard() {
  return (
    <main className="mx-auto max-w-6xl px-4 py-8">
      <h1 className="text-2xl font-bold text-slate-900">Dashboard geral do mercado</h1>
      <p className="mt-1 text-sm text-slate-500">
        Visao consolidada dos ativos monitorados, com sinais e destaques de risco/oportunidade.
      </p>
      <div className="mt-6">
        <ResumoMercado />
      </div>
    </main>
  );
}