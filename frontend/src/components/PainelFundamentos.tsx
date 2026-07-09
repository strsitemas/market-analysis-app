import type { Fundamentos } from "@/types/analise";

interface Props {
  fundamentos: Fundamentos | null;
}

function fmt(v: number | null, sufixo = "") {
  return v === null || v === undefined ? "N/D" : `${v.toFixed(2)}${sufixo}`;
}

export function PainelFundamentos({ fundamentos }: Props) {
  if (!fundamentos) {
    return (
      <div className="rounded-lg border border-slate-200 p-5">
        <h3 className="mb-2 text-sm font-semibold text-slate-700">Fundamentos</h3>
        <p className="text-sm text-slate-400">Dados fundamentalistas indisponiveis para este ativo.</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-slate-200 p-5">
      <h3 className="mb-3 text-sm font-semibold text-slate-700">
        Fundamentos - {fundamentos.nome_empresa}
      </h3>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        <div>
          <p className="text-xs text-slate-500">P/L</p>
          <p className="text-base font-semibold text-slate-800">{fmt(fundamentos.pl)}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">P/VP</p>
          <p className="text-base font-semibold text-slate-800">{fmt(fundamentos.pvp)}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">ROE</p>
          <p className="text-base font-semibold text-slate-800">{fmt(fundamentos.roe_pct, "%")}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Margem liquida</p>
          <p className="text-base font-semibold text-slate-800">{fmt(fundamentos.margem_liquida_pct, "%")}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Divida/Patrimonio</p>
          <p className="text-base font-semibold text-slate-800">{fmt(fundamentos.divida_patrimonio)}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Dividend Yield</p>
          <p className="text-base font-semibold text-slate-800">{fmt(fundamentos.dividend_yield_pct, "%")}</p>
        </div>
      </div>
    </div>
  );
}