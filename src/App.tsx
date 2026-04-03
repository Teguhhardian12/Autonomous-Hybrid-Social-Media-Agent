import React from 'react';
import { 
  Terminal, 
  Cpu, 
  MessageSquare, 
  ShieldCheck, 
  Chrome, 
  Bot,
  ExternalLink,
  Copy,
  CheckCircle2
} from 'lucide-react';

export default function App() {
  const [copied, setCopied] = React.useState<string | null>(null);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-zinc-300 font-sans selection:bg-blue-500/30">
      {/* Header */}
      <header className="border-b border-zinc-800/50 bg-black/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600/10 rounded-lg">
              <Bot className="w-6 h-6 text-blue-500" />
            </div>
            <h1 className="text-xl font-semibold text-white tracking-tight">X-Agent <span className="text-zinc-500 font-normal">Command Center</span></h1>
          </div>
          <div className="flex items-center gap-2 px-3 py-1 bg-green-500/10 border border-green-500/20 rounded-full">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-xs font-medium text-green-500 uppercase tracking-wider">Ready for Local Deploy</span>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="mb-16">
          <h2 className="text-4xl font-bold text-white mb-4 tracking-tight">Autonomous Hybrid Social Media Agent</h2>
          <p className="text-lg text-zinc-400 max-w-2xl leading-relaxed">
            Your foundational Python architecture is ready. This agent combines Playwright automation, 
            Ollama local AI, and Telegram remote control into a single local Windows workflow.
          </p>
        </div>

        {/* Setup Steps */}
        <div className="grid gap-8">
          
          {/* Step 1: Chrome CDP */}
          <section className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-8">
            <div className="flex items-start gap-4 mb-6">
              <div className="p-3 bg-orange-500/10 rounded-xl">
                <Chrome className="w-6 h-6 text-orange-500" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-white">1. Launch Chrome with CDP</h3>
                <p className="text-zinc-400 mt-1">Playwright needs to connect to your existing session to bypass login & detection.</p>
              </div>
            </div>
            <div className="bg-black rounded-xl p-4 font-mono text-sm relative group">
              <code className="text-orange-400">
                chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome_dev"
              </code>
              <button 
                onClick={() => copyToClipboard('chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\\temp\\chrome_dev"', 'cdp')}
                className="absolute right-4 top-4 p-2 bg-zinc-800 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity"
              >
                {copied === 'cdp' ? <CheckCircle2 className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>
          </section>

          {/* Step 2: Telegram Bot */}
          <section className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-8">
            <div className="flex items-start gap-4 mb-6">
              <div className="p-3 bg-blue-500/10 rounded-xl">
                <MessageSquare className="w-6 h-6 text-blue-500" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-white">2. Configure Telegram Bot</h3>
                <p className="text-zinc-400 mt-1">Create your remote control interface via @BotFather.</p>
              </div>
            </div>
            <ul className="space-y-4 text-zinc-400">
              <li className="flex items-center gap-3">
                <span className="w-6 h-6 rounded-full bg-zinc-800 flex items-center justify-center text-xs font-bold">1</span>
                Message <a href="https://t.me/botfather" target="_blank" className="text-blue-400 hover:underline inline-flex items-center gap-1">@BotFather <ExternalLink className="w-3 h-3" /></a> and send <code className="text-zinc-200">/newbot</code>
              </li>
              <li className="flex items-center gap-3">
                <span className="w-6 h-6 rounded-full bg-zinc-800 flex items-center justify-center text-xs font-bold">2</span>
                Copy the API Token and paste it into <code className="text-zinc-200">agent.py</code>
              </li>
            </ul>
          </section>

          {/* Step 3: Ollama */}
          <section className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-8">
            <div className="flex items-start gap-4 mb-6">
              <div className="p-3 bg-purple-500/10 rounded-xl">
                <Cpu className="w-6 h-6 text-purple-500" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-white">3. Run Local AI (Ollama)</h3>
                <p className="text-zinc-400 mt-1">Ensure your local model is downloaded and ready.</p>
              </div>
            </div>
            <div className="bg-black rounded-xl p-4 font-mono text-sm relative group">
              <code className="text-purple-400">
                ollama run qwen2.5:1.5b
              </code>
              <button 
                onClick={() => copyToClipboard('ollama run qwen2.5:1.5b', 'ollama')}
                className="absolute right-4 top-4 p-2 bg-zinc-800 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity"
              >
                {copied === 'ollama' ? <CheckCircle2 className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>
          </section>

          {/* Step 4: Run Agent */}
          <section className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-8">
            <div className="flex items-start gap-4 mb-6">
              <div className="p-3 bg-green-500/10 rounded-xl">
                <Terminal className="w-6 h-6 text-green-500" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-white">4. Initialize & Run</h3>
                <p className="text-zinc-400 mt-1">Install dependencies and start the command center.</p>
              </div>
            </div>
            <div className="space-y-3">
              <div className="bg-black rounded-xl p-4 font-mono text-sm text-zinc-500">
                # Install dependencies<br />
                <span className="text-green-400">pip install -r requirements.txt</span><br /><br />
                # Start the agent<br />
                <span className="text-green-400">python agent.py</span>
              </div>
            </div>
          </section>

        </div>

        {/* Security Note */}
        <div className="mt-12 p-6 bg-zinc-900/30 border border-zinc-800/50 rounded-2xl flex items-start gap-4">
          <ShieldCheck className="w-6 h-6 text-zinc-500 shrink-0" />
          <p className="text-sm text-zinc-500 leading-relaxed">
            <strong className="text-zinc-300">Humanization Note:</strong> The agent uses visual locators (get_by_role, get_by_test_id) 
            and random delays to mimic human behavior. Always ensure your Chrome session is logged into X before starting the agent.
          </p>
        </div>
      </main>
    </div>
  );
}
