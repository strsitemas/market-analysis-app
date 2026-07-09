"use client";

import { useEffect, useState } from "react";
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import { obterHistoricoSalvo } from "@/lib/api";
import type { HistoricoPonto, TabelaTecnica } from "@/types/analise";

interface Props {
  ticker: string;
  tecnico: TabelaTecnica;
}

/**
 * Grafico combinado de preco de fechamento (linha) + volume (barras),
 * com linhas de referencia horizontais para suporte, resistencia e
 * bandas de Bollinger ATUAIS (nao ha serie historica desses indicadores
 * no backend hoje -- apenas o valor mais recente).
 */
export function GraficoPrecoVolume({ ticker, tecnico }: Props) {
  const [pontos, setPontos] = useState<HistoricoPonto[]>([]);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    setCarregando(true);
    obterHistoricoSalvo(ticker)
      .then(setPontos)
      .finally(() => setCarregando(false));
  }, [ticker]);

  if (carregando) {
    return <p className="text-sm text-slate-500">Carregando histórico...</p>;
  }

  const dadosGrafico = pontos.map((p) => ({
    data: p.data,
    fechamento: p.fechamento,
    volume: p.volume,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-700">
          Preço de fechamento ({pontos.length} pregões)
        </h3>
        <ResponsiveContainer width="100%" height={280}>
          <ComposedChart data={dadosGrafico}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis
              dataKey="data"
              tick={{ fontSize: 10 }}
              interval="preserveStartEnd"
              minTickGap={40}
            />
            <YAxis
              domain={["auto", "auto"]}
              tick={{ fontSize: 11 }}
              tickFormatter={(v) => `R$ ${v.toFixed(0)}`}
            />
            <Tooltip
              formatter={(value: number) => [`R$ ${value.toFixed(2)}`, "Fechamento"]}
            />
            <Line
              type="monotone"
              dataKey="fechamento"
              stroke="#0f172a"
              strokeWidth={2}
              dot={false}
            />
            <ReferenceLine
              y={tecnico.suporte}
              stroke="#10b981"
              strokeDasharray="4 4"
              label={{ value: "Suporte", position: "insideBottomLeft", fontSize: 10, fill: "#10b981" }}
            />
            <ReferenceLine
              y={tecnico.resistencia}
              stroke="#ef4444"
              strokeDasharray="4 4"
              label={{ value: "Resistência", position: "insideTopLeft", fontSize: 10, fill: "#ef4444" }}
            />
            <ReferenceLine
              y={tecnico.bollinger.banda_superior}
              stroke="#94a3b8"
              strokeDasharray="2 2"
              label={{ value: "Bollinger sup.", position: "insideTopRight", fontSize: 9, fill: "#94a3b8" }}
            />
            <ReferenceLine
              y={tecnico.bollinger.banda_inferior}
              stroke="#94a3b8"
              strokeDasharray="2 2"
              label={{ value: "Bollinger inf.", position: "insideBottomRight", fontSize: 9, fill: "#94a3b8" }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-700">Volume</h3>
        <ResponsiveContainer width="100%" height={120}>
          <ComposedChart data={dadosGrafico}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis
              dataKey="data"
              tick={{ fontSize: 10 }}
              interval="preserveStartEnd"
              minTickGap={40}
            />
            <YAxis
              tick={{ fontSize: 11 }}
              tickFormatter={(v) => `${(v / 1_000_000).toFixed(0)}M`}
            />
            <Tooltip
              formatter={(value: number) => [value.toLocaleString("pt-BR"), "Volume"]}
            />
            <Bar dataKey="volume" fill="#94a3b8" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}