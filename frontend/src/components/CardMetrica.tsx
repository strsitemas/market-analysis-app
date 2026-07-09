interface Props {
  titulo: string;
  valor: string;
  subtitulo?: string;
  corValor?: string;
}

export function CardMetrica({ titulo, valor, subtitulo, corValor = "text-slate-800" }: Props) {
  return (
    <div className="rounded-lg border border-slate-200 p-4">
      <p className="text-xs text-slate-500">{titulo}</p>
      <p className={`mt-1 text-2xl font-bold ${corValor}`}>{valor}</p>
      {subtitulo && <p className="text-xs text-slate-400">{subtitulo}</p>}
    </div>
  );
}