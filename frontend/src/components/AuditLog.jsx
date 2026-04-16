import { useState, useEffect } from 'react';
import { Download } from 'lucide-react';
import { api } from '../api/client';

const AuditLog = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    try {
      const data = await api.audit.list({ limit: 50 });
      setLogs(data.audit_log || []);
    } catch (error) {
      console.error('Failed to load audit log:', error);
    } finally {
      setLoading(false);
    }
  };

  const getAgentColor = (agentName) => {
    const colors = {
      intake: 'bg-indigo-500/20 text-indigo-400',
      planning: 'bg-blue-500/20 text-blue-400',
      staffing: 'bg-violet-500/20 text-violet-400',
      risk: 'bg-orange-500/20 text-orange-400',
      execution_coordinator: 'bg-teal-500/20 text-teal-400',
    };
    return colors[agentName] || 'bg-primary/20 text-primary';
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-lg font-semibold text-text-primary">Audit Log</h1>
        <button className="flex items-center gap-2 px-4 py-2 border border-border text-text-primary hover:bg-surface rounded-sm text-sm font-semibold transition-colors">
          <Download size={16} />
          Export CSV
        </button>
      </div>

      <div className="space-y-4">
        {logs.map((log, index) => (
          <div key={log.id} className="bg-surface rounded-md p-4 border border-border">
            <div className="flex items-start gap-4">
              <div className="flex flex-col items-center">
                <div className="w-3 h-3 rounded-full bg-primary"></div>
                {index < logs.length - 1 && (
                  <div className="w-0.5 h-full bg-border mt-2"></div>
                )}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getAgentColor(log.agent_name)}`}>
                    {log.agent_name}
                  </span>
                  <span className="text-sm font-medium text-text-primary">{log.action}</span>
                  {log.confidence_score && (
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      log.confidence_score > 0.85 ? 'bg-success/20 text-success' :
                      log.confidence_score > 0.65 ? 'bg-warning/20 text-warning' :
                      'bg-danger/20 text-danger'
                    }`}>
                      {log.confidence_score.toFixed(2)}
                    </span>
                  )}
                  <span className="text-xs text-text-secondary ml-auto">
                    {new Date(log.created_at).toLocaleString()}
                  </span>
                </div>
                <div className="text-xs text-text-secondary">
                  {log.entity_type && `${log.entity_type}: ${log.entity_id}`}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AuditLog;
