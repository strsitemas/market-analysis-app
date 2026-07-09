import { listarAtivosDisponiveis } from "@/lib/api";
import { TabelaAnalise } from "@/components/TabelaAnalise";

export default async function AnalisePage() {
  const ativos = await listarAtivosDisponiveis();
  const tickers = ativos.map((a) => a.ticker);

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <h1 className="text-2xl font-bold text-slate-900">
        Tabela de Análise Comparativa
      </h1>
      <p className="mt-1 text-sm text-slate-500">
        Clique nos cabeçalhos para ordenar. Ferramenta de apoio à decisão —
        não é recomendação de investimento.
      </p>

      <div className="mt-6">
        <TabelaAnalise tickers={tickers} />
      </div>
    </main>
  );
}