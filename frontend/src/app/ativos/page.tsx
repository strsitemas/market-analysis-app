import { listarAtivosDisponiveis, obterAnaliseMultipla } from "@/lib/api";
import { TabelaAtivos } from "@/components/TabelaAtivos";

export default async function PaginaAtivos() {
  const disponiveis = await listarAtivosDisponiveis();
  const tickers = disponiveis.map((a) => a.ticker);
  const { resultados, erros } = await obterAnaliseMultipla(tickers);

  return (
    <main className="mx-auto max-w-6xl px-4 py-8">
      <h1 className="text-2xl font-bold text-slate-900">Ativos</h1>
      <p className="mt-1 text-sm text-slate-500">
        Tabela geral de analise de todos os ativos disponiveis.
      </p>
      <TabelaAtivos resultados={resultados} erros={erros} />
    </main>
  );
}