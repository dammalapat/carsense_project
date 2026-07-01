import { ArrowLeft, RotateCcw } from 'lucide-react';

interface HeaderProps {
  phase: 'landing' | 'wizard' | 'results';
  onRestart: () => void;
  onBack: () => void;
}

export default function Header({ phase, onRestart, onBack }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 bg-surface-0/80 backdrop-blur-md border-b border-surface-200">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* Left: Back button or logo */}
        <div className="flex items-center gap-3">
          {phase !== 'landing' && (
            <button
              onClick={onBack}
              className="btn-ghost p-2 -ml-2"
              aria-label="Go back"
            >
              <ArrowLeft size={20} />
            </button>
          )}
          <button
            onClick={onRestart}
            className="flex items-center gap-2 group"
          >
            <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center">
              <span className="text-white font-display font-bold text-sm">CS</span>
            </div>
            <span className="font-display font-semibold text-lg text-surface-800 group-hover:text-brand-600 transition-colors">
              CarSense
            </span>
          </button>
        </div>

        {/* Right: Phase indicator + restart */}
        <div className="flex items-center gap-3">
          {phase !== 'landing' && (
            <span className="text-xs font-medium text-surface-500 uppercase tracking-wide hidden sm:block">
              {phase === 'wizard' ? 'Tell us about you' : 'Your matches'}
            </span>
          )}
          {phase === 'results' && (
            <button
              onClick={onRestart}
              className="btn-ghost text-sm"
              title="Start over"
            >
              <RotateCcw size={16} />
              <span className="hidden sm:inline">Start over</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
