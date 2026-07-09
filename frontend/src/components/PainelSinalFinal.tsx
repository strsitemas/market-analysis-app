import type { SinalFinal, Scores } from "@/types/analise";

interface Props {
  sinal: SinalFinal;
  scores: Scores;
}

const CONFIG_SINAL: Record<SinalFinal["sinal"], { label: string; classe: string }> = {
  compra: { label: "COMPRA", classe: "bg-emerald-100 text-emerald-700 border-emerald-300" },
  venda: { label: "VENDA", classe: "bg-rose-100 text-rose-700 border-rose-300" },
  atencao: { label: "ATENCAO", classe: "bg-amber-100 text-amber-700 border-amber-300" },
  neutro: { label: "NEUTRO", classe: "bg-slate-100 text-slate-700 border-slate-300" },
};

export function PainelSinalFinal({ sinal, scores }: Props) {
  const cfg = CONFIG_SINAL[sinal.sinal];

  return (
    <div className="rounded-lg border border-slate-200 p-5">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-700">Sinal final</h3>
        <span className={`rounded-full border px-3 py-1 text-xs font-bold ${cfg.classe}`}>
          {cfg.label}
        </span>
      </div>
      <p className="mt-3 text-sm text-slate-600">{sinal.justificativa}</p>
      <div className="mt-4 grid grid-cols-2 gap-3">
        <div>
          <p className="text-xs text-slate-500">Score de risco</p>
          <p className="text-lg font-bold text-rose-600">{scores.score_risco.toFixed(0)}/100</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Score de oportunidade</p>
          <p className="text-lg font-bold text-emerald-600">{scores.score_oportunidade.toFixed(0)}/100</p>
        </div>
      </div>
      <p className="mt-3 text-[11px] text-slate-400">
        Este sinal e uma leitura probabilistica baseada nos indicadores calculados e nao
        constitui garantia de resultado futuro nem recomendacao de investimento.
      </p>
    </div>
  );
}