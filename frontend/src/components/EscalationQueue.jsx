import { useState, useEffect } from 'react';
import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { api } from '../api/client';

const EscalationQueue = () => {
  const [escalations, setEscalations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEscalations();
  }, []);

  const loadEscalations = async () => {
    try {
      const data = await api.escalations.list('pending');
      setEscalations(data.escalations || []);
    } catch (error) {
      console.error('Failed to load escalations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDecision = async (id, decision) => {
    try {
      await api.escalations.approve(id, {
        decision,
        reviewed_by: 'pm-user-id', // Would come from auth context
      });
      loadEscalations();
    } catch (error) {
      console.error('Failed to process escalation:', error);
    }
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-lg font-semibold text-text-primary">Escalation Queue</h1>
        <span className="px-3 py-1 bg-danger/20 text-danger rounded-full text-sm font-medium">
          {escalations.length} Pending
        </span>
      </div>

      {escalations.length === 0 ? (
        <div className="text-center py-16">
          <CheckCircle size={48} className="mx-auto text-success mb-4" />
          <h3 className="text-md font-semibold text-text-primary mb-2">All caught up!</h3>
          <p className="text-sm text-text-secondary">No pending escalations at the moment.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {escalations.map((escalation) => (
            <div
              key={escalation.id}
              className="bg-surface rounded-md border-l-4 border-danger p-6"
            >
              <div className="flex items-start gap-4">
                <AlertTriangle size={24} className="text-danger mt-1" />
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <span className="px-2 py-1 bg-primary/20 text-primary rounded-full text-xs font-medium">
                      {escalation.agent_name}
                    </span>
                    <span className="text-sm font-semibold text-text-primary">
                      {escalation.project_name}
                    </span>
                    <span className="px-2 py-1 bg-danger/20 text-danger rounded-full text-xs font-medium">
                      Confidence: {escalation.confidence_score?.toFixed(2)}
                    </span>
                    <span className="text-xs text-text-secondary ml-auto">
                      {new Date(escalation.created_at).toLocaleString()}
                    </span>
                  </div>

                  <p className="text-sm text-text-secondary mb-4">{escalation.reason}</p>

                  {escalation.suggested_action && (
                    <div className="bg-surface-raised p-4 rounded-md mb-4">
                      <p className="text-xs text-text-secondary mb-2">Suggested Action:</p>
                      <pre className="text-xs text-text-primary whitespace-pre-wrap">
                        {JSON.stringify(escalation.suggested_action, null, 2)}
                      </pre>
                    </div>
                  )}

                  <div className="flex gap-3">
                    <button
                      onClick={() => handleDecision(escalation.id, 'approved')}
                      className="flex items-center gap-2 px-4 py-2 bg-success hover:bg-success/90 text-white rounded-sm text-sm font-semibold transition-colors"
                    >
                      <CheckCircle size={16} />
                      Approve
                    </button>
                    <button
                      onClick={() => handleDecision(escalation.id, 'rejected')}
                      className="flex items-center gap-2 px-4 py-2 border border-danger text-danger hover:bg-danger/10 rounded-sm text-sm font-semibold transition-colors"
                    >
                      <XCircle size={16} />
                      Reject
                    </button>
                    <button
                      onClick={() => handleDecision(escalation.id, 'overridden')}
                      className="px-4 py-2 border border-primary text-primary hover:bg-primary/10 rounded-sm text-sm font-semibold transition-colors"
                    >
                      Override
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default EscalationQueue;
