/**
 * ChatPanel.tsx — Conversational AI advisor panel.
 *
 * Slides in from the right. Maintains chat history and passes
 * the buyer's needs context so Claude can give personalized answers.
 *
 * Example questions the buyer might ask:
 * - "Is the Creta worth the extra money over the Seltos?"
 * - "Which car has the best resale value?"
 * - "I'm worried about safety for my kids — what should I look for?"
 */

import { useState, useRef, useEffect } from 'react';
import { X, Send, Loader2, MessageCircle } from 'lucide-react';
import type { UserNeeds, ChatMessage } from '../types';
import { chatWithAdvisor } from '../api';

interface ChatPanelProps {
  userNeeds: UserNeeds | null;
  shortlistedCarIds: number[];
  onClose: () => void;
}

const SUGGESTED_QUESTIONS = [
  "Which of my matches has the best resale value?",
  "Is diesel still worth it in 2024?",
  "What should I check during a test drive?",
  "Are EVs practical for highway trips?",
];

export default function ChatPanel({ userNeeds, shortlistedCarIds, onClose }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    setTimeout(() => inputRef.current?.focus(), 300);
  }, []);

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return;

    const userMsg: ChatMessage = { role: 'user', content: text.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await chatWithAdvisor(
        text.trim(),
        messages,
        userNeeds ?? undefined,
        shortlistedCarIds,
      );
      setMessages((prev) => [...prev, { role: 'assistant', content: response.reply }]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I couldn\'t process that. Please try again.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-surface-900/30 backdrop-blur-sm" onClick={onClose} />

      {/* Panel */}
      <div className="relative w-full sm:max-w-md bg-surface-0 shadow-2xl flex flex-col fade-in">
        {/* Header */}
        <div className="shrink-0 border-b border-surface-200 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-brand-100 flex items-center justify-center">
              <MessageCircle size={16} className="text-brand-600" />
            </div>
            <div>
              <h3 className="font-display font-semibold text-sm text-surface-800">CarSense Advisor</h3>
              <p className="text-xs text-surface-500">Ask anything about your matches</p>
            </div>
          </div>
          <button onClick={onClose} className="btn-ghost p-2 -mr-2" aria-label="Close">
            <X size={18} />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
          {/* Welcome message */}
          {messages.length === 0 && (
            <div className="fade-in">
              <div className="bg-brand-50 rounded-xl rounded-tl-sm p-4 mb-4">
                <p className="text-sm text-brand-900">
                  Hey! I'm your CarSense advisor. I know your preferences and shortlisted cars.
                  Ask me anything — comparisons, ownership costs, test drive tips, whatever helps
                  you decide.
                </p>
              </div>

              {/* Suggested questions */}
              <div className="space-y-2">
                <p className="text-xs text-surface-500 font-medium">Try asking:</p>
                {SUGGESTED_QUESTIONS.map((q) => (
                  <button
                    key={q}
                    onClick={() => sendMessage(q)}
                    className="block w-full text-left px-3 py-2 rounded-lg border border-surface-200 text-sm text-surface-700 hover:bg-surface-50 hover:border-brand-200 transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Chat messages */}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] rounded-xl px-4 py-3 text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-brand-600 text-white rounded-br-sm'
                    : 'bg-surface-100 text-surface-800 rounded-bl-sm'
                }`}
              >
                {msg.content.split('\n').map((line, j) => (
                  <p key={j} className={j > 0 ? 'mt-2' : ''}>{line}</p>
                ))}
              </div>
            </div>
          ))}

          {/* Loading indicator */}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-surface-100 rounded-xl rounded-bl-sm px-4 py-3">
                <Loader2 size={18} className="text-brand-500 animate-spin" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form
          onSubmit={handleSubmit}
          className="shrink-0 border-t border-surface-200 px-4 py-3"
        >
          <div className="flex items-center gap-2">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your car matches..."
              className="input-field flex-1 text-sm"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="btn-primary p-2.5 rounded-lg disabled:opacity-50"
            >
              <Send size={18} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
