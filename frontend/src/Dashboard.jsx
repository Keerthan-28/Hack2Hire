import React, { useState } from 'react';
import axios from 'axios';
import { Play, RotateCcw, Activity } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const samples = {
    strong: {
        candidate_id: "C_STRONG",
        role: "Senior Engineer",
        questions: [
            { question_id: 1, difficulty: "medium", time_taken: 45, max_time: 60, answer_quality: 0.95 },
            { question_id: 2, difficulty: "hard", time_taken: 80, max_time: 120, answer_quality: 0.9 },
            { question_id: 3, difficulty: "hard", time_taken: 90, max_time: 120, answer_quality: 1.0 },
            { question_id: 4, difficulty: "hard", time_taken: 50, max_time: 120, answer_quality: 0.9 },
        ]
    },
    borderline: {
        candidate_id: "C_BORDER",
        role: "Junior Dev",
        questions: [
            { question_id: 1, difficulty: "easy", time_taken: 50, max_time: 60, answer_quality: 0.6 },
            { question_id: 2, difficulty: "medium", time_taken: 70, max_time: 60, answer_quality: 0.5 },
            { question_id: 3, difficulty: "medium", time_taken: 55, max_time: 60, answer_quality: 0.7 },
        ]
    },
    termination: {
        candidate_id: "C_FAIL",
        role: "Intern",
        questions: [
            { question_id: 1, difficulty: "easy", time_taken: 20, max_time: 60, answer_quality: 0.2 },
            { question_id: 2, difficulty: "easy", time_taken: 20, max_time: 60, answer_quality: 0.1 },
            { question_id: 3, difficulty: "easy", time_taken: 20, max_time: 60, answer_quality: 0.1 },
            { question_id: 4, difficulty: "easy", time_taken: 20, max_time: 60, answer_quality: 0.5 },
        ]
    },
    adaptive: {
        candidate_id: "C_ADAPT",
        role: "System Architect",
        questions: [
            { question_id: 1, difficulty: "medium", time_taken: 40, max_time: 60, answer_quality: 0.9 }, // High score -> Harder
            { question_id: 2, difficulty: "hard", time_taken: 100, max_time: 120, answer_quality: 0.4 }, // Low score -> Easier
            { question_id: 3, difficulty: "medium", time_taken: 50, max_time: 60, answer_quality: 0.8 },
        ]
    }
};

export default function Dashboard() {
    const [jsonInput, setJsonInput] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleProcess = async () => {
        try {
            setLoading(true);
            setError(null);

            let data;
            try {
                data = JSON.parse(jsonInput);
            } catch (e) {
                throw new Error("Invalid JSON format");
            }

            // Call API
            const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const response = await axios.post(`${apiUrl}/api/process`, data);
            setResult(response.data);

        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    };

    const loadSample = (key) => {
        setJsonInput(JSON.stringify(samples[key], null, 2));
    };

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            <header className="flex items-center justify-between glass-panel p-4">
                <div className="flex items-center gap-2">
                    <div className="p-2 bg-indigo-600 rounded-lg">
                        <Activity className="w-6 h-6 text-white" />
                    </div>
                    <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-pink-400">
                        InterviewSim <span className="text-slate-500 font-light text-sm">v2.0</span>
                    </h1>
                </div>
                <div className="text-sm text-slate-400">
                    <span className="w-2 h-2 rounded-full bg-green-500 inline-block mr-2 animate-pulse"></span>
                    System Online
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Input Section */}
                <section className="lg:col-span-1 glass-panel p-6 flex flex-col h-[calc(100vh-140px)]">
                    <div className="mb-4">
                        <h2 className="text-lg font-semibold text-slate-200 mb-2">Load Scenario</h2>
                        <div className="grid grid-cols-2 gap-2">
                            <button onClick={() => loadSample('strong')} className="text-xs px-3 py-2 rounded bg-slate-800 hover:bg-green-900/30 text-slate-300 hover:text-green-400 transition border border-transparent hover:border-green-500/30">
                                🚀 Strong Hire
                            </button>
                            <button onClick={() => loadSample('borderline')} className="text-xs px-3 py-2 rounded bg-slate-800 hover:bg-yellow-900/30 text-slate-300 hover:text-yellow-400 transition border border-transparent hover:border-yellow-500/30">
                                ⚖️ Borderline
                            </button>
                            <button onClick={() => loadSample('termination')} className="text-xs px-3 py-2 rounded bg-slate-800 hover:bg-red-900/30 text-slate-300 hover:text-red-400 transition border border-transparent hover:border-red-500/30">
                                🛑 Termination
                            </button>
                            <button onClick={() => loadSample('adaptive')} className="text-xs px-3 py-2 rounded bg-slate-800 hover:bg-indigo-900/30 text-slate-300 hover:text-indigo-400 transition border border-transparent hover:border-indigo-500/30">
                                📈 Adaptive
                            </button>
                        </div>
                    </div>

                    <textarea
                        value={jsonInput}
                        onChange={(e) => setJsonInput(e.target.value)}
                        className="flex-1 w-full bg-slate-950/50 border border-slate-700 rounded-lg p-4 font-mono text-xs text-slate-300 focus:ring-2 focus:ring-indigo-500 outline-none resize-none"
                        placeholder="// Paste interview JSON here..."
                    />

                    <button
                        onClick={handleProcess}
                        disabled={loading || !jsonInput}
                        className="mt-4 w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-semibold text-white flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-500/20"
                    >
                        {loading ? (
                            <span className="animate-spin">⟳</span>
                        ) : (
                            <Play className="w-4 h-4" />
                        )}
                        {loading ? 'Processing...' : 'Run Simulation'}
                    </button>

                    {error && (
                        <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded text-red-400 text-sm">
                            ⚠ {error}
                        </div>
                    )}
                </section>

                {/* Results Section */}
                <section className="lg:col-span-2 space-y-6">
                    {!result ? (
                        <div className="h-full glass-panel flex flex-col items-center justify-center text-slate-500 p-12">
                            <Activity className="w-16 h-16 mb-4 opacity-20" />
                            <p>Run a simulation to view analysis</p>
                        </div>
                    ) : (
                        <>
                            {/* Score Cards */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div className="glass-panel p-6 relative overflow-hidden group">
                                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition">
                                        <Activity className="w-24 h-24 text-indigo-500" />
                                    </div>
                                    <h3 className="text-slate-400 text-sm uppercase tracking-wider">Readiness Score</h3>
                                    <div className="mt-2 flex items-baseline gap-2">
                                        <span className="text-5xl font-bold text-white">{result.final_score}</span>
                                        <span className="text-slate-500">/100</span>
                                    </div>
                                    <div className={`mt-4 inline-block px-3 py-1 rounded-full text-xs font-bold
                    ${result.final_score >= 85 ? 'bg-green-500/20 text-green-400' :
                                            result.final_score >= 70 ? 'bg-blue-500/20 text-blue-400' :
                                                result.final_score >= 50 ? 'bg-yellow-500/20 text-yellow-400' : 'bg-red-500/20 text-red-400'}
                  `}>
                                        {result.recommendation.toUpperCase()}
                                    </div>
                                </div>

                                <div className="glass-panel p-6">
                                    <h3 className="text-slate-400 text-sm uppercase tracking-wider mb-4">Performance Metrics</h3>
                                    <div className="space-y-3">
                                        <MetricBar label="Accuracy" value={result.metrics.accuracy} color="bg-indigo-500" />
                                        <MetricBar label="Time Efficiency" value={result.metrics.time_efficiency} color="bg-pink-500" />
                                        <MetricBar label="Consistency" value={result.metrics.consistency} color="bg-cyan-500" />
                                    </div>
                                </div>

                                <div className="glass-panel p-6 flex flex-col justify-center">
                                    <h3 className="text-slate-400 text-sm uppercase tracking-wider mb-2">Status</h3>
                                    <div className="text-xl font-semibold text-white mb-2">{result.status}</div>
                                    {result.termination_reason && (
                                        <div className="text-red-400 text-sm bg-red-500/10 p-2 rounded border border-red-500/20">
                                            Reason: {result.termination_reason}
                                        </div>
                                    )}
                                    <div className="mt-4 text-xs text-slate-500">
                                        Interview ID: {result.interview_id}
                                    </div>
                                </div>
                            </div>

                            {/* Detailed Breakdown */}
                            <div className="glass-panel p-6">
                                <h3 className="text-lg font-semibold text-slate-200 mb-4">Detailed Question Analysis</h3>
                                <div className="overflow-x-auto">
                                    <table className="w-full text-left text-sm text-slate-400">
                                        <thead className="bg-slate-950/30 text-xs uppercase">
                                            <tr>
                                                <th className="p-3 rounded-l-lg">ID</th>
                                                <th className="p-3">Difficulty</th>
                                                <th className="p-3">Time</th>
                                                <th className="p-3">Score %</th>
                                                <th className="p-3 text-right rounded-r-lg">Status</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-slate-800">
                                            {result.questions.map((q, i) => (
                                                <tr key={i} className="hover:bg-slate-800/50 transition">
                                                    <td className="p-3 font-mono text-white">{q.question_id}</td>
                                                    <td className="p-3">
                                                        <span className={`px-2 py-0.5 rounded text-xs
                              ${q.difficulty === 'hard' ? 'bg-red-500/10 text-red-400' :
                                                                q.difficulty === 'medium' ? 'bg-yellow-500/10 text-yellow-400' : 'bg-green-500/10 text-green-400'}
                            `}>
                                                            {q.difficulty}
                                                        </span>
                                                    </td>
                                                    <td className="p-3">
                                                        <span className={q.time_taken > q.time_limit ? 'text-red-400' : 'text-green-400'}>
                                                            {q.time_taken}s
                                                        </span>
                                                        <span className="text-slate-600 text-xs ml-1">/ {q.time_limit}s</span>
                                                    </td>
                                                    <td className="p-3">
                                                        <div className="flex items-center gap-2">
                                                            <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                                                <div
                                                                    className="h-full bg-indigo-500 rounded-full"
                                                                    style={{ width: `${q.score_percentage}%` }}
                                                                ></div>
                                                            </div>
                                                            <span className="text-white">{q.score_percentage}%</span>
                                                        </div>
                                                    </td>
                                                    <td className="p-3 text-right">
                                                        {q.status === 'Passed' ? (
                                                            <span className="text-green-400">✔ Pass</span>
                                                        ) : (
                                                            <span className="text-red-400">✖ Fail</span>
                                                        )}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </>
                    )}
                </section>
            </div>
        </div>
    );
}

const MetricBar = ({ label, value, color }) => (
    <div>
        <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-400">{label}</span>
            <span className="text-white font-bold">{value}%</span>
        </div>
        <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
            <div
                className={`h-full ${color} transition-all duration-1000`}
                style={{ width: `${value}%` }}
            ></div>
        </div>
    </div>
);
