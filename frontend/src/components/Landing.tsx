import { ArrowRight, Shield, Fuel, Brain, GitCompareArrows } from 'lucide-react';

interface LandingProps {
  onStart: () => void;
}

export default function Landing({ onStart }: LandingProps) {
  return (
    <div className="flex flex-col">
      {/* ── Hero ──────────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden">
        {/* Subtle background pattern */}
        <div className="absolute inset-0 bg-gradient-to-br from-brand-50 via-surface-50 to-surface-100" />
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%234263eb' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }}
        />

        <div className="relative max-w-4xl mx-auto px-4 pt-20 pb-16 sm:pt-28 sm:pb-24 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-100 text-brand-700 text-sm font-medium mb-6 fade-in">
            <Brain size={14} />
            AI-powered car advisor
          </div>

          <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-bold text-surface-900 leading-tight mb-5 slide-up">
            Stop guessing.
            <br />
            <span className="text-gradient">Find the right car.</span>
          </h1>

          <p className="text-lg sm:text-xl text-surface-600 max-w-2xl mx-auto mb-10 fade-in" style={{ animationDelay: '0.15s' }}>
            Tell us about your life, not car specs. Our AI analyzes 
            30+ cars against your actual needs and explains <em>why</em> each 
            one fits — or doesn't.
          </p>

          <button
            onClick={onStart}
            className="btn-primary text-lg px-8 py-3.5 rounded-xl shadow-lg shadow-brand-600/20 hover:shadow-xl hover:shadow-brand-600/30 transition-all fade-in"
            style={{ animationDelay: '0.3s' }}
          >
            Find my car
            <ArrowRight size={20} />
          </button>

          <p className="mt-4 text-sm text-surface-500 fade-in" style={{ animationDelay: '0.4s' }}>
            Takes 2 minutes · No signup needed
          </p>
        </div>
      </section>

      {/* ── How it works ──────────────────────────────────────────────── */}
      <section className="max-w-5xl mx-auto px-4 py-16 sm:py-20">
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-center text-surface-800 mb-12">
          How CarSense works
        </h2>

        <div className="grid sm:grid-cols-3 gap-8">
          {[
            {
              step: '01',
              title: 'Tell us your life',
              desc: "Budget, daily routine, family size, what you care about. We ask about you, not engine displacement.",
              color: 'bg-brand-100 text-brand-700',
            },
            {
              step: '02',
              title: 'AI finds your matches',
              desc: "Our engine scores every car against your priorities and explains the reasoning — no black-box scores.",
              color: 'bg-emerald-100 text-emerald-700',
            },
            {
              step: '03',
              title: 'Compare with confidence',
              desc: "Side-by-side comparison with AI insights on what actually matters for your use case.",
              color: 'bg-amber-100 text-amber-700',
            },
          ].map((item) => (
            <div key={item.step} className="text-center sm:text-left">
              <div className={`inline-flex items-center justify-center w-10 h-10 rounded-lg ${item.color} font-display font-bold text-sm mb-4`}>
                {item.step}
              </div>
              <h3 className="font-display font-semibold text-lg text-surface-800 mb-2">
                {item.title}
              </h3>
              <p className="text-surface-600 text-sm leading-relaxed">
                {item.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Trust signals ─────────────────────────────────────────────── */}
      <section className="border-t border-surface-200 bg-surface-0">
        <div className="max-w-5xl mx-auto px-4 py-12 sm:py-16">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 text-center">
            {[
              { icon: <Shield size={24} />, value: '30+', label: 'Cars analyzed' },
              { icon: <Fuel size={24} />, value: '5', label: 'Fuel types' },
              { icon: <GitCompareArrows size={24} />, value: 'AI', label: 'Powered comparison' },
              { icon: <Brain size={24} />, value: '6', label: 'Scoring dimensions' },
            ].map((stat) => (
              <div key={stat.label}>
                <div className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-brand-50 text-brand-600 mb-2">
                  {stat.icon}
                </div>
                <div className="font-display font-bold text-2xl text-surface-800">{stat.value}</div>
                <div className="text-sm text-surface-500">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────────────────────── */}
      <footer className="border-t border-surface-200 bg-surface-50">
        <div className="max-w-5xl mx-auto px-4 py-6 flex items-center justify-between text-sm text-surface-500">
          <span>CarSense — Built for CarDekho AI Assignment</span>
          <span className="font-mono text-xs">v1.0.0</span>
        </div>
      </footer>
    </div>
  );
}
