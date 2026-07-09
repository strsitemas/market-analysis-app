import Link from "next/link";
import { listarAtivosDisponiveis } from "@/lib/api";

export default async function HomePage() {
  const ativos = await listarAtivosDisponiveis();

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <h1 className="text-2xl font-bold text-slate-900">
        Análise de Bolsa
      </h1>
      <p className="mt-2 text-sm text-slate-500">
        Ferramenta de apoio à decisão com indicadores técnicos, estatísticos
        e fundamentalistas. Não constitui recomendação de investimento.
      </p>

      <div className="mt-8 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-800">
          Ativos disponíveis
        </h2>
        <Link
          href="/analise"
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
        >
          Ver tabela comparativa
        </Link>
      </div>

      <ul className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
        {ativos.map((ativo) => (
          <li
            key={ativo.ticker}
            className="rounded-lg border border-slate-200 p-4 hover:border-slate-400"
          >
            <p className="font-semibold text-slate-900">{ativo.ticker}</p>
            <p className="text-sm text-slate-500">
              {ativo.nome} · {ativo.setor}
            </p>
          </li>
        ))}
      </ul>
    </main>
  );
}