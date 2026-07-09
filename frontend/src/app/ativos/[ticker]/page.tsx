import Link from "next/link";
import { obterAnaliseCompleta } from "@/lib/api";
import { GraficoPrecoVolume } from "@/components/GraficoPrecoVolume";
import { PainelIndicadores } from "@/components/PainelIndicadores";
import { PainelSinalFinal } from "@/components/PainelSinalFinal";
import { PainelFundamentos } from "@/components/PainelFundamentos";
import { CardMetrica } from "@/components/CardMetrica";

interface PageProps {
  params: Promise<{ ticker: string }>;
}

export default async function PaginaAtivo({ params }: PageProps) {
  const { ticker } = await params;
  const analise = await obterAnaliseCompleta(ticker);
  const { tecnico, estatisticas, fundamentos, scores, sinal } = analise;

  const corVariacao = tecnico.variacao_diaria_pct >= 0 ? "text-emerald-600" : "text-rose-600";
  const corTendencia =
    tecnico.tendencia === "alta"
      ? "text-emerald-600"
      : tecnico.tendencia === "baixa"
      ? "text-rose-600"
      : "text-slate-600";

  return (
    <main className="mx-auto max-w-6xl px-4 py-8">
      <Link href="/dashboard" className="text-xs text-slate-500 hover:underline">
        Voltar ao dashboard
      </Link>

      <div className="mt-2 flex items-baseline gap-3">
        <h1 className="text-2xl font-bold text-slate-900">{tecnico.ticker}</h1>
        <span className="text-sm text-slate-500">{fundamentos?.nome_empresa ?? ""}</span>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <CardMetrica titulo="Preco atual" valor={`R$ ${tecnico.preco_atual.toFixed(2)}`} />
        <CardMetrica titulo="Variacao diaria" valor={`${tecnico.variacao_diaria_pct.toFixed(2)}%`} corValor={corVariacao} />
        <CardMetrica titulo="Tendencia" valor={tecnico.tendencia} corValor={corTendencia} />
        <CardMetrica titulo="Volume" valor={tecnico.volume.toLocaleString("pt-BR")} />
      </div>

      <div className="mt-8">
        <PainelIndicadores tecnico={tecnico} />
      </div>
      <div className="mt-8">
        <GraficoPrecoVolume ticker={ticker} tecnico={tecnico} />
      </div>

      <div className="mt-8 grid gap-6 md:grid-cols-2">
        <PainelSinalFinal sinal={sinal} scores={scores} />
        <PainelFundamentos fundamentos={fundamentos} />
      </div>

      <div className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <CardMetrica titulo="Volatilidade anualizada" valor={`${estatisticas.volatilidade_anualizada_pct.toFixed(2)}%`} />
        <CardMetrica titulo="Retorno acumulado" valor={`${estatisticas.retorno_acumulado_pct.toFixed(2)}%`} />
        <CardMetrica titulo="Drawdown maximo" valor={`${estatisticas.drawdown_maximo_pct.toFixed(2)}%`} corValor="text-rose-600" />
        <CardMetrica titulo="Correlacao com Ibovespa" valor={estatisticas.correlacao_ibovespa.toFixed(2)} />
      </div>
    </main>
  );
}
