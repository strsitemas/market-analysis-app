"use client";

import type { TabelaTecnica } from "@/types/analise";

interface Props {
  tecnico: TabelaTecnica;
}

/**
 * Painel com os indicadores tecnicos do momento atual (RSI, MACD,
 * medias moveis). Nao e uma serie historica -- e a "foto" mais
 * recente calculada pelo backend.
 */
export function PainelIndicadores({ tecnico }: Props) {
  const rsi = tecnico.rsi_14;
  const corRsi =
    rsi >= 70 ? "text-rose-600" : rsi <= 30 ? "text-emerald-600" : "text-slate-700";
  const statusRsi = rsi >= 70 ? "Sobrecomprado" : rsi <= 30 ? "Sobrevendido" : "Neutro";

  const histogramaPositivo = tecnico.macd.histograma > 0;

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
      <div className="rounded-lg border border-slate-200 p-4">
        <p className="text-xs text-slate-500">RSI (14)</p>
        <p className={`mt-1 text-2xl font-bold ${corRsi}`}>{rsi.toFixed(1)}</p>
        <p className="text-xs text-slate-400">{statusRsi}</p>
      </div>

      <div className="rounded-lg border border-slate-200 p-4">
        <p className="text-xs text-slate-500">MACD Histograma</p>
        <p
          className={`mt-1 text-2xl font-bold ${
            histogramaPositivo ? "text-emerald-600" : "text-rose-600"
          }`}
        >
          {tecnico.macd.histograma.toFixed(3)}
        </p>
        <p className="text-xs text-slate-400">
          {histogramaPositivo ? "Momentum de alta" : "Momentum de baixa"}
        </p>
      </div>

      <div className="rounded-lg border border-slate-200 p-4">
        <p className="text-xs text-slate-500">SMA 20 / SMA 50</p>
        <p className="mt-1 text-lg font-semibold text-slate-800">
          {tecnico.medias_moveis.sma_20.toFixed(2)} /{" "}
          {tecnico.medias_moveis.sma_50.toFixed(2)}
        </p>
        <p className="text-xs text-slate-400">Médias móveis simples</p>
      </div>

      <div className="rounded-lg border border-slate-200 p-4">
        <p className="text-xs text-slate-500">Bollinger (média)</p>
        <p className="mt-1 text-lg font-semibold text-slate-800">
          R$ {tecnico.bollinger.banda_media.toFixed(2)}
        </p>
        <p className="text-xs text-slate-400">
          {tecnico.bollinger.banda_inferior.toFixed(2)} —{" "}
          {tecnico.bollinger.banda_superior.toFixed(2)}
        </p>
      </div>
    </div>
  );
}