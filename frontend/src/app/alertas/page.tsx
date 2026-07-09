import { PainelAlertas } from "@/components/PainelAlertas";
import Link from "next/link";

export default function AlertasPage() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-800">Alertas</h1>
        <Link href="/analise" className="text-sm text-sky-600 hover:underline">
          Voltar para analise
        </Link>
      </div>
      <PainelAlertas />
    </main>
  );
}