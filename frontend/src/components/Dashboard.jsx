import { useState, useEffect } from 'react';
import { Plus, AlertTriangle } from 'lucide-react';
import { api } from '../api/client';
import ProjectCard from './ProjectCard';
import NewProjectModal from './NewProjectModal';

const Dashboard = () => {
  const [projects, setProjects] = useState([]);
  const [escalations, setEscalations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNewProject, setShowNewProject] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [projectsData, escalationsData] = await Promise.all([
        api.projects.list(),
        api.escalations.list('pending')
      ]);
      setProjects(projectsData.projects || []);
      setEscalations(escalationsData.escalations || []);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const stats = {
    activeProjects: projects.filter(p => p.status === 'active').length,
    escalationsPending: escalations.length,
    avgConfidence: projects.length > 0
      ? (projects.reduce((sum, p) => sum + (p.confidence_score || 0), 0) / projects.length).toFixed(2)
      : 0,
    tasksOverdue: 0, // Would need task data
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8">
      {/* KPI Strip */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        <div className="bg-surface p-6 rounded-md border border-border">
          <div className="text-xl font-bold text-text-primary">{stats.activeProjects}</div>
          <div className="text-sm text-text-secondary mt-1">Active Projects</div>
        </div>
        <div className="bg-surface p-6 rounded-md border border-border">
          <div className={`text-xl font-bold ${stats.escalationsPending > 0 ? 'text-danger' : 'text-text-primary'}`}>
            {stats.escalationsPending}
          </div>
          <div className="text-sm text-text-secondary mt-1">Escalations Pending</div>
        </div>
        <div className="bg-surface p-6 rounded-md border border-border">
          <div className={`text-xl font-bold ${
            stats.avgConfidence > 0.85 ? 'text-success' : 
            stats.avgConfidence > 0.65 ? 'text-warning' : 'text-danger'
          }`}>
            {stats.avgConfidence}
          </div>
          <div className="text-sm text-text-secondary mt-1">Avg Confidence</div>
        </div>
        <div className="bg-surface p-6 rounded-md border border-border">
          <div className="text-xl font-bold text-text-primary">{stats.tasksOverdue}</div>
          <div className="text-sm text-text-secondary mt-1">Tasks Overdue</div>
        </div>
      </div>

      {/* Active Projects */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-md font-semibold text-text-primary">Active Projects</h2>
          <button
            onClick={() => setShowNewProject(true)}
            className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded-sm font-semibold transition-colors"
          >
            <Plus size={18} />
            New Project
          </button>
        </div>

        <div className="grid grid-cols-3 gap-6">
          {projects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>

        {projects.length === 0 && (
          <div className="text-center py-12 text-text-secondary">
            No projects yet. Create your first project to get started.
          </div>
        )}
      </div>

      {/* Needs Attention */}
      {escalations.length > 0 && (
        <div>
          <h2 className="text-md font-semibold text-text-primary mb-6">Needs Your Attention</h2>
          <div className="space-y-4">
            {escalations.slice(0, 3).map((escalation) => (
              <div
                key={escalation.id}
                className="bg-surface p-4 rounded-md border-l-4 border-danger"
              >
                <div className="flex items-start gap-3">
                  <AlertTriangle size={20} className="text-danger mt-1" />
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-sm font-medium text-text-primary">
                        {escalation.project_name}
                      </span>
                      <span className="text-xs px-2 py-1 bg-danger/20 text-danger rounded-full">
                        {escalation.confidence_score?.toFixed(2)}
                      </span>
                    </div>
                    <p className="text-sm text-text-secondary">{escalation.reason}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* New Project Modal */}
      {showNewProject && (
        <NewProjectModal
          onClose={() => setShowNewProject(false)}
          onSuccess={() => {
            setShowNewProject(false);
            loadData();
          }}
        />
      )}
    </div>
  );
};

export default Dashboard;
